"""B02 actual local crash/reopen, contention and immutable byte gates (DLV-08/09)."""
import base64
import copy
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager,closing
from dataclasses import replace
import json
import os
from pathlib import Path
import queue
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from test_audit_execution_wire import fixture,LIMITS,covers
from crucis_causal.execution import api,codec
from crucis_causal.execution.journal import Journal,binding_digest,resolve_binding,delta_binding
from crucis_causal.execution.model import ExecutionError,canonical,contract,digest,identity,known,reference,scope,unknown
from crucis_causal.execution.store import ArtifactStore
from audit_fixtures.sc3_runtime.receipt_case import snapshot as retained_snapshot, triplet

@contextmanager
def scratch():
    base=Path(os.environ.get('CRUCIS_TEST_TEMP',tempfile.gettempdir())).resolve()
    temp=tempfile.TemporaryDirectory(prefix='crucis-s3-journal-',dir=base)
    target=Path(temp.name).resolve()
    assert target.parent==base and target.name.startswith('crucis-s3-journal-')
    try:yield target
    finally:
        assert Path(temp.name).resolve()==target and target.parent==base
        temp.cleanup()

def context(journal,account,views=(),fault=None):
    read=api.PinnedReadContext(tuple(views),api.supplied_read(v.package_id for v in views),None,LIMITS)
    return api.RuntimeContext(read,journal.control(account),fault=fault)

def opened(root):
    view,resolver=fixture()
    account=next(r['payload']['account'] for r in view.records if r['record_type']=='s3.account_view')
    journal=Journal(root);ctx=context(journal,account,resolver._views.values())
    delta=api.CommitDelta(view.records,tuple(view.package['roots']),tuple(resolver._views.values()))
    out=journal.append(account,'0',identity(),delta,ctx)
    if out.state!='completed':raise AssertionError(out.issues)
    return journal,ctx,account,out.value.head

def diagnostic(head,text):
    r=copy.deepcopy(next(r for r in head.snapshot.records if r['record_type']=='s3.diagnostic'))
    r['id']=identity();r['payload']['details']=text
    return api.CommitDelta((r,),(),())

def request_digest(account,revision,delta):
    return digest(canonical({'account':account,'expected_revision':revision,'delta':delta_binding(delta)}))

def killed_worker(root,packet,point):
    worker=ROOT/'tests/audit_fixtures/sc3_runtime/journal_worker.py'
    path=root/'input.json';path.write_bytes(canonical(packet))
    process=subprocess.Popen([sys.executable,'-B',str(worker),'--root',str(root/'db'),'--input',str(path),'--barrier',point],
        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    messages=queue.Queue()
    reader=threading.Thread(target=lambda:messages.put(process.stdout.readline()),daemon=True);reader.start()
    try:
        line=messages.get(timeout=30)
        if line.strip()!='READY:'+point:
            raise AssertionError('controlled barrier absent: '+line+process.stderr.read())
        process.kill();process.wait(timeout=15)
    finally:
        if process.poll() is None:process.kill();process.wait(timeout=15)
        reader.join(timeout=5)
        process.stdin.close();process.stdout.close();process.stderr.close()
    if reader.is_alive():raise AssertionError('owned barrier reader did not end')

class JournalCases(unittest.TestCase):
    @covers('F01','J01')
    def test_F01_capture_process_death_preserves_atomic_bytes_identity_and_cursor(self):
        for point,committed in [('before_journal_commit',False),('after_journal_commit',True)]:
            with self.subTest(point=point),scratch() as root:
                j,ctx,account,head=opened(root/'db')
                source=api.SourceIdentity(reference(next(r['id'] for r in head.snapshot.records if r['record_type']=='s3.source_frontier'),'source_frontier',head.snapshot.package_id),
                    contract('fixture_stream'),digest(b'filter'),known('g1'),known('c1'),contract('fixture_source_identity'))
                cursor=known({'contract':contract('fixture_cursor'),'position':'1','scope':scope()});tx=identity();occ=identity()
                packet={'mode':'capture','account':account,'revision':'1','transaction':tx,'records':[],'roots':[],'dependencies':[],
                    'source':{'subject':source.subject,'protocol':source.protocol,'filter_digest':source.filter_digest,'generation':source.generation,'consumer':source.consumer,'identity_rule':source.identity_rule},
                    'cursor':cursor,'raw':[{'occurrence':occ,'bytes':base64.b64encode(b'crash-capture').decode(),'extent':scope()}]}
                killed_worker(root,packet,point)
                fresh=Journal(root/'db');fresh_ctx=context(fresh,account)
                recovered=fresh.capture_transaction(account,tx,fresh_ctx)
                self.assertEqual(recovered.state,'completed' if committed else 'rejected')
                self.assertEqual(fresh.checkpoint(account,source,fresh_ctx),cursor if committed else unknown('s3.no_committed_source_position'))
                self.assertEqual(fresh.snapshot(account,'1',fresh_ctx).value.source_bytes,head.snapshot.source_bytes)
                if committed:
                    self.assertEqual(recovered.value.source,source)
                    self.assertEqual(fresh.artifacts.read(digest(b'crash-capture')),b'crash-capture')
                    with closing(sqlite3.connect(fresh.path)) as db:
                        extra=json.loads(db.execute('SELECT extra FROM transactions WHERE id=?',(tx,)).fetchone()[0])
                    self.assertEqual(extra['members'][0]['occurrence'],occ)
                    self.assertEqual(extra['members'][0]['artifact'],recovered.value.artifacts[0])
                with closing(sqlite3.connect(fresh.path)) as db:
                    oracle_rows=db.execute('SELECT COUNT(*) FROM transactions WHERE id=?',(tx,)).fetchone()[0]
                triplet('F01','capture_'+point,{'transaction_rows':oracle_rows,'capture_metadata_committed':bool(oracle_rows),
                    'artifact_bytes_present':fresh.artifacts._path(digest(b'crash-capture')['value']).is_file(),'native_calls':0},
                    {'before':retained_snapshot(head.snapshot),'transaction':tx,'barrier':point,'actual_process_killed':True},
                    {'state':recovered.state,'checkpoint':fresh.checkpoint(account,source,fresh_ctx),
                     'current':retained_snapshot(fresh.head(account,fresh_ctx).value.snapshot)})


    @covers('J01')
    def test_J01_prepare_process_death_never_resurrects_committed_permit(self):
        with scratch() as root:
            j,ctx,account,head=opened(root/'db')
            c=next(r for r in head.snapshot.records if r['record_type']=='s3.effect_command')
            d=next(r for r in head.snapshot.records if r['record_type']=='s3.transmission')
            command=reference(c['id'],'effect_command');transmission=reference(d['id'],'transmission')
            packet={'mode':'prepare','account':account,'revision':'1','transaction':d['id'],'records':[],'roots':[],
                'dependencies':[base64.b64encode(v.source_bytes).decode() for v in ctx.read.views],
                'command':command,'transmission':transmission}
            killed_worker(root,packet,'after_journal_commit')
            fresh=Journal(root/'db');fresh_ctx=context(fresh,account,ctx.read.views)
            resolver=codec.Resolver((*ctx.read.views,head.snapshot),limits=LIMITS)
            grants=api.OwnerBindingReceipts((),binding_digest(resolve_binding(c['payload']['binding'],head.snapshot.package_id,resolver)),api.ValidityContext((),unknown(),(),api.RecordDelta()))
            replay=fresh.prepare_issue(command,head,grants,fresh_ctx,transmission)
            self.assertEqual(replay.state,'completed',replay.issues);self.assertIsNone(replay.value.runtime_permit)
            with self.assertRaises(ExecutionError):fresh.consume(replay.value,fresh_ctx)

    @covers('J01')
    def test_J01_exact_replay_changed_binding_old_cutoff_and_reopen(self):
        with scratch() as root:
            j,ctx,account,head=opened(root)
            delta=diagnostic(head,'new evidence');tx=identity()
            expected=request_digest(account,'1',delta)
            first=j.append(account,'1',tx,delta,ctx)
            self.assertEqual(first.state,'completed',first.issues)
            again=j.append(account,'1',tx,delta,ctx)
            self.assertEqual(first.value.head.snapshot.source_bytes,again.value.head.snapshot.source_bytes)
            self.assertEqual(j.append(account,'1',tx,diagnostic(head,'changed'),ctx).issues[0].code,'s3.transaction_binding_conflict')
            self.assertEqual(j.snapshot(account,'1',ctx).value.source_bytes,head.snapshot.source_bytes)
            fresh=Journal(root);fresh_ctx=context(fresh,account)
            self.assertEqual(fresh.head(account,fresh_ctx).value.revision,'2')
            self.assertEqual(fresh.lookup_transaction(account,tx,expected,fresh_ctx).value.state,'committed')
            self.assertEqual(fresh.lookup_transaction(account,tx,digest(b'wrong'),fresh_ctx).value.state,'disputed')
            with closing(sqlite3.connect(j.path)) as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM transactions').fetchone()[0],2)

    @covers('J01')
    def test_J01_two_actual_writers_have_one_expected_revision_winner(self):
        with scratch() as root:
            j,ctx,account,head=opened(root)
            j2=Journal(root);ctx2=context(j2,account)
            barrier=threading.Barrier(2)
            def writer(journal,owner,label):
                delta=diagnostic(head,label);barrier.wait(timeout=15)
                return journal.append(account,'1',identity(),delta,owner)
            with ThreadPoolExecutor(max_workers=2) as pool:
                a=pool.submit(writer,j,ctx,'left');b=pool.submit(writer,j2,ctx2,'right')
                results=[a.result(timeout=30),b.result(timeout=30)]
            self.assertEqual(sorted(r.state for r in results),['completed','rejected'])
            self.assertEqual(next(r for r in results if r.state=='rejected').issues[0].code,'s3.stale_journal_revision')
            self.assertEqual(j.head(account,ctx).value.revision,'2')
            with closing(sqlite3.connect(j.path)) as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM transactions').fetchone()[0],2)

    @covers('F01')
    def test_F01_kill_before_and_after_commit_then_fresh_process_reconciliation(self):
        worker=ROOT/'tests/audit_fixtures/sc3_runtime/journal_worker.py'
        for point,expected_state,expected_revision in [('before_journal_commit','not_committed','1'),('after_journal_commit','committed','2')]:
            with self.subTest(point=point),scratch() as root:
                j,ctx,account,head=opened(root/'db')
                delta=diagnostic(head,point);tx=identity();expected=request_digest(account,'1',delta)
                packet={'account':account,'revision':'1','transaction':tx,'records':list(delta.records),'roots':[],
                    'dependencies':[]}
                path=root/'input.json';path.write_bytes(canonical(packet))
                process=subprocess.Popen([sys.executable,'-B',str(worker),'--root',str(root/'db'),'--input',str(path),'--barrier',point],
                    stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                messages=queue.Queue()
                threading.Thread(target=lambda:messages.put(process.stdout.readline()),daemon=True).start()
                try:
                    line=messages.get(timeout=30)
                    self.assertEqual(line.strip(),'READY:'+point)
                    process.kill();process.wait(timeout=15)
                finally:
                    if process.poll() is None:process.kill();process.wait(timeout=15)
                    process.stdin.close();process.stdout.close();process.stderr.close()
                fresh=Journal(root/'db');fresh_ctx=context(fresh,account)
                self.assertEqual(fresh.lookup_transaction(account,tx,expected,fresh_ctx).value.state,expected_state)
                recovered=fresh.head(account,fresh_ctx).value
                self.assertEqual(recovered.revision,expected_revision)
                self.assertEqual(fresh.snapshot(account,'1',fresh_ctx).value.source_bytes,head.snapshot.source_bytes)
                with closing(sqlite3.connect(fresh.path)) as db:
                    count=db.execute('SELECT COUNT(*) FROM transactions WHERE id=?',(tx,)).fetchone()[0]
                self.assertEqual(count,1 if expected_state=='committed' else 0)
                triplet('F01','append_'+point,{'transaction_rows':count,'native_calls':0},
                    {'before':retained_snapshot(head.snapshot),'transaction':tx,'barrier':point,'actual_process_killed':True},
                    {'revision':recovered.revision,'state':expected_state,'current':retained_snapshot(recovered.snapshot)})


    @covers('J01')
    def test_J01_durable_claim_has_one_live_permit_and_no_replay_permit(self):
        with scratch() as root:
            j,ctx,account,head=opened(root)
            c=next(r for r in head.snapshot.records if r['record_type']=='s3.effect_command')
            d=next(r for r in head.snapshot.records if r['record_type']=='s3.transmission')
            resolver=codec.Resolver((*ctx.read.views,head.snapshot),limits=LIMITS)
            binding=resolve_binding(c['payload']['binding'],head.snapshot.package_id,resolver)
            amount=binding_digest(binding)
            grants=api.OwnerBindingReceipts((),amount,api.ValidityContext((),unknown(),(),api.RecordDelta()))
            first=j.prepare_issue(reference(c['id'],'effect_command'),head,grants,ctx,reference(d['id'],'transmission'))
            self.assertEqual(first.state,'completed',first.issues)
            again=j.prepare_issue(reference(c['id'],'effect_command'),head,grants,ctx,reference(d['id'],'transmission'))
            self.assertEqual(again.state,'completed',again.issues);self.assertIsNone(again.value.runtime_permit)
            with self.assertRaises(ExecutionError):j.consume(again.value,ctx)
            forged=replace(first.value,runtime_permit=object.__new__(api.OpaqueIssuePermit))
            with self.assertRaises(ExecutionError):j.consume(forged,ctx)
            j.consume(first.value,ctx)
            with self.assertRaises(ExecutionError):j.consume(first.value,ctx)
            fresh=Journal(root);fresh_ctx=context(fresh,account)
            recovered=fresh.prepare_issue(reference(c['id'],'effect_command'),head,grants,
                replace(fresh_ctx,read=ctx.read),reference(d['id'],'transmission'))
            self.assertEqual(recovered.state,'completed',recovered.issues);self.assertIsNone(recovered.value.runtime_permit)

    @covers('J01')
    def test_J01_uncertain_commit_mints_no_permit_and_takeover_fences_old_writer(self):
        with scratch() as root:
            j,ctx,account,head=opened(root)
            c=next(r for r in head.snapshot.records if r['record_type']=='s3.effect_command')
            d=next(r for r in head.snapshot.records if r['record_type']=='s3.transmission')
            resolver=codec.Resolver((*ctx.read.views,head.snapshot),limits=LIMITS)
            grants=api.OwnerBindingReceipts((),binding_digest(resolve_binding(c['payload']['binding'],head.snapshot.package_id,resolver)),api.ValidityContext((),unknown(),(),api.RecordDelta()))
            def lost(label):
                if label=='after_journal_commit':raise OSError('injected lost commit acknowledgement')
            result=j.prepare_issue(reference(c['id'],'effect_command'),head,grants,replace(ctx,fault=lost),reference(d['id'],'transmission'))
            self.assertEqual(result.state,'rejected');self.assertIsNone(result.value)
            replay=j.prepare_issue(reference(c['id'],'effect_command'),head,grants,ctx,reference(d['id'],'transmission'))
            self.assertEqual(replay.state,'completed',replay.issues);self.assertIsNone(replay.value.runtime_permit)
            current=j.head(account,ctx).value
            new_cap=j.takeover(account,ctx)
            self.assertEqual(j.append(account,current.revision,identity(),diagnostic(head,'stale'),ctx).issues[0].code,'s3.stale_storage_epoch')
            new_ctx=replace(ctx,control=new_cap)
            self.assertEqual(j.append(account,current.revision,identity(),diagnostic(head,'current'),new_ctx).state,'completed')

    @covers('J01')
    def test_J01_raw_capture_replay_and_fault_do_not_advance_past_retained_bytes(self):
        with scratch() as root:
            j,ctx,account,head=opened(root)
            source=api.SourceIdentity(reference(next(r['id'] for r in head.snapshot.records if r['record_type']=='s3.source_frontier'),'source_frontier',head.snapshot.package_id),
                contract('fixture_stream'),digest(b'filter'),known('g1'),known('c1'),contract('fixture_source_identity'))
            raw=api.CapturedBytes(identity(),source,b'event1',scope(),api.RecordDelta())
            cursor=known({'contract':contract('fixture_cursor'),'position':'1','scope':scope()});batch=identity()
            malformed=replace(source,generation=known(True))
            rejected=j.commit_capture(malformed,'1',identity(),(replace(raw,source=malformed),),api.CommitDelta(),cursor,ctx)
            self.assertEqual(rejected.state,'rejected')
            self.assertEqual(j.head(account,ctx).value.revision,'1')
            first=j.commit_capture(source,'1',batch,(raw,),api.CommitDelta(),cursor,ctx)
            self.assertEqual(first.state,'completed',first.issues)
            repeat=j.commit_capture(source,'1',batch,(raw,),api.CommitDelta(),cursor,ctx)
            self.assertEqual(first.value.artifacts,repeat.value.artifacts)
            changed_meta=api.RecordDelta(records=diagnostic(head,'different raw metadata').records)
            changed=j.commit_capture(source,'1',batch,(replace(raw,metadata=changed_meta),),api.CommitDelta(),cursor,ctx)
            self.assertEqual(changed.issues[0].code,'s3.transaction_binding_conflict')
            self.assertEqual(j.checkpoint(account,source,ctx),cursor)
            fresh=Journal(root);recovered=fresh.capture_transaction(account,batch,context(fresh,account))
            self.assertEqual(recovered.state,'completed',recovered.issues)
            self.assertEqual(recovered.value.source,source)
            self.assertEqual(recovered.value.artifacts,first.value.artifacts)
            with closing(sqlite3.connect(j.path)) as db:
                extra=json.loads(db.execute('SELECT extra FROM transactions WHERE id=?',(batch,)).fetchone()[0])
            self.assertEqual(extra['members'][0]['occurrence'],raw.occurrence)
            self.assertEqual(extra['members'][0]['digest'],digest(b'event1'))
            before=j.head(account,ctx).value
            def full(label):
                if label=='artifact_before_flush':raise OSError(28,'injected space failure')
            j.artifacts.fault=full
            failed=j.commit_capture(source,before.revision,identity(),(replace(raw,occurrence=identity(),bytes=b'event2'),),api.CommitDelta(),known({**cursor['value'],'position':'2'}),ctx)
            self.assertEqual(failed.state,'rejected')
            self.assertEqual(j.head(account,ctx).value.revision,before.revision)
            self.assertEqual(j.checkpoint(account,source,ctx),cursor)
            self.assertTrue(j.artifacts.orphans())

    @covers('J01')
    def test_J01_actual_profile_and_changed_artifact_is_never_repaired(self):
        with scratch() as root:
            j,ctx,account,head=opened(root)
            self.assertEqual({k:j.profile()[k] for k in ['journal_mode','synchronous','foreign_keys']},
                {'journal_mode':'delete','synchronous':'2','foreign_keys':'1'})
            store=ArtifactStore(root/'separate');bound=store.stage(b'original')
            store._path(bound['value']).write_bytes(b'changed')
            with self.assertRaisesRegex(ExecutionError,'integrity_mismatch'):store.read(bound)
            with self.assertRaises(ExecutionError):store.stage(b'original')
            self.assertEqual(store._path(bound['value']).read_bytes(),b'changed')
            rejected=j.append(account,'1',identity(),api.RecordDelta(),ctx)
            self.assertEqual(rejected.state,'rejected')
            self.assertEqual(rejected.issues[0].code,'s3.immutable_commit_delta_required')

if __name__=='__main__':unittest.main()
