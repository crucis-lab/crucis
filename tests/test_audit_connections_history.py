from crucis_causal.core.paths import ROOT as DATA_ROOT
"""Episode/transport/state/replay acceptance cases (DLV-08, DLV-09)."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from crucis_causal.connections import Builder, WireError, known, number
from crucis_causal.connections.evidence import capture_bytes
from crucis_causal.connections.history import (RecordedReplay, ReplayEntry, ReplayExhausted,
    accounting_total, native_action_count)
from crucis_causal.connections.model import contract, index, not_applicable, scope, source, unknown_ref, unresolved
from crucis_causal.connections.semantics import validate


def status(report, ref, check):
    return next(c.result for c in report.checks if c.subject == ref['target'] and c.contract == 's1.'+check)


def request(b,route='s1.fixture'):
    policy = b.add('policy', {'policy_contract':contract('fixture_policy'), 'parameters':[], 'scope':scope(),
        'authority':known(b.producer), 'source':source()})
    r = b.add('request', {'operation':contract('fixture_discovery'), 'task_scope':scope(), 'deliverables':[],
        'completion':contract('fixture_completion'), 'completion_parameters':[], 'presentation_policy':policy,
        'resource_policy':known(policy), 'recovery_policy':known(policy), 'route':route, 'source':source()})
    return r, policy


def attempt(b, req, state=None):
    return b.add('attempt', {'request':req, 'native_identity':unresolved(), 'initial_state':known(state) if state else unresolved(),
        'binding':unresolved(), 'source':source()})


def event(b, subject, name='fixture_event', predecessors=(), seq=None, evidence=()):
    raw = capture_bytes(b, b'fixture event')
    return b.add('event', {'subject':subject, 'actor':b.producer, 'event_contract':contract(name), 'content':raw,
        'native_time':unresolved(), 'local_sequence':known({'stream':'fixture', 'position':str(seq), 'producer':b.producer}) if seq is not None else unresolved(),
        'predecessors':list(predecessors), 'correlation':unresolved(), 'source':source('observed', evidence or [raw], b.producer)})


class HistoryCases(unittest.TestCase):
    def test_event_partial_order_has_concurrency_and_rejects_cycles(self):
        b=Builder();r,_=request(b);a=event(b,r,seq=0);z=event(b,r,seq=1);concurrent=event(b,r)
        p=b.package([a,z,concurrent]);self.assertEqual(status(validate(p),a,'event_precedence'),'pass')
        next(x for x in p['records'] if x['id']==a['target'])['payload']['predecessors']=[z]
        self.assertEqual(status(validate(p),a,'event_precedence'),'fail')
        self.assertEqual(b.get(concurrent)['payload']['local_sequence']['state'],'unresolved')

    def test_checkpoint_restart_is_new_attempt_and_unknown_rng_blocks_exact(self):
        b=Builder();r,policy=request(b);blob=capture_bytes(b,b'checkpoint')
        state=b.output('model_reference', {'model_role':'s1.checkpoint','artifacts':[{'artifact':blob,'selector':known({'selector_type':'byte_range','start':'0','end_exclusive':'10'})}], 'input_domains':[], 'output_domains':[],
            'dependencies':[], 'associated':[], 'reader':unresolved(), 'state_coverage':index(extent='partial_for_scope')})
        a=attempt(b,r);z=attempt(b,r,state)
        load_payload={'attempt':z, 'snapshot':state, 'requested_components':['s1.optimizer','s1.rng'],
            'observed_components':[{'component':'s1.optimizer','identity':known('v1'),'availability':known(blob),'loaded':known(True),'evidence':[blob]},
                {'component':'s1.rng','identity':unresolved(),'availability':unresolved(),'loaded':unresolved(),'evidence':[]}],
            'configuration_before':[], 'configuration_after':[], 'continuity':'partial','scope':scope(z),'source':source('observed',[blob])}
        load=b.add('state_load',load_payload)
        recovery=b.add('recovery', {'successor':z,'predecessor':a,'recovery_kind':'checkpoint_continuation',
            'request_relation':'same_request','state':known(state),'load':known(load),'reason':known('s1.interrupted'),'policy':policy,'source':source()})
        p=b.package([recovery]);report=validate(p);self.assertTrue(report.ok,report.to_json())
        self.assertEqual(status(report,recovery,'checkpoint_binding'),'pass');self.assertNotEqual(a,z)
        next(x for x in p['records'] if x['id']==load['target'])['payload']['continuity']='exact_within_scope'
        self.assertEqual(status(validate(p),load,'state_continuity'),'fail')

    def test_recovery_self_cycle_and_wrong_request_relation_fail(self):
        b=Builder();r,policy=request(b);a=attempt(b,r)
        rec=b.add('recovery',{'successor':a,'predecessor':a,'recovery_kind':'retry','request_relation':'new_request',
            'state':unresolved(),'load':unresolved(),'reason':unresolved(),'policy':policy,'source':source()})
        report=validate(b.package([rec]));self.assertEqual(status(report,rec,'recovery_identity'),'fail')
        self.assertEqual(status(report,rec,'recovery_ancestry'),'fail')

    def test_cancellation_acknowledgment_is_not_stop(self):
        b=Builder();r,policy=request(b);a=attempt(b,r);asked=event(b,a,'cancel_requested');ack=event(b,a,'cancel_acknowledged')
        cancel=b.add('cancellation',{'subject':a,'requester':b.producer,'policy':policy,'requested':asked,
            'acknowledgment':known(ack),'observed_stop':known(ack),'source':source()})
        self.assertEqual(status(validate(b.package([cancel])),cancel,'cancellation_stop'),'unknown')
        stopped=event(b,a,'native_stop');p=b.package([cancel]);next(x for x in p['records'] if x['id']==cancel['target'])['payload']['observed_stop']=known(stopped)
        self.assertEqual(status(validate(p),cancel,'cancellation_stop'),'pass')

    def test_duplicate_transport_needs_supported_receipt_evidence(self):
        b=Builder();raw=capture_bytes(b,b'receipt=1');message=unknown_ref('action_request')
        payload={'message':message,'sender':b.producer,'recipient':b.producer,'transport':contract('ordinary_transport'),
            'native_receipt':known({'authority':'fixture','namespace':'actions','native_id':'1','source':source('observed',[raw])}),
            'outcome':'acknowledged','source':source('observed',[raw])}
        a=b.add('transmission',payload);z=b.add('transmission',payload)
        self.assertEqual(native_action_count(b.package([a,z]),[a,z])['state'],'unresolved')
        payload['transport']=contract('idempotent_receipt');c=b.add('transmission',payload);d=b.add('transmission',payload)
        self.assertEqual(native_action_count(b.package([c,d]),[c,d])['value']['text'],'1')

    def test_parent_completion_not_inferred_from_membership(self):
        b=Builder();r,_=request(b);a=attempt(b,r)
        s=b.add('session',{'request':r,'native_identity':unresolved(),'parent':not_applicable('no_parent'),
            'membership':index([a]),'completion_rule':contract('fixture_completion'),'source':source()})
        self.assertEqual(status(validate(b.package([s])),s,'session_completion'),'unknown')

    def test_replay_duplicate_content_has_ordered_occurrence_and_no_fallback(self):
        replay=RecordedReplay([ReplayEntry('first',b'Q',{'endpoint':'x'},b'A'),ReplayEntry('second',b'Q',{'endpoint':'x'},b'B')])
        with self.assertRaises(ReplayExhausted):replay.respond(b'Q',{'endpoint':'wrong'},'first')
        self.assertEqual(replay.position,0)
        self.assertEqual(replay.respond(b'Q',{'endpoint':'x'},'first'),b'A')
        with self.assertRaises(ReplayExhausted):replay.respond(b'Q',{'endpoint':'x'},'first')
        self.assertEqual(replay.respond(b'Q',{'endpoint':'x'},'second'),b'B')
        with self.assertRaises(ReplayExhausted):replay.respond(b'Q',{'endpoint':'x'},'third')
        self.assertEqual(RecordedReplay([],exhaustion='return_unresolved').respond(b'',{},'none')['state'],'unresolved')

    def test_replay_cannot_reuse_source_occurrence(self):
        with self.assertRaises(WireError):RecordedReplay([ReplayEntry('x',b'Q',{},b'A'),ReplayEntry('x',b'Q',{},b'A')])

    def test_accounting_sums_across_restart_but_rejects_inclusive_overlap(self):
        b=Builder();r,_=request(b);a=attempt(b,r);z=attempt(b,r);rows=[]
        for subject,val in ((a,'0.1'),(z,'0.2')):
            q=b.output('quantity',{'quantity_kind':'s1.reported_cost','subject':subject,'value':known(number(val)),
                'units':known({'name':'USD','convention':contract('usd')}),'conditioning':[], 'basis':known(subject),
                'procedure':b.producer,'associated_rule':known(contract('provider_reported_cost'))})
            rows.append(b.add('accounting',{'scope':scope(r),'quantities':[q],'members':[subject],
                'aggregation':contract('disjoint_sum'),'coverage':'disjoint_members','revised':[],'source':source()}))
        p=b.package(rows);self.assertEqual(accounting_total(p,rows)['value']['text'],'0.3')
        with self.assertRaises(WireError):accounting_total(p,[rows[0],rows[0]])
        next(x for x in p['records'] if x['id']==rows[1]['target'])['payload']['coverage']='inclusive_total'
        with self.assertRaises(WireError):accounting_total(p,rows)

    def test_native_fixture_reconnect_checkpoint_callback_and_cancel(self):
        def start():
            p=subprocess.Popen([sys.executable,'-B',str(ROOT/'tests/audit_fixtures/s1_native_fixture.py')],
                stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8')
            self.assertEqual(json.loads(p.stdout.readline())['event'],'started');return p
        def send(p,value):
            p.stdin.write(json.dumps(value)+'\n');p.stdin.flush();return json.loads(p.stdout.readline())
        def close(p):
            if p.poll() is None:p.terminate()
            p.wait(timeout=5);p.stdin.close();p.stdout.close();p.stderr.close()
        p=start()
        try:
            pid=p.pid;first=send(p,{'op':'submit','key':'same'});second=send(p,{'op':'submit','key':'same'})
            self.assertEqual(first,second);self.assertEqual(send(p,{'op':'observe'})['state']['counter'],1)
            self.assertEqual(p.pid,pid) # observer reconnect is a new observation of the same process
            self.assertEqual(send(p,{'op':'callback','question':'fixture?'})['event'],'action_requested')
            send(p,{'op':'respond','response':'observed answer'})
            checkpoint=send(p,{'op':'checkpoint'})['state']
            self.assertFalse(send(p,{'op':'cancel'})['stopped'])
        finally:close(p)
        restarted=start()
        try:
            self.assertEqual(send(restarted,{'op':'restore','state':checkpoint})['event'],'loaded')
            self.assertEqual(send(restarted,{'op':'observe'})['state'],checkpoint)
            final=send(restarted,{'op':'finish'});self.assertEqual(final['callback'],'observed answer')
            restarted.wait(timeout=5);self.assertEqual(restarted.returncode,0)
        finally:close(restarted)

    @unittest.skipUnless((DATA_ROOT / 'runs').is_dir(),'recorded sources absent')
    def test_existing_causal_copilot_stage_reader_is_additive(self):
        from crucis_causal.core import adapter,battery
        from crucis_causal.connections.legacy import import_record,echo,encode
        ad=adapter.get('causal_copilot');bt=battery.get('q1s2');item=bt.items[0]
        rec=ad.recorded(item,'real');imported=import_record(rec,n=item.n)
        self.assertTrue(rec.stages,'the selected recorded Causal-Copilot case must actually exercise stages')
        self.assertTrue(validate(imported['package']).ok)
        self.assertEqual(encode(echo(imported['package'],imported['legacy_snapshot'])),encode(rec))
        if rec.stages:
            from crucis_causal.trace.stages import lineage
            self.assertEqual(lineage(echo(imported['package'],imported['legacy_snapshot']).stages),lineage(rec.stages))


if __name__=='__main__':unittest.main()
