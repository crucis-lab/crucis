"""B11 actual local publication/copy gates; no remote publication (DLV-08/09)."""
from dataclasses import replace
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests/audit_fixtures/sc3_runtime'))
from test_audit_execution_wire import covers
from test_audit_execution_journal import scratch
from test_audit_execution_coordinator import fault_receipt
import publication_case as case
from crucis_causal.execution import api,codec
from crucis_causal.execution.model import ExecutionError,canonical,contract,digest,identity,known,qualified,reference,scope
from crucis_causal.execution.projection import validate_audience,exact_native_projection


def oracle(env):
    with env.store._db() as db:
        return {'publications':[{'id':r['id'],'package':r['package'],'digest':json.loads(r['digest'])} for r in db.execute('SELECT * FROM publications')],
            'pointers':[dict(r)|{'selection':json.loads(r['selection'])} for r in db.execute('SELECT * FROM pointers')],
            'copies':[dict(r)|{'digest':json.loads(r['digest']),'physical_file':(env.store.copies/r['id']).is_file()} for r in db.execute('SELECT * FROM copies')]}


def fault(code,variant,env,**details):
    head=env.journal.head(env.account,env.jctx).value
    fault_receipt(code,variant,'receiver-oracle',oracle(env))
    fault_receipt(code,variant,'history-prefix',{'revision':head.revision,'snapshot':head.snapshot.package_id,'digest':head.snapshot.digest})
    fault_receipt(code,variant,'recovered-view',details)


def receipts(result):return [r for r in result.records.records if r['record_type']=='s3.publication_receipt']


class PublicationCases(unittest.TestCase):
    @covers('F14','OP21P','OP22P','OP21H','OP22H')
    def test_lost_manifest_commit_reply_reconciles_exact_bytes_and_key_after_reopen(self):
        with scratch() as root:
            env=case.Environment(root);view,audience=env.target();draft=env.freeze(view,audience)
            self.assertEqual(draft.state,'completed',draft.issues);raw=view.source_bytes
            request=env.publish_request(draft.value);publication_id=next(p['value']['value'] for p in request.parameters if p['key']=='publication_id')
            planned=env.plan(request);self.assertEqual(planned.state,'completed',planned.issues)
            group,d=identity(),identity();packet=case.packet(env,planned.value,group,d)
            def lost(label):
                if label=='publication_after_commit':raise OSError('actual manifest commit reply lost')
            env.store_fault=lost;admitted=env.admit(planned.value,group=group);self.assertEqual(admitted.state,'completed',admitted.issues)
            failed=env.issue(admitted.value,transmission=d);self.assertNotEqual(failed.state,'completed');self.assertEqual(len(oracle(env)['publications']),1)
            fresh,original=case.reopen(packet);new=fresh.admit(original,group=group);self.assertEqual(new.state,'completed',new.issues)
            replay=fresh.issue(new.value,transmission=d);self.assertEqual(replay.state,'partial');self.assertIsNone(replay.value.token.runtime_permit)
            found=fresh.run(fresh.lookup_request(planned.value.command,draft.value,publication_id));self.assertEqual(found.state,'completed',found.issues)
            self.assertEqual(fresh.store.artifacts.read(view.digest),raw);self.assertEqual(view.source_bytes,raw)
            self.assertEqual(len(oracle(fresh)['publications']),1)
            self.assertTrue(any(r['record_type']=='s3.publication_receipt' for v in found.records.dependencies for r in v.records))
            wrong=fresh.lookup_request(planned.value.command,draft.value,identity());self.assertNotEqual(fresh.run(wrong).state,'completed')
            fault('F14','manifest_committed_before_ack',fresh,original_package=view.package_id,same_digest=True,publications='1',no_refreeze=True)

    @covers('F14','OP21H')
    def test_interrupted_staging_does_not_expose_committed_root(self):
        with scratch() as root:
            env=case.Environment(root);view,audience=env.target();draft=env.freeze(view,audience).value
            request=env.publish_request(draft);plan=env.plan(request);self.assertEqual(plan.state,'completed',plan.issues)
            def fail(label):
                if label=='publication_after_stage':raise OSError('before manifest commit')
            env.store_fault=fail
            admitted=env.admit(plan.value);self.assertEqual(admitted.state,'completed',admitted.issues)
            out=env.issue(admitted.value);self.assertNotEqual(out.state,'completed');self.assertEqual(oracle(env)['publications'],[])
            self.assertTrue(env.store.artifacts.orphans())
            fault('F14','stage_without_manifest',env,committed_roots='0',orphan_bytes_retained=True)

    @covers('F15','OP23P','OP23H')
    def test_revision_CAS_rejects_ABA_even_when_selection_bytes_match_again(self):
        with scratch() as root:
            env=case.Environment(root);views=[];commits=[]
            for label in ('A','B'):
                view,audience=env.target(label=label);draft=env.freeze(view,audience).value
                out=env.run(env.publish_request(draft));self.assertEqual(out.state,'completed',out.issues)
                views.append(view);commits.append(qualified(reference(receipts(out)[0]['id'],'publication_receipt'),next(v.package_id for v in out.records.dependencies if any(r['id']==receipts(out)[0]['id'] for r in v.records))))
            a,b=views;ra,rb=commits
            for view,receipt,rev in [(a,ra,'0'),(b,rb,'1'),(a,ra,'2')]:
                out=env.run(env.pointer_request(view,receipt,rev));self.assertEqual(out.state,'completed',out.issues)
            stale=env.run(env.pointer_request(b,rb,'1'));self.assertNotEqual(stale.state,'completed')
            rows=oracle(env)['pointers'];self.assertEqual(rows[0]['revision'],3);self.assertEqual(rows[0]['selection']['package_id'],a.package_id)
            fault('F15','A_B_A_stale_revision',env,current_revision='3',stale_revision='1',value_equal_A=True,value_CAS_not_substituted=True)

    @covers('F16','OP24P','OP24H','OP25P','OP25H','OP26P','OP26H')
    def test_copy_revoke_delete_interruption_keeps_pins_other_copy_and_exposure_obligation(self):
        with scratch() as root:
            env=case.Environment(root);subject,location,copy_id=env.artifact();raw=subject.source_view.source_bytes
            other=identity();env.store.install_copy(other,b'Explicit owned copy bytes',api.RuntimeContext(env.context.read,env.store_control))
            self.assertEqual(env.run(env.locate_request(subject,copy_id)).state,'completed')
            self.assertNotEqual(env.run(env.locate_request(subject,copy_id,expected_digest=digest(b'changed'))).state,'completed')
            for method in ('revoke','delete'):
                request=env.copy_request(method,subject,location);plan=env.plan(request);self.assertEqual(plan.state,'completed',plan.issues)
                g,d=identity(),identity();packet=case.packet(env,plan.value,g,d)
                def lose(label):
                    if label=='copy_after_'+method+'_commit':raise OSError('actual copy effect reply lost')
                env.store_fault=lose;admitted=env.admit(plan.value,group=g);self.assertEqual(admitted.state,'completed',admitted.issues)
                out=env.issue(admitted.value,transmission=d);self.assertNotEqual(out.state,'completed')
                env,original=case.reopen(packet)
                replay=env.admit(original,group=g);self.assertEqual(replay.state,'completed',replay.issues)
                repeated=env.issue(replay.value,transmission=d);self.assertEqual(repeated.state,'partial');self.assertIsNone(repeated.value.token.runtime_permit)
                self.assertEqual(env.run(env.locate_request(subject,copy_id)).state,'completed')
                self.assertTrue((env.store.copies/other).is_file());self.assertEqual(subject.source_view.source_bytes,raw)
                if method=='delete':self.assertFalse((env.store.copies/copy_id).exists())
                h=env.journal.head(env.account,env.jctx).value
                self.assertTrue(any(r['record_type']=='s3.obligation' and r['payload']['disposition']=='unresolved' for r in h.snapshot.records))
                fault('F16',method+'_commit_before_reply',env,original_pin_retained=True,other_copy_retained=True,global_erasure=False,prior_exposure_erased=False)
            # Actually exercised positive receipts use a different explicitly
            # owned copy; prior uncertain operations are not retroactively passed.
            positive,where,key=env.artifact(b'Another explicitly owned copy')
            self.assertEqual(env.run(env.copy_request('revoke',positive,where)).state,'completed')
            self.assertEqual(env.run(env.copy_request('delete',positive,where)).state,'completed')
            bad=env.copy_request('delete',positive,where,owner=reference(identity(),'component',env.view.package_id))
            self.assertEqual(env.plan(bad).state,'rejected')

    @covers('X09','OP21H')
    def test_all_metadata_permissions_embedded_refs_and_opaque_assurance_are_checked(self):
        with scratch() as root:
            env=case.Environment(root);view,audience=env.target(opaque=True)
            result=env.freeze(view,audience);self.assertEqual(result.state,'completed',result.issues)
            closure=result.value.audience;resolver=codec.Resolver(env.context.read.views,limits=case.case.L)
            producer=next(r for r in view.records if r['record_type']=='s3.component')
            omitted=replace(closure,allowed_records=tuple(r for r in closure.allowed_records if r['target']!=producer['id']))
            with self.assertRaisesRegex(ExecutionError,'audience_record_not_allowed'):validate_audience(view,omitted,resolver,env.registry.payloads)
            missing=replace(closure,allowed_dependencies=())
            with self.assertRaisesRegex(ExecutionError,'dependency_not_allowed'):validate_audience(view,missing,resolver,env.registry.payloads)
            claim=api.ClaimRequest(contract('s3.fixture.semantic_secrecy'),scope(),api.PinnedInputs((),()))
            held=env.freeze(view,audience,(claim,));self.assertEqual(held.state,'partial');self.assertTrue(held.value.withheld)
            self.assertEqual(oracle(env)['publications'],[])
            # N13: a receipt cannot pin the whole package containing itself.
            # Its alleged external subject resolves back to that same package.
            circular=view.package
            descriptor=dict(circular['external_packages'][0])
            descriptor['package_id']=view.package_id
            descriptor['expected_digest']=known(view.digest)
            circular['external_packages'].append(descriptor)
            with self.assertRaisesRegex(ExecutionError,'duplicate_or_self_dependency'):
                codec.dumps(circular,case.case.L)
            # N13 direct form: subject_package is an ID, not a dependency Ref.
            # A known full-content pin cannot name its own containing package.
            from test_audit_execution_wire import fixture
            specimen,_=fixture();self_receipt=specimen.package
            native_receipt=next(r for r in self_receipt['records'] if r['record_type']=='s3.publication_receipt')
            native_receipt['payload']['subject_package']=specimen.package_id
            native_receipt['payload']['digest']=known(specimen.digest)
            with self.assertRaisesRegex(ExecutionError,'circular_publication_subject_digest'):
                codec.dumps(self_receipt,case.case.L)
            # An unresolved digest does not assert a circular whole-content pin.
            native_receipt['payload']['digest']={'state':'unresolved','reasons':['s3.not_observed'],'evidence':[]}
            codec.dumps(self_receipt,case.case.L)


    @covers('X09')
    def test_historical_L_native_export_is_exactly_611_bytes_two_entities_without_new_metadata(self):
        folder=ROOT/'tests/audit_fixtures/sc3_publication'
        artifact=json.loads((folder/'manifest.json').read_bytes());raw=(folder/'L-public.json').read_bytes();self.assertEqual(len(raw),611)
        original=ROOT/'crucis_causal/docs/subsystem3-complete-package-review-2026-11-03.json'
        if original.is_file():
            import hashlib
            self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(),artifact['source_sha256'])
            self.assertEqual(raw,json.loads(original.read_bytes())['native_public_artifacts'][0]['raw_utf8'].encode())
        def permission(raw,audience):return audience=='public' and digest(raw)==artifact['digest']
        public=exact_native_projection(raw,artifact['digest'],permission,audience='public')
        self.assertEqual(public,raw);self.assertEqual([r['id'] for r in json.loads(public)],artifact['members'])
        from crucis_causal.execution.store import ArtifactStore
        with scratch() as root:
            store=ArtifactStore(root/'native-export');bound=store.stage(public)
            self.assertEqual(bound,artifact['digest']);self.assertEqual(store.read(bound),raw)
        with self.assertRaises(ExecutionError):exact_native_projection(raw+b'\n',artifact['digest'],permission,audience='public')
        with self.assertRaises(ExecutionError):exact_native_projection(raw,artifact['digest'],permission,audience='unpermitted')


if __name__=='__main__':unittest.main()
