"""B03 real local owner state/authority and scoped ledger gates (DLV-08/09)."""
import copy
from contextlib import closing
from dataclasses import replace
import json
from pathlib import Path
import sqlite3
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from test_audit_execution_wire import fixture,LIMITS,covers,record_ref
from test_audit_execution_journal import scratch,context as journal_context,opened
from crucis_causal.execution import api,codec
from crucis_causal.execution.accounting import resource_total,exposure_totals
from crucis_causal.execution.authority import require_owner_grants
from crucis_causal.execution.owners import LocalOwner,METHODS,native_binding_ref,_native_time,persist_owner_requests
from crucis_causal.execution.journal import resolve_binding,binding_digest
from crucis_causal.execution.model import (ExecutionError,Builder,canonical,contract,digest,identity,index,
    known,not_applicable,number,qualified,reference,scope,unknown)

from audit_fixtures.sc3_runtime.receipt_case import snapshot as retained_snapshot, owner_oracle, triplet

RESOURCES={'s3.fixture_work':{'unit':contract('fixture_unit'),'capacity':number('20')}}

def owner_setup(root,*,capacity='20',max_calls='100',clock=None):
    v,resolver=fixture();binding=resolve_binding(record_ref(v,'operation_binding'),v.package_id,resolver)
    owner=LocalOwner(root,{'s3.fixture_work':{'unit':contract('fixture_unit'),'capacity':number(capacity)}},
        native_operations=(binding.record['payload']['operation'],),clock=clock)
    allocation=identity();cap=owner.control(allocation,max_calls=max_calls)
    with owner._db() as db:
        for r in db.execute('SELECT data FROM views'):resolver.add(codec.parse_snapshot(bytes(r[0]),LIMITS))
    read=api.PinnedReadContext(tuple(resolver._views.values()),api.supplied_read(resolver._views),None,LIMITS)
    return owner,binding,api.RuntimeContext(read,cap),allocation

def packet(binding,ctx,documents):
    from crucis_causal.connections.model import Builder as S1Builder,contract as c1
    from crucis_causal.connections.evidence import capture_bytes
    from crucis_causal.connections.codec import dumps as s1dumps
    b=Builder('Explicit owner request fixture');native=S1Builder('Explicit owner parameter bytes');refs={}
    for label,(selected,value) in documents.items():
        refs[label]=(selected,capture_bytes(native,canonical(value),format_contract=c1('json')))
    source=codec.parse_snapshot(s1dumps(native.package([native.producer])),LIMITS)
    for label,(selected,artifact) in refs.items():
        refs[label]=b.add('typed_payload',{'payload_contract':contract('s3.payload.'+selected),
            'content':{'artifact':qualified(artifact,source.package_id),'selector':not_applicable()},
            'reference_context':{'package_id':b.package_id,'format':contract('account_package')}})
    audience=next(record_ref(v,'audience') for v in ctx.read.views if any(r['record_type']=='s3.audience' for r in v.records))
    root=b.add('projection_view',{'view_role':'audience_projection','audience':audience,'projection_contract':contract('owner_request_fixture'),
        'members':index(refs.values()),'claims':index(),'limits':index()})
    dependencies=(*ctx.read.views,source)
    view=codec.parse_snapshot(codec.dumps(b.package(root,dependencies),LIMITS),LIMITS)
    read=replace(ctx.read,views=(*dependencies,view),access=api.supplied_read(v.package_id for v in (*dependencies,view)))
    return {k:qualified(r,view.package_id) for k,r in refs.items()},replace(ctx,read=read)

def request(owner,binding,method,*,correlation=None,group=None,occurrence=None,params=None,evidence=None):
    correlation=correlation or identity();group=group or identity();occurrence=occurrence or identity()
    values={'correlation':correlation,'request_occurrence':occurrence,'admission_occurrence':group,**(params or {})}
    return api.ExactOwnerRequest(contract(METHODS[method]),owner.owner,correlation,binding,
        tuple({'key':k,'value':known(v)} for k,v in values.items()),evidence or api.PinnedInputs((),binding.inputs.source_views),occurrence,group)

def reserve(owner,binding,ctx,amount='3',*,correlation=None,group=None):
    refs,ctx=packet(binding,ctx,{'amounts':('reservation_amounts',{'entries':[{'resource':contract('fixture_work'),
        'unit':contract('fixture_unit'),'quantity':number(amount),'scope':scope(native_binding_ref(binding)),
        'aggregation':contract('s3.aggregation.replace_then_disjoint_members')}]})})
    revision=owner.inspect(binding,ctx).value.revision['value']
    req=request(owner,binding,'reserve',correlation=correlation,group=group,params={'amounts':refs['amounts'],'expected_revision':revision})
    return req,ctx,owner.reserve(req,ctx)

def receipt_payload(result):
    ref=result.value.receipt;view=next(v for v in result.records.dependencies if v.package_id==ref['package_id'])
    return next(r['payload'] for r in view.records if r['id']==ref['target'])

def validity(owner,binding,until='9999999999999999999',epoch='0'):
    return {'owner':owner.owner,'scope':scope(native_binding_ref(binding)),'epoch':epoch,'valid_from':unknown(),
        'valid_until':known(_native_time(int(until))),'receiver_check':contract('owner_exact_live_grant'),'revocation':contract('owner_persisted_epoch')}

def query_request(owner,binding,ctx,original,*,target=None):
    lost=target or original.request_occurrence
    refs,ctx=packet(binding,ctx,{'key':('owner_request_key',{'request_occurrence':lost}),
        'time':('validity',validity(owner,binding))})
    query={'subject':native_binding_ref(binding),'keys':refs['key'],'time_scope':refs['time'],
        'retention':contract('owner_retained_requests'),'negative_coverage':contract('owner_exact_request_history')}
    refs,ctx=packet(binding,ctx,{'query':('query',query)})
    return request(owner,binding,'reconcile',correlation=original.correlation,group=original.admission_occurrence,
        params={'query':refs['query'],'request_to_reconcile':lost}),ctx

def facts(owner,binding,ctx,*,exposure=False):
    b=Builder('Authored scoped accounting facts, not native charges');refs=[]
    template={'scope':scope(native_binding_ref(binding)),'owner':owner.owner,'resource':contract('fixture_work'),
        'unit':owner.units['s3.fixture_work'],'entry_kind':'bill','quantity':known(number('3')),
        'interval':not_applicable('s3.owner_atomic_subject_interval'),'finality':'interim','revises':[],
        'aggregation':contract('s3.aggregation.replace_then_disjoint_members'),'basis':[]}
    first=b.add('resource_entry',template,basis='reported');refs.append(first)
    second=b.add('resource_entry',{**template,'quantity':known(number('5')),'finality':'final','revises':[first]},basis='reported');refs.append(second)
    from crucis_causal.execution.model import walk
    other_payload=copy.deepcopy(binding.record['payload'])
    for _,ref,_ in walk(other_payload):
        if isinstance(ref,dict) and ref.get('binding')=='internal':ref.update(binding='external',package_id=binding.context['package_id'])
    other=b.add('operation_binding',other_payload,basis='derived',evidence=[native_binding_ref(binding)],procedure=contract('fixture_explicit_relocation'))
    last=b.add('resource_entry',{**template,'scope':scope(other),'quantity':known(number('4')),'finality':'final'},basis='reported');refs.append(last)
    if exposure:
        for facet,value in [('delivered','1'),('policy_consumed','1'),('used',None)]:
            refs.append(b.add('exposure_entry',{'scope':scope(native_binding_ref(binding)),'owner':owner.owner,
                'recipient':owner.owner,'information':index(),'facet':facet,'extent':known(number(value)) if value is not None else unknown(),
                'policy':contract('fixture_exposure_policy'),'basis':[],'revises':[]},basis='reported'))
    root=b.add('projection_view',{'view_role':'audience_projection','audience':owner.audience,'projection_contract':contract('accounting_test_facts'),
        'members':index(refs),'claims':index(),'limits':index()})
    view=codec.parse_snapshot(codec.dumps(b.package(root,ctx.read.views),LIMITS),LIMITS)
    resolver=codec.Resolver((*ctx.read.views,view),limits=LIMITS)
    entries=[]
    for ref in refs:
        r,pid=resolver.record(ref,view.package_id)
        entries.append(api.BoundInput('s3.role.evidence',qualified(ref,pid),r,pid,view.digest))
    return tuple(entries),replace(ctx,read=replace(ctx.read,views=tuple(resolver._views.values()),access=api.supplied_read(resolver._views)))

class OwnerCases(unittest.TestCase):
    @covers('A01')
    def test_A01_partial_and_unresolved_owner_group_never_becomes_live_admission(self):
        with scratch() as root:
            first,binding,ctx,_=owner_setup(root/'one')
            second,other,ctx2,_=owner_setup(root/'two',capacity='0')
            req,ctx,permitted=reserve(first,binding,ctx)
            _,ctx2,held=reserve(second,other,ctx2)
            self.assertEqual(receipt_payload(held)['decision'],'held')
            with self.assertRaisesRegex(ExecutionError,'owner_group_incomplete'):
                require_owner_grants(((first,permitted,ctx),(second,held,ctx2)),binding,binding.record['payload']['operation'])
            unknown_request,ctx2=query_request(second,other,ctx2,req,target=identity())
            unresolved=second.reconcile(unknown_request,ctx2)
            self.assertIsNone(unresolved.value.grant)
            with self.assertRaises(ExecutionError):require_owner_grants(((first,permitted,ctx),(second,unresolved,ctx2)),binding,binding.record['payload']['operation'])
            with closing(sqlite3.connect(first.path)) as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM subjects WHERE status=?',('active',)).fetchone()[0],1)

    @covers('F03','OP17P','OP18P','OP19P')
    def test_F03_lost_renew_settle_release_replies_reconcile_same_request_without_extra_effect(self):
        for method in ['renew','settle','release']:
            with self.subTest(method=method),scratch() as root:
                owner,binding,ctx,_=owner_setup(root)
                reserved,ctx,_=reserve(owner,binding,ctx)
                revision=owner.inspect(binding,ctx).value.revision['value']
                evidence=None
                if method=='renew':
                    refs,ctx=packet(binding,ctx,{'validity':('validity',validity(owner,binding))})
                    params={'expected_revision':revision,'extension':refs['validity']}
                elif method=='settle':
                    facts_,ctx=facts(owner,binding,ctx);evidence=api.PinnedInputs(facts_[:2],ctx.read.views)
                    params={'expected_revision':revision,'aggregation':contract('s3.aggregation.replace_then_disjoint_members')}
                else:params={'expected_revision':revision,'release_rule':contract('owner_release_capacity_only')}
                req=request(owner,binding,method,correlation=reserved.correlation,params=params,evidence=evidence)
                def lost(label):
                    if label=='after_owner_commit':raise OSError('lost response after actual receiver commit')
                before_oracle=owner_oracle(owner)
                dropped=getattr(owner,method)(req,replace(ctx,fault=lost))
                committed_oracle=owner_oracle(owner)
                self.assertEqual(dropped.state,'rejected')
                replay=getattr(owner,method)(req,ctx)
                self.assertEqual(replay.state,'completed',replay.issues)
                again=getattr(owner,method)(req,ctx)
                self.assertEqual(replay.value.receipt,again.value.receipt)
                with closing(sqlite3.connect(owner.path)) as db:
                    self.assertEqual(db.execute('SELECT COUNT(*) FROM requests WHERE id=?',(req.request_occurrence,)).fetchone()[0],1)
                    self.assertEqual(db.execute('SELECT COUNT(*) FROM subjects').fetchone()[0],1)
                triplet('F03',method+'_reply_lost',{'before':before_oracle,'after_lost_reply':committed_oracle,'after_replay':owner_oracle(owner)},
                    {'request_occurrence':req.request_occurrence,'correlation':req.correlation,'admission_occurrence':req.admission_occurrence,
                     'revision_before':revision,'source_pins':[{'package_id':v.package_id,'digest':v.digest} for v in ctx.read.views]},
                    {'receipt':replay.value.receipt,'revision':replay.value.revision,'decision':receipt_payload(replay),
                     'reply_loss':'injected after actual receiver commit; same-process API replay, not process death'})


    @covers('OP16P','OP16H','F03')
    def test_OP16_exact_lost_reserve_reply_reconciles_one_hold_and_unknown_stays_unknown(self):
        with scratch() as root:
            owner,binding,ctx,_=owner_setup(root)
            def lost(label):
                if label=='after_owner_commit':raise OSError('injected lost reply')
            req,normal,first=reserve(owner,binding,replace(ctx,fault=lost))
            self.assertEqual(first.state,'rejected');self.assertEqual(first.issues[0].code,'s3.owner_reply_unconfirmed')
            committed_oracle=owner_oracle(owner)
            normal=replace(normal,fault=None)
            reconcile,normal=query_request(owner,binding,normal,req)
            recovered=owner.reconcile(reconcile,normal)
            self.assertEqual(recovered.state,'completed',recovered.issues);self.assertIsNotNone(recovered.value.grant)
            self.assertEqual(receipt_payload(recovered)['decision'],'permitted')
            with closing(sqlite3.connect(owner.path)) as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM subjects').fetchone()[0],1)
            unknown_query,normal=query_request(owner,binding,normal,req,target=identity())
            missing=owner.reconcile(unknown_query,normal)
            self.assertEqual(missing.state,'completed',missing.issues);self.assertEqual(receipt_payload(missing)['decision'],'unresolved');self.assertIsNone(missing.value.grant)
            triplet('F03','reserve_reply_lost',{'after_lost_reply':committed_oracle,'after_reconcile':owner_oracle(owner)},
                {'request_occurrence':req.request_occurrence,'correlation':req.correlation,'admission_occurrence':req.admission_occurrence,
                 'source_pins':[{'package_id':v.package_id,'digest':v.digest} for v in normal.read.views]},
                {'receipt':recovered.value.receipt,'decision':receipt_payload(recovered),'unknown_query_decision':receipt_payload(missing),
                 'reply_loss':'injected after actual receiver commit; reconciliation is not a new reservation'})


    @covers('OP18P','OP18H','A01')
    def test_OP18_settlement_replaces_interim_bill_and_preserves_missing_evidence(self):
        with scratch() as root:
            owner,binding,ctx,_=owner_setup(root)
            reserved,ctx,out=reserve(owner,binding,ctx)
            evidence,ctx=facts(owner,binding,ctx)
            revision=owner.inspect(binding,ctx).value.revision['value']
            req=request(owner,binding,'settle',correlation=reserved.correlation,params={'expected_revision':revision,
                'aggregation':contract('s3.aggregation.replace_then_disjoint_members')},
                evidence=api.PinnedInputs(evidence[:2],ctx.read.views))
            settled=owner.settle(req,ctx)
            self.assertEqual(settled.state,'completed',settled.issues)
            self.assertEqual(receipt_payload(settled)['decision'],'permitted')
            with closing(sqlite3.connect(owner.path)) as db:self.assertEqual(db.execute('SELECT quantity FROM charges').fetchone()[0],'5')
            _,ctx,another=reserve(owner,binding,ctx,'3')
            missing=request(owner,binding,'settle',correlation=identity(),params={'expected_revision':another.value.revision,
                'aggregation':contract('s3.aggregation.replace_then_disjoint_members')})
            self.assertEqual(owner.settle(missing,ctx).state,'rejected')

    @covers('A01')
    def test_A01_replacement_5_plus_disjoint_4_is_9_unknowns_and_facets_separate(self):
        with scratch() as root:
            owner,binding,ctx,_=owner_setup(root)
            evidence,ctx=facts(owner,binding,ctx,exposure=True)
            total=resource_total(evidence[:3]);self.assertEqual(total.quantity,known(number('9')))
            self.assertFalse(total.issues)
            changed=copy.deepcopy(evidence[2].record);changed['payload']['quantity']=unknown()
            self.assertEqual(resource_total((*evidence[:2],replace(evidence[2],record=changed))).quantity['state'],'unresolved')
            cycles=[]
            for e in evidence[:2]:cycles.append(copy.deepcopy(e.record))
            cycles[0]['payload']['revises']=[evidence[1].reference]
            self.assertEqual(resource_total((replace(evidence[0],record=cycles[0]),replace(evidence[1],record=cycles[1]),evidence[2])).quantity['state'],'unresolved')
            totals=exposure_totals(evidence[3:]);self.assertEqual(len(totals),3)
            self.assertEqual(sorted(t.quantity['state'] for t in totals.values()),['known','known','unresolved'])
            cross=copy.deepcopy(evidence[-1].record);cross['payload']['revises']=[evidence[-2].reference]
            self.assertTrue(any(t.issues for t in exposure_totals((evidence[-2],replace(evidence[-1],record=cross))).values()))
            original=evidence[3];other=copy.deepcopy(original.record);other['id']=identity()
            duplicate=replace(original,record=other,reference=reference(other['id'],'exposure_entry',original.source_package))
            self.assertTrue(next(iter(exposure_totals((original,duplicate)).values())).issues)
            cyc1=copy.deepcopy(original.record);cyc2=copy.deepcopy(other)
            cyc1['payload']['revises']=[duplicate.reference];cyc2['payload']['revises']=[original.reference]
            self.assertEqual(next(iter(exposure_totals((replace(original,record=cyc1),replace(duplicate,record=cyc2))).values())).issues[0].code,'s3.exposure_revision_cycle')

    @covers('A01','OP16H','OP18H')
    def test_exact_replay_binds_evidence_and_unknown_query_retains_capacity(self):
        with scratch() as root:
            owner,binding,ctx,_=owner_setup(root,capacity='5')
            reserved,ctx,_=reserve(owner,binding,ctx,'3')
            query,ctx=query_request(owner,binding,ctx,reserved,target=identity())
            self.assertEqual(receipt_payload(owner.reconcile(query,ctx))['decision'],'unresolved')
            _,ctx,blocked=reserve(owner,binding,ctx,'3')
            self.assertEqual(receipt_payload(blocked)['decision'],'held')
            evidence,ctx=facts(owner,binding,ctx)
            rev=owner.inspect(binding,ctx).value.revision['value']
            req=request(owner,binding,'settle',correlation=reserved.correlation,
                params={'expected_revision':rev,'aggregation':contract('s3.aggregation.replace_then_disjoint_members')},
                evidence=api.PinnedInputs(evidence[:2],ctx.read.views))
            self.assertEqual(owner.settle(req,ctx).state,'completed')
            changed=replace(req,evidence=api.PinnedInputs(evidence[:1],ctx.read.views))
            self.assertEqual(owner.settle(changed,ctx).issues[0].code,'s3.owner_request_identity_conflict')

    @covers('F02')
    def test_F02_interruption_before_receiver_keeps_original_request_key_and_no_hold(self):
        with scratch() as root:
            owner,binding,ctx,_=owner_setup(root/'owner')
            refs,ctx=packet(binding,ctx,{'amounts':('reservation_amounts',{'entries':[{'resource':contract('fixture_work'),'unit':contract('fixture_unit'),
                'quantity':number('3'),'scope':scope(native_binding_ref(binding)),'aggregation':contract('s3.aggregation.replace_then_disjoint_members')}]})})
            req=request(owner,binding,'reserve',params={'amounts':refs['amounts'],'expected_revision':'0'})
            journal,jctx,account,head=opened(root/'journal')
            durable=persist_owner_requests(journal,head,(req,),jctx,ctx.read)
            self.assertEqual(durable.state,'completed',durable.issues)
            # Interruption is before owner entry; a fresh journal contains R/H/G.
            from crucis_causal.execution.journal import Journal
            fresh=Journal(root/'journal');reopened=fresh.head(account,journal_context(fresh,account)).value.snapshot
            self.assertTrue(any(r['id']==req.request_occurrence for r in reopened.records))
            self.assertTrue(any(r['id']==req.admission_occurrence for r in reopened.records))
            with closing(sqlite3.connect(owner.path)) as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM subjects').fetchone()[0],0)
            before_oracle=owner_oracle(owner)
            retried=owner.reserve(req,ctx)
            self.assertEqual(retried.state,'completed',retried.issues)
            self.assertEqual(receipt_payload(retried)['request_occurrence'],req.request_occurrence)
            with closing(sqlite3.connect(owner.path)) as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM subjects').fetchone()[0],1)
            triplet('F02','intent_before_receiver',{'before_entry':before_oracle,'after_original_request':owner_oracle(owner)},
                {'retained_intent':retained_snapshot(reopened),'request_occurrence':req.request_occurrence,
                 'admission_occurrence':req.admission_occurrence,'interruption':'explicit before owner call; journal object reopened, no process death'},
                {'receipt':retried.value.receipt,'decision':receipt_payload(retried),'same_request_occurrence':req.request_occurrence})


    @covers('OP15P','OP15H','A01')
    def test_OP15_actual_hold_dedup_changed_request_and_capacity(self):
        with scratch() as root:
            owner,binding,ctx,allocation=owner_setup(root,capacity='5')
            req,ctx,first=reserve(owner,binding,ctx,'3')
            self.assertEqual(first.state,'completed',first.issues);self.assertEqual(receipt_payload(first)['decision'],'permitted')
            self.assertIsNotNone(first.value.grant)
            repeat=owner.reserve(req,ctx);self.assertEqual(repeat.value.receipt,first.value.receipt)
            with closing(sqlite3.connect(owner.path)) as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM subjects').fetchone()[0],1)
                self.assertEqual(db.execute('SELECT COUNT(*) FROM requests').fetchone()[0],1)
                self.assertGreater(db.execute('SELECT COUNT(*) FROM calls').fetchone()[0],1)
            _,_,held=reserve(owner,binding,ctx,'3')
            self.assertEqual(receipt_payload(held)['decision'],'held');self.assertIsNone(held.value.grant)
            changed=replace(req,admission_occurrence=identity())
            self.assertEqual(owner.reserve(changed,ctx).state,'rejected')
            self.assertTrue(any(r['payload'].get('entry_kind')=='control_overhead' for v in repeat.records.dependencies for r in v.records))

    @covers('OP20P','OP20H','A01')
    def test_OP20_authorize_live_binding_forgery_expiry_and_epoch(self):
        with scratch() as root:
            ticks=[0];owner,binding,ctx,_=owner_setup(root,clock=lambda:ticks[0])
            reserve_req,ctx,held=reserve(owner,binding,ctx)
            self.assertEqual(held.state,'completed',held.issues)
            refs,ctx=packet(binding,ctx,{'validity':('validity',validity(owner,binding,'100'))})
            revision=owner.inspect(binding,ctx).value.revision['value']
            req=request(owner,binding,'authorize',correlation=reserve_req.correlation,group=reserve_req.admission_occurrence,
                params={'effects':[binding.record['payload']['operation']],'validity':refs['validity']})
            out=owner.authorize(req,ctx);self.assertEqual(out.state,'completed',out.issues);self.assertIsNotNone(out.value.grant)
            self.assertEqual(owner.check(out.value.grant,binding,binding.record['payload']['operation'],ctx).state,'completed')
            fake=object.__new__(api.OpaqueGrant)
            self.assertEqual(owner.check(fake,binding,binding.record['payload']['operation'],ctx).state,'rejected')
            ticks[0]=101
            self.assertEqual(owner.check(out.value.grant,binding,binding.record['payload']['operation'],ctx).state,'rejected')
            denied=owner.authorize(replace(req,request_occurrence=identity()),ctx)
            self.assertEqual(denied.state,'rejected') # duplicated identity fields conflict, never refreshed implicitly
            refs,ctx=packet(binding,ctx,{'expired':('validity',validity(owner,binding,'1'))})
            negative=request(owner,binding,'authorize',correlation=reserve_req.correlation,
                params={'effects':[binding.record['payload']['operation']],'validity':refs['expired']})
            denied=owner.authorize(negative,ctx);self.assertEqual(receipt_payload(denied)['decision'],'denied');self.assertIsNone(denied.value.grant)
            self.assertIsNone(owner.authorize(negative,ctx).value.grant)
            ticks[0]=0;owner.rotate_epoch(ctx)
            self.assertEqual(owner.check(held.value.grant,binding,binding.record['payload']['operation'],ctx).state,'rejected')

    @covers('OP17P','OP17H','OP19P','OP19H')
    def test_OP17_renew_and_OP19_release_do_not_reset_budget_or_native_history(self):
        with scratch() as root:
            owner,binding,ctx,_=owner_setup(root)
            initial,ctx,out=reserve(owner,binding,ctx)
            refs,ctx=packet(binding,ctx,{'extension':('validity',validity(owner,binding))})
            revision=owner.inspect(binding,ctx).value.revision['value']
            renew=request(owner,binding,'renew',correlation=initial.correlation,group=initial.admission_occurrence,
                params={'expected_revision':revision,'extension':refs['extension']})
            result=owner.renew(renew,ctx);self.assertEqual(result.state,'completed',result.issues)
            self.assertEqual(owner.renew(renew,ctx).value.receipt,result.value.receipt)
            wrong=request(owner,binding,'renew',correlation=initial.correlation,params={'expected_revision':'0','extension':refs['extension']})
            self.assertEqual(owner.renew(wrong,ctx).state,'rejected')
            release=request(owner,binding,'release',correlation=initial.correlation,params={'expected_revision':result.value.revision,'release_rule':contract('owner_release_capacity_only')})
            released=owner.release(release,ctx);self.assertEqual(released.state,'completed',released.issues)
            self.assertEqual(owner.release(release,ctx).value.receipt,released.value.receipt)
            self.assertEqual(owner.check(out.value.grant,binding,binding.record['payload']['operation'],ctx).state,'rejected')
            bad=request(owner,binding,'release',correlation=initial.correlation,params={'expected_revision':released.value.revision,'release_rule':contract('pretend_native_stopped')})
            self.assertEqual(owner.release(bad,ctx).state,'rejected')

    @covers('A01')
    def test_A01_control_budget_persists_across_fresh_owner_context(self):
        with scratch() as root:
            owner,binding,ctx,allocation=owner_setup(root,max_calls='2')
            self.assertEqual(owner.inspect(binding,ctx).state,'completed')
            self.assertEqual(owner.inspect(binding,ctx).state,'completed')
            self.assertEqual(owner.inspect(binding,ctx).issues[0].code,'s3.owner_control_allowance_exhausted')
            fresh=LocalOwner(root,RESOURCES,native_operations=(binding.record['payload']['operation'],))
            cap=fresh.control(allocation,max_calls='2')
            self.assertEqual(fresh.inspect(binding,replace(ctx,control=cap)).issues[0].code,'s3.owner_control_allowance_exhausted')
            self.assertEqual(fresh.remaining_control(allocation),'0')

if __name__=='__main__':unittest.main()
