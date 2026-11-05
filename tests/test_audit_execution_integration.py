"""B12 fresh scoped paths and explicit cold bootstrap (DLV-08/09/10)."""
import base64
from dataclasses import replace
from decimal import Decimal
import inspect
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests/audit_fixtures/sc3_runtime'))
from test_audit_execution_wire import covers,fixture,fixture_views
from test_audit_execution_journal import scratch
from test_audit_execution_dispatch import native_request
import dispatch_case as case
import integration_case as integration
import interaction_case as interaction
import recovery_case as recovery
from crucis_causal.execution import api,codec
from crucis_causal.execution.core import Core,install_import_reader
from crucis_causal.execution.model import (Builder,ExecutionError,canonical,contract,digest,identity,index,known,
    not_applicable,number,qualified,reference,scope,unknown,unknown_ref)


def cold(env,kind,**extra):
    value=integration.cold_packet(env,kind,**extra)
    path=env.root/(identity()+'.cold.json');path.write_bytes(canonical(value))
    bootstrap={k:value[k] for k in ('kind','root','account','allocation')}
    if kind!='local':bootstrap.update(address=env.client.address,token=env.client._token,namespace=env.client.namespace,epoch=env.client.epoch)
    result=subprocess.run([sys.executable,'-B',str(ROOT/'tests/audit_fixtures/sc3_runtime/integration_worker.py'),str(path)],
        input=json.dumps(bootstrap)+'\n',capture_output=True,text=True,timeout=180,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0)
    if result.returncode:raise AssertionError('Cold fixture failed: '+result.stderr)
    return json.loads(result.stdout)


def outcome(name,env,value):
    import os
    destination=os.environ.get('CRUCIS_S3_CASE_RECEIPTS')
    if not destination:return
    head=env.journal.head(env.account,env.jctx).value
    path=Path(destination)/'profiles';path.mkdir(parents=True,exist_ok=True)
    (path/(name+'.json')).write_bytes(canonical({'profile':name,'scope':'controlled synthetic mechanisms, not real scientific/backend qualification',
        'view':head.snapshot.package_id,'digest':head.snapshot.digest,'revision':head.revision,'outcome':value}))


class IntegrationCases(unittest.TestCase):
    def test_methodology_maps_actual_sources_and_all_contract_dimensions_without_upgrading_claims(self):
        import hashlib
        index=json.loads((ROOT/'crucis_causal/docs/subsystem3-methodology-index-2026-11-03.json').read_bytes())
        self.assertEqual((len(index['record_kinds']),len(index['operations']),len(index['methods']),len(index['support_axes'])),(38,31,48,8))
        for row in index['methods']:
            source=ROOT/row['source'];self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),row['sha256'],row['port'])
            self.assertIn('receipt',row['validation'])
            self.assertTrue(row['case_ids']);self.assertTrue(row['test_sources'])
            self.assertIn(row['primary_bundle'],row['receipt'])
            source_path,pointer=row['accepted_rule'].split('#/',1)
            selected=row['accepted_rule_excerpt']
            self.assertEqual(selected['method'],row['port'])
            self.assertEqual(selected['case_ids'],row['case_ids'])
            # Source distributions retain the technical excerpt and its source
            # pin, while excluding the full development planning documents.
            if (ROOT/source_path).is_file():
                raw=(ROOT/source_path).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),row['accepted_source_sha256'])
                original=json.loads(raw)
                for part in pointer.split('/'):
                    original=original[int(part)] if isinstance(original,list) else original[part]
                self.assertEqual(original,selected)
            for linked in row['test_sources']:
                self.assertTrue((ROOT/linked['source']).is_file())
        self.assertEqual(len({row['port'] for row in index['methods']}),48)
        for axis in index['support_axes']:
            self.assertTrue(axis['case_ids']);self.assertTrue(axis['test_sources']);self.assertTrue(axis['claim_limit'])
        self.assertIn('unestablished',next(p['scientific_scope'] for p in index['profiles'] if p['id']=='E03'))

    @covers('E01')
    def test_local_function_native_graph_mapping_meter_and_cold_history(self):
        with scratch() as root:
            receiver=integration.LocalReceiver(root/'native');env=integration.LocalEnvironment(root/'coordinator',receiver)
            request=env.launch(mode='local');out=env.run(request);self.assertEqual(out.state,'completed',out.issues)
            observed,decoded=integration.decode_graph(env,out)
            expected=json.loads((case.FIX/'oracles.json').read_bytes())['local']
            meter=receiver.oracle();self.assertEqual(str(len(meter['calls'])),expected['jobs']);self.assertEqual(meter['charge'],expected['charge']);self.assertEqual(meter['cap'],expected['cap'])
            self.assertEqual(observed['order'],expected['native_order']);self.assertEqual(observed['canonical_order'],expected['canonical_order']);self.assertEqual(observed['mapping'],expected['mapping'])
            outputs=[r for v in decoded.records.dependencies for r in v.records if r['record_type']=='s1.output' and r['id'] in (observed['native']['target'],observed['derived']['target'])]
            self.assertEqual(len(outputs),2);self.assertNotEqual(observed['native'],observed['derived'])
            self.assertTrue(all(r['payload']['body']['omission']['within_coverage']=='unreported' for r in outputs))
            current=env.journal.head(env.account,env.jctx).value
            written=env.journal.append(env.account,current.revision,identity(),api.CommitDelta((),(),decoded.records.dependencies),replace(env.jctx,read=env.context.read))
            self.assertEqual(written.state,'completed',written.issues);env.include(*written.records.dependencies,written.value.head.snapshot)
            recovered=cold(env,'local');self.assertEqual(recovered['state'],'completed');self.assertFalse(recovered['native_dispatch'])
            self.assertEqual(receiver.oracle()['charge'],'0.7')
            duplicate=env.run(env.launch(mode='local'));self.assertEqual(duplicate.state,'rejected');self.assertEqual(duplicate.issues[0].code,'s3.attempt_already_has_initiating_command')
            self.assertEqual(len(receiver.oracle()['calls']),1)
            outcome('E01',env,{'jobs':'1','native_order':observed['order'],'canonical_order':observed['canonical_order'],'mapping':observed['mapping'],'charge':meter['charge'],'cap':meter['cap'],'cold_process':recovered})

    @covers('E02')
    def test_remote_lost_ack_same_owner_capture_three_events_two_and_cold_ack(self):
        with scratch() as root,case.service(root/'provider') as (client,_):
            env=integration.RemoteEnvironment(root/'coordinator',client)
            plan=env.plan(env.launch(drop_reply=True));self.assertEqual(plan.state,'completed',plan.issues)
            admitted=env.admit(plan.value);self.assertEqual(admitted.state,'completed',admitted.issues)
            d=identity();lost=env.issue(admitted.value,transmission=d);self.assertEqual(lost.state,'partial',lost.issues)
            found=env.run(env.lookup(plan.value.command));self.assertEqual(found.state,'completed',found.issues)
            native=client.call('query',command=plan.value.command['target'])['matches'][0]
            subject=found.value.result.subjects['members'][0]
            env.configure(native,native_subject=subject)
            observed=env.run(env.observe());self.assertEqual(observed.state,'completed',observed.issues)
            capture=env.capture();self.assertEqual(len(capture.artifacts),3)
            from test_audit_execution_collection import native_events
            events={p['native_event'] for p in native_events(env)}
            self.assertEqual(len(events),2)
            old_budget=env.owner.remaining_control(env.allocation);recovered=cold(env,'remote',capture=capture.occurrence)
            self.assertEqual(recovered['state'],'completed');self.assertEqual(recovered['ack']['position'],'3')
            self.assertLess(int(env.owner.remaining_control(env.allocation)),int(old_budget))
            jobs=client.call('oracle')['jobs'];self.assertEqual(len(jobs),1);self.assertEqual(jobs[0]['charge'],'4')
            self.assertEqual(env.owner.resources['s3.fixture_work']['capacity']['text'],'10')
            self.assertFalse(client.call('query',command=plan.value.command['target'])['no_late_acceptance'])
            outcome('E02',env,{'jobs':'1','captures':'3','distinct_events':'2','charge':'4','cap':'10','cold_process':recovered,'single_owner_identity':env.owner.owner})

    @covers('E03')
    def test_unknown_origin_interactive_two_questions_one_delivery_cold_lookup(self):
        with scratch() as root,case.service(root/'provider') as (client,_):
            client.call('launch',**native_request()|{'mode':'interactive'})
            job=client.call('oracle')['jobs'][0]['id'];env=interaction.Environment(root/'coordinator',client,job)
            self.assertEqual(env.run(env.information('Q1')).state,'completed')
            self.assertEqual(env.run(env.compute('Q1')).state,'completed')
            env.prepare_decisions();selected=env.select();self.assertEqual(selected.state,'completed',selected.issues)
            q2=env.select(('Q2',));self.assertEqual(q2.state,'partial');self.assertEqual(q2.value.selected['members'],[])
            chosen=env.freeze_choice(selected);self.assertEqual(chosen.state,'completed',chosen.issues)
            sent=env.run(env.deliver(chosen.value));self.assertEqual(sent.state,'completed',sent.issues)
            before=client.call('interaction_oracle');self.assertEqual(before['deliveries'],'1');self.assertEqual(before['consumed'],'1');self.assertEqual(before['remaining'],'1')
            recovered=cold(env,'interactive',command=sent.value.command);self.assertEqual(recovered['state'],'completed')
            after=recovered['oracle'];self.assertEqual(after['deliveries'],'1');self.assertEqual(after['computations'],'1');self.assertEqual(after['native_termination']['state'],'unresolved')
            self.assertFalse(any(r['record_type'] in ('s1.request','s1.attempt','s2.trial','s2.run_binding') for v in env.context.read.views for r in v.records))
            outcome('E03',env,{'same_text_occurrences':'2','q1_deliveries':'1','q2_missing_source_choices':'0','q2_missing_source_deliveries':'0',
                'policy_consumed':'1','policy_remaining':'1','native_termination':'unresolved','original_scientific_membership':'unestablished','cold_process':recovered})

    @covers('E04')
    def test_checkpoint_R2_both_sources_partial_state_and_unchanged_original_NA(self):
        from crucis_causal.execution.scientific import match_run,require_recovery_intent
        for source_type in ('captured_payload','native_reference'):
            with self.subTest(source_type=source_type),scratch() as root,case.service(root/'provider',program=recovery.SERVICE) as (client,_):
                env=recovery.Environment(root/'coordinator',client,source_type=source_type)
                stop=env.run(env.stop_request());self.assertEqual(stop.state,'completed',stop.issues)
                self.assertFalse(env.observe_stop()['observed_stopped']);self.assertEqual(env.plan(env.restart_request()).state,'rejected')
                client.call('finish_stop',job=env.predecessor_job);env.observe_stop()
                started=env.run(env.restart_request());self.assertEqual(started.state,'completed',started.issues)
                loaded=env.run(env.restore_request());self.assertEqual(loaded.state,'completed',loaded.issues)
                components=next(r['payload']['components'] for r in loaded.records.records if r['record_type']=='s3.recovery')
                self.assertEqual({c['component']['name']:c['loaded']['state'] for c in components},
                    {'s3.fixture.model':'known','s3.fixture.optimizer':'known','s3.fixture.rng':'unresolved','s3.fixture.history':'unresolved'})
                native=client.call('recovery_oracle');total=sum(Decimal(row['charge']) for row in native['jobs'])
                self.assertEqual(total,Decimal('9'));self.assertEqual(len(native['jobs']),2);self.assertEqual(env.owner.resources['s3.fixture_work']['capacity']['text'],'20')
                reopened=cold(env,'local',profile='checkpoint_evidence')
                self.assertEqual(reopened['state'],'completed');self.assertFalse(reopened['native_dispatch']);self.assertEqual(len(reopened['state_restoration_receipts']),1)
                self.assertEqual(len(client.call('recovery_oracle')['jobs']),2)
                outcome('E04-'+source_type,env,{'source':source_type,'scientific_trials':'1','attempts':'2','total':str(total),'cap':'20','unknown':['rng','history'],'cold_evidence_process':reopened,
                    'interrupted_live_recovery_cases':['F12','F13']})
        # The old positive-looking native archive still has NA recovery. The
        # separate R2 identity does not rewrite or adopt that old request.
        row=next(r for r in json.loads((case.FIX/'manifest.json').read_bytes())['bindings'] if r['path']=='checkpoint')
        views,roles=case.scientific_inputs('checkpoint');resolver=codec.Resolver(views,limits=case.L)
        receipt=next(reference(r['id'],r['record_type'],v.package_id) for v in views for r in v.records if r['record_type']=='s2.request_binding_receipt' and r['payload']['request']['target']==row['request']['target'])
        matched=match_run(row['run_binding'],row['request'],row['attempt'],receipt,resolver)
        with self.assertRaisesRegex(ExecutionError,'recovery_policy_unestablished'):require_recovery_intent(matched,resolver,recovery.MODE)

    @covers('X05')
    def test_admitted_import_keeps_unknown_origin_and_cli_has_no_live_bootstrap(self):
        from crucis_causal.execution.authority import DriverBoundary
        from crucis_causal.connections.store import PackageStore
        from crucis_causal.connections.model import Builder as B1,contract as c1
        from crucis_causal.connections.evidence import capture_bytes
        with scratch() as root:
            selected=contract('s3.op.import_evidence');env=case.Environment(root/'coordinator',SimpleNamespace(namespace='no_provider',epoch='0'),scientific_path=None,native_operations=(*case.OPS,selected))
            b=B1('Supplied historical native bytes only');a=capture_bytes(b,b'opaque historical result',format_contract=c1('octets'))
            source=case.input_case.snapshot1(b,[a]);env.include(source)
            store=PackageStore(root/'imports')
            install_import_reader(env.registry,env.component,env.pin,DriverBoundary(env.journal,env.jctx,((env.owner,env.octx),)),store)
            req=api.OperationRequest(selected,({'role':'s3.role.sources','members':index([qualified(a,source.package_id)])},),
                ({'key':'occurrence','value':known(identity())},{'key':'reader','value':known(contract('s3.reader.supplied_evidence'))},{'key':'prior_import','value':not_applicable()}),identity())
            result=env.run(req);self.assertEqual(result.state,'completed',result.issues)
            receipts=[r for v in result.records.dependencies for r in v.records if r['record_type']=='s1.import_receipt']
            self.assertTrue(receipts);self.assertTrue(all(r['payload']['native_occurrence']['state']=='unresolved' for r in receipts))
            self.assertFalse(any(r['record_type'] in ('s1.request','s1.attempt') for v in result.records.dependencies for r in v.records))
            for args in [[],['--help']]:
                done=subprocess.run([sys.executable,'-B','-m','crucis_causal.execution',*args],cwd=ROOT,capture_output=True,text=True,check=True)
                self.assertIn('supplied',done.stdout)
            snapshot=root/'source.json';snapshot.write_bytes(source.source_bytes)
            inspected=subprocess.run([sys.executable,'-B','-m','crucis_causal.execution','inspect',str(snapshot)],cwd=ROOT,capture_output=True,text=True,check=True)
            self.assertEqual(json.loads(inspected.stdout)['package_id'],source.package_id)
            recovery_plan=subprocess.run([sys.executable,'-B','-m','crucis_causal.execution','recovery-plan',str(snapshot),'--kind','restart','--policy','s3.not_installed'],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(recovery_plan.returncode,2);self.assertEqual(json.loads(recovery_plan.stdout)['effects'],[])


if __name__=='__main__':unittest.main()
