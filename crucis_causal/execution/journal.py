"""Cooperative single-host atomic history and local forwarding claims (DLV-08/09).

SQLite rollback DELETE/FULL is checked on every connection. Local capabilities
authorize only this storage namespace. They never authorize native/provider work.
"""
import builtins
import copy
from contextlib import contextmanager
import datetime
import json
from pathlib import Path
import re
import sqlite3
import threading
import weakref
from . import api, codec
from .model import (ExecutionError, Builder, canonical, contract, digest, identity, index,
                    known, qualified, reference, scope, source, unknown)

DDL = '''
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS accounts(id TEXT PRIMARY KEY, revision INTEGER NOT NULL, epoch TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY, data BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS account_records(account TEXT NOT NULL REFERENCES accounts(id), record TEXT NOT NULL REFERENCES records(id), revision INTEGER NOT NULL, PRIMARY KEY(account,record));
CREATE TABLE IF NOT EXISTS dependencies(id TEXT PRIMARY KEY, data BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS account_dependencies(account TEXT NOT NULL REFERENCES accounts(id), package TEXT NOT NULL REFERENCES dependencies(id), PRIMARY KEY(account,package));
CREATE TABLE IF NOT EXISTS snapshots(account TEXT NOT NULL REFERENCES accounts(id), revision INTEGER NOT NULL, package_id TEXT UNIQUE NOT NULL, data BLOB NOT NULL, PRIMARY KEY(account,revision));
CREATE TABLE IF NOT EXISTS transactions(id TEXT PRIMARY KEY, account TEXT NOT NULL REFERENCES accounts(id), fingerprint BLOB NOT NULL, binding BLOB NOT NULL, revision INTEGER NOT NULL, receipt TEXT NOT NULL, kind TEXT NOT NULL, extra BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS checkpoints(account TEXT NOT NULL REFERENCES accounts(id), source TEXT NOT NULL, cursor BLOB NOT NULL, transaction_id TEXT NOT NULL REFERENCES transactions(id), PRIMARY KEY(account,source));
CREATE TABLE IF NOT EXISTS epoch_history(id TEXT PRIMARY KEY, account TEXT NOT NULL REFERENCES accounts(id), previous TEXT NOT NULL, current TEXT NOT NULL, observed_at TEXT NOT NULL);
'''

def _time():
    return {'time_type':'utc_instant','value':datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='microseconds').replace('+00:00','Z'),
            'precision':'fractional_second','clock':unknown(),'uncertainty_seconds':unknown()}

def source_binding(value):
    if not isinstance(value, api.SourceIdentity): raise ExecutionError('s3.typed_source_identity_required')
    from .schema import validate_value
    for name,expr in [('subject','KnownRef'),('protocol','Contract'),('filter_digest','Digest'),('generation','K(String)'),('consumer','K(String)'),('identity_rule','Contract')]:
        validate_value(getattr(value,name),expr,'source/'+name)
    return {'subject':value.subject,'protocol':value.protocol,'filter_digest':value.filter_digest,
            'generation':value.generation,'consumer':value.consumer,'identity_rule':value.identity_rule}

def delta_binding(delta, limits=None):
    if not isinstance(delta, api.CommitDelta): raise ExecutionError('s3.immutable_commit_delta_required')
    if any(not isinstance(getattr(delta,k),tuple) for k in ['records','roots','dependencies']):raise ExecutionError('s3.bounded_commit_sequences_required')
    if any(not isinstance(v, api.PinnedView) for v in delta.dependencies): raise ExecutionError('s3.pinned_dependencies_required')
    for view in delta.dependencies:
        actual=codec.parse_snapshot(view.source_bytes,limits or api.Limits(),access=view.read_scope)
        if (actual.package_id,actual.format,actual.digest)!=(view.package_id,view.format,view.digest):raise ExecutionError('s3.pinned_view_mismatch')
    return {'records':list(delta.records),'roots':list(delta.roots),
            'dependencies':[{'package_id':v.package_id,'digest':v.digest} for v in delta.dependencies]}

def resolve_binding(ref, anchor, resolver):
    """Resolve exact role inputs once, retaining their original wire references."""
    record, pid = resolver.record(ref, anchor)
    if record['record_type'] != 's3.operation_binding':raise ExecutionError('s3.operation_binding_required')
    entries=[]
    for role in record['payload']['roles']:
        for member in role['members']['members']:
            found, source_pid = resolver.record(member, pid)
            entries.append(api.BoundInput(role['role'],copy.deepcopy(member),found,source_pid,resolver.view(source_pid).digest))
    return api.ResolvedOperationBinding(record,{'package_id':pid,'format':resolver.view(pid).format},
        api.PinnedInputs(tuple(entries),resolver.closure(pid)))

def binding_digest(binding):
    """Exact record/context/input-pin digest, not receiver idempotency."""
    if not isinstance(binding,api.ResolvedOperationBinding):raise ExecutionError('s3.resolved_binding_required')
    view=next((v for v in binding.inputs.source_views if v.package_id==binding.context['package_id']),None)
    if view is None:raise ExecutionError('s3.binding_source_pin_required')
    return digest(canonical({'record':binding.record,'context':binding.context,'source_digest':view.digest,
        'inputs':[{'role':e.role,'reference':e.reference,'source_package':e.source_package,'source_digest':e.source_digest} for e in binding.inputs.entries]}))

class Journal:
    def __init__(self, root, *, limits=None, artifacts=None, busy_timeout_ms='5000'):
        from .store import ArtifactStore
        self.root = Path(root).resolve()
        if str(self.root).startswith('\\\\'): raise ExecutionError('s3.network_store_not_qualified')
        if not isinstance(busy_timeout_ms,str) or not re.fullmatch(r'[1-9][0-9]*',busy_timeout_ms) or int(busy_timeout_ms)>60000:
            raise ExecutionError('s3.bounded_busy_timeout_required')
        self.timeout = int(busy_timeout_ms)
        self.limits = limits or api.Limits()
        self.root.mkdir(parents=True,exist_ok=True)
        self.path = self.root/'history.sqlite3'
        self.artifacts = artifacts or ArtifactStore(self.root/'artifacts',max_bytes=self.limits.max_external_bytes)
        self._controls, self._permits, self._epochs = weakref.WeakKeyDictionary(),weakref.WeakKeyDictionary(),weakref.WeakKeyDictionary()
        self._guard = threading.RLock()
        with self._db() as db:
            db.executescript(DDL)
            producer = Builder('Local S3 journal recorder',created_at=known(_time()))
            record = next(iter(producer._records.values()))
            db.execute('INSERT OR IGNORE INTO meta(key,value) VALUES(?,?)',('producer',canonical(record)))
            self.producer = json.loads(db.execute('SELECT value FROM meta WHERE key=?',('producer',)).fetchone()[0])

    @contextmanager
    def _db(self):
        db=sqlite3.connect(self.path,timeout=self.timeout/1000,isolation_level=None)
        db.row_factory=sqlite3.Row
        try:
            mode=db.execute('PRAGMA journal_mode=DELETE').fetchone()[0]
            db.execute('PRAGMA synchronous=FULL');db.execute('PRAGMA foreign_keys=ON')
            db.execute('PRAGMA busy_timeout='+str(self.timeout))
            if mode.lower()!='delete' or db.execute('PRAGMA synchronous').fetchone()[0]!=2 or db.execute('PRAGMA foreign_keys').fetchone()[0]!=1:
                raise ExecutionError('s3.sqlite_profile_not_established')
            yield db
        finally:
            db.close()

    def profile(self):
        with self._db() as db:
            return {'sqlite':sqlite3.sqlite_version,'journal_mode':db.execute('PRAGMA journal_mode').fetchone()[0],
                    'synchronous':str(db.execute('PRAGMA synchronous').fetchone()[0]),'foreign_keys':str(db.execute('PRAGMA foreign_keys').fetchone()[0]),
                    'busy_timeout_ms':str(self.timeout),'fault_scope':'cooperative_same_host_process_crash_only'}

    def control(self, account, *, rights=('read','write')):
        """Actual local namespace-owner bootstrap, not a serialized self-grant.

        Constructing/owning this service gives the caller its local storage admin
        role. Remote deployments must supply their own owner implementation.
        """
        from .schema import validate_value
        validate_value(account,'KnownRef(account)')
        if set(rights)-{'read','write'}: raise ExecutionError('s3.unknown_storage_right')
        with self._db() as db:
            row=db.execute('SELECT epoch FROM accounts WHERE id=?',(account['target'],)).fetchone()
        cap=api.OpaqueControlCapability(api._OPAQUE_KEY,self)
        with self._guard:self._controls[cap]=(account['target'],row['epoch'] if row else '0',frozenset(rights))
        return cap

    def _check(self, db, account, context, right):
        cap=getattr(context,'control',None)
        with self._guard:binding=self._controls.get(cap) if isinstance(cap,api.OpaqueControlCapability) else None
        if binding is None or binding[0]!=account['target'] or right not in binding[2]: raise ExecutionError('s3.storage_control_denied')
        row=db.execute('SELECT epoch FROM accounts WHERE id=?',(account['target'],)).fetchone()
        epoch=row['epoch'] if row else '0'
        if binding[1]!=epoch: raise ExecutionError('s3.stale_storage_epoch')
        return epoch

    @staticmethod
    def _fault(context, label):
        if getattr(context,'fault',None):context.fault(label)

    def takeover(self, account, context):
        """Explicit storage-owner epoch transition; native work is unaffected."""
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            old=self._check(db,account,context,'write')
            if not db.execute('SELECT 1 FROM accounts WHERE id=?',(account['target'],)).fetchone():raise ExecutionError('s3.account_not_open')
            current=str(int(old)+1)
            db.execute('UPDATE accounts SET epoch=? WHERE id=?',(current,account['target']))
            db.execute('INSERT INTO epoch_history VALUES(?,?,?,?,?)',(identity(),account['target'],old,current,_time()['value']))
            db.execute('COMMIT')
        return self.control(account)

    def _snapshot(self, db, account, revision):
        row=db.execute('SELECT data FROM snapshots WHERE account=? AND revision=?',(account['target'],int(revision))).fetchone()
        if row is None:raise ExecutionError('s3.snapshot_unavailable')
        return codec.parse_snapshot(builtins.bytes(row['data']),self.limits)

    def _head(self, db, account):
        row=db.execute('SELECT revision FROM accounts WHERE id=?',(account['target'],)).fetchone()
        if row is None:raise ExecutionError('s3.account_not_open')
        return api.JournalHead(copy.deepcopy(account),str(row['revision']),self._snapshot(db,account,row['revision']))

    def head(self, account, context):
        try:
            with self._db() as db:
                db.execute('BEGIN');self._check(db,account,context,'read');value=self._head(db,account);db.execute('COMMIT')
            return api.CallResult('completed',value)
        except ExecutionError as exc:return api.rejected(exc.code,scope(account))
        except sqlite3.Error:return api.rejected('s3.journal_read_unconfirmed',scope(account))

    def snapshot(self, account, revision, context):
        try:
            with self._db() as db:
                self._check(db,account,context,'read');value=self._snapshot(db,account,revision)
            return api.CallResult('completed',value)
        except ExecutionError as exc:return api.rejected(exc.code,scope(account))
        except sqlite3.Error:return api.rejected('s3.journal_read_unconfirmed',scope(account))

    def _commit_value(self, db, row):
        account=reference(row['account'],'account')
        snapshot=self._snapshot(db,account,row['revision'])
        return api.JournalCommit(reference(row['receipt'],'journal_receipt',snapshot.package_id),
            api.JournalHead(account,str(row['revision']),snapshot),json.loads(row['binding']),contract('durability.local_process_crash'))

    def lookup_transaction(self, account, transaction, expected_binding, context):
        try:
            with self._db() as db:
                self._check(db,account,context,'read')
                row=db.execute('SELECT * FROM transactions WHERE id=? AND account=?',(transaction,account['target'])).fetchone()
                state='not_committed' if row is None else 'committed' if json.loads(row['binding'])==expected_binding else 'disputed'
                ref=known(self._commit_value(db,row).receipt) if state=='committed' else unknown('s3.transaction_not_established')
            return api.CallResult('completed',api.TransactionLookup(state,transaction,copy.deepcopy(expected_binding),ref,api.RecordDelta()))
        except ExecutionError as exc:return api.rejected(exc.code,scope(account))
        except sqlite3.Error:
            return api.CallResult('partial',api.TransactionLookup('unknown',transaction,expected_binding,unknown(),api.RecordDelta()),
                issues=(api.Issue('s3.journal_read_unconfirmed',scope(account),()),))

    def _dependencies(self, db, account):
        return tuple(codec.parse_snapshot(builtins.bytes(r['data']),self.limits) for r in db.execute(
            'SELECT d.data FROM dependencies d JOIN account_dependencies a ON d.id=a.package WHERE a.account=?',(account['target'],)))

    def _append(self, account, expected_revision, transaction, delta, context, binding, *, exposed=None, kind='append',extra=None,checkpoint=None):
        from .schema import validate_value
        validate_value(transaction,'ID');validate_value(expected_revision,'Index')
        delta_binding(delta,self.limits);fingerprint=digest(canonical(binding));exposed=exposed or fingerprint
        extra=extra or {}
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            epoch=self._check(db,account,context,'write')
            prior=db.execute('SELECT * FROM transactions WHERE id=?',(transaction,)).fetchone()
            if prior:
                if prior['account']!=account['target'] or json.loads(prior['fingerprint'])!=fingerprint:
                    raise ExecutionError('s3.transaction_binding_conflict')
                value=self._commit_value(db,prior);db.execute('COMMIT');return value,False,json.loads(prior['extra'])
            current=db.execute('SELECT revision FROM accounts WHERE id=?',(account['target'],)).fetchone()
            revision=current['revision'] if current else 0
            if revision!=int(expected_revision):raise ExecutionError('s3.stale_journal_revision')
            if current is None:db.execute('INSERT INTO accounts VALUES(?,?,?)',(account['target'],0,epoch))
            records=[json.loads(r['data']) for r in db.execute('SELECT r.data FROM records r JOIN account_records a ON r.id=a.record WHERE a.account=?',(account['target'],))]
            original={r['id']:r for r in records}
            dependencies={v.package_id:v for v in self._dependencies(db,account)}
            for view in delta.dependencies:
                old=dependencies.get(view.package_id)
                if old and old.source_bytes!=view.source_bytes:raise ExecutionError('s3.package_identity_conflict')
                dependencies[view.package_id]=view
            resolver=codec.Resolver(dependencies.values(),limits=self.limits)
            # Also enforce immutable identities across the durable global namespace.
            for record in delta.records:
                stored=db.execute('SELECT data FROM records WHERE id=?',(record['id'],)).fetchone()
                if stored and canonical(record)!=builtins.bytes(stored['data']):raise ExecutionError('s3.record_identity_conflict')
                original[record['id']]=copy.deepcopy(record)
            original[self.producer['id']]=copy.deepcopy(self.producer)
            new_revision=revision+1
            receipt_id=identity()
            producer_ref=reference(self.producer['id'],'component')
            receipt={'id':receipt_id,'record_type':'s3.journal_receipt','contract':contract('journal_receipt'),
                'producer':producer_ref,'created_at':known(_time()),'provenance':source('observed',procedure=contract('journal_append')),
                'payload':{'account':copy.deepcopy(account),'transaction':transaction,'previous_revision':str(revision),
                    'committed_revision':str(new_revision),'records':index([reference(r['id'],r['record_type']) for r in delta.records]+list(extra.get('artifacts',[]))),
                    'durability':contract('durability.local_process_crash')},'extensions':[]}
            original[receipt_id]=receipt
            roots=list(delta.roots)
            if not roots:
                if not current:raise ExecutionError('s3.initial_root_required')
                roots=self._snapshot(db,account,revision).package['roots']
            package={'format':contract('account_package'),'package_id':identity(),'roots':roots,'records':list(original.values()),
                'external_packages':[{'package_id':v.package_id,'format':v.format,'locator':unknown(),'expected_digest':known(v.digest),'access':'s3.explicitly_supplied'} for v in dependencies.values()],'extensions':[]}
            raw=codec.dumps(package,self.limits);view=codec.parse_snapshot(raw,self.limits)
            resolver.add(view);resolver.closure(view.package_id)
            self.artifacts.stage(raw)
            for record in original.values():
                db.execute('INSERT OR IGNORE INTO records VALUES(?,?)',(record['id'],canonical(record)))
                db.execute('INSERT OR IGNORE INTO account_records VALUES(?,?,?)',(account['target'],record['id'],new_revision))
            for v in dependencies.values():
                stored=db.execute('SELECT data FROM dependencies WHERE id=?',(v.package_id,)).fetchone()
                if stored and builtins.bytes(stored['data'])!=v.source_bytes:raise ExecutionError('s3.package_identity_conflict')
                # Every dependency is immutable and flushed before its durable reference.
                self.artifacts.stage(v.source_bytes)
                db.execute('INSERT OR IGNORE INTO dependencies VALUES(?,?)',(v.package_id,v.source_bytes))
                db.execute('INSERT OR IGNORE INTO account_dependencies VALUES(?,?)',(account['target'],v.package_id))
            db.execute('INSERT INTO snapshots VALUES(?,?,?,?)',(account['target'],new_revision,view.package_id,raw))
            db.execute('INSERT INTO transactions VALUES(?,?,?,?,?,?,?,?)',(transaction,account['target'],canonical(fingerprint),canonical(exposed),new_revision,receipt_id,kind,canonical(extra)))
            if checkpoint:
                source_key,cursor=checkpoint
                db.execute('INSERT INTO checkpoints VALUES(?,?,?,?) ON CONFLICT(account,source) DO UPDATE SET cursor=excluded.cursor, transaction_id=excluded.transaction_id',
                    (account['target'],source_key,canonical(cursor),transaction))
            db.execute('UPDATE accounts SET revision=? WHERE id=?',(new_revision,account['target']))
            self._fault(context,'before_journal_commit')
            db.execute('COMMIT')
            self._fault(context,'after_journal_commit')
            row=db.execute('SELECT * FROM transactions WHERE id=?',(transaction,)).fetchone()
            return self._commit_value(db,row),True,extra

    def append(self, account, expected_revision, transaction, delta, context):
        try:
            binding={'account':account,'expected_revision':expected_revision,'delta':delta_binding(delta,self.limits)}
            value,_,_=self._append(account,expected_revision,transaction,delta,context,binding)
            return api.CallResult('completed',value)
        except ExecutionError as exc:return api.rejected(exc.code,scope(account))
        except Exception:return api.rejected('s3.journal_commit_unconfirmed',scope(account))

    def prepare_issue(self, command, expected_head, grant_bindings, context, transmission):
        account=expected_head.account
        try:
            supplied=tuple(context.read.views)+(expected_head.snapshot,)
            resolver=codec.Resolver(supplied,limits=self.limits)
            c,c_pid=resolver.record(command,expected_head.snapshot.package_id)
            d,_=resolver.record(transmission,expected_head.snapshot.package_id)
            if c['record_type']!='s3.effect_command' or d['record_type']!='s3.transmission' or d['payload']['command']['target']!=c['id']:
                raise ExecutionError('s3.intent_command_transmission_mismatch')
            if c['payload']['account']['target']!=account['target']:raise ExecutionError('s3.intent_account_mismatch')
            if binding_digest(resolve_binding(c['payload']['binding'],c_pid,resolver)) != grant_bindings.binding_digest:
                raise ExecutionError('s3.intent_binding_digest_mismatch')
            with self._db() as db:epoch=self._check(db,account,context,'write')
            binding={'command':c,'transmission':d,'binding_digest':grant_bindings.binding_digest,'owner_receipts':list(grant_bindings.receipts),'epoch':epoch}
            delta=api.CommitDelta((c,d),(),tuple(resolver._views.values()))
            value,fresh,extra=self._append(account,expected_head.revision,d['id'],delta,context,binding,
                exposed=grant_bindings.binding_digest,kind='issue',extra={'epoch':epoch})
            opaque_epoch=api.OpaqueEpoch(api._OPAQUE_KEY,self)
            with self._guard:self._epochs[opaque_epoch]=(account['target'],extra['epoch'])
            permit=None
            if fresh:
                permit=api.OpaqueIssuePermit(api._OPAQUE_KEY,self)
                with self._guard:self._permits[permit]=(account['target'],c['id'],d['id'],canonical(grant_bindings.binding_digest),epoch)
            token=api.IssueToken(copy.deepcopy(command),value,opaque_epoch,copy.deepcopy(grant_bindings.binding_digest),copy.deepcopy(transmission),permit)
            return api.CallResult('completed',token)
        except ExecutionError as exc:return api.rejected(exc.code,scope(account))
        except Exception:return api.rejected('s3.intent_commit_unconfirmed',scope(account))

    def consume(self, token, context):
        """Guarded core entry only. Provider/owner checks remain independently required."""
        if not isinstance(token,api.IssueToken):raise ExecutionError('s3.actual_issue_token_required')
        if not isinstance(token.runtime_permit,api.OpaqueIssuePermit) or not isinstance(token.owner_epoch,api.OpaqueEpoch):
            raise ExecutionError('s3.issue_permit_absent_or_spent')
        account=token.intent_commit.head.account
        with self._db() as db:epoch=self._check(db,account,context,'write')
        expected=(account['target'],token.command['target'],token.transmission['target'],canonical(token.binding_digest),epoch)
        with self._guard:
            if self._permits.get(token.runtime_permit)!=expected or self._epochs.get(token.owner_epoch)!=(account['target'],epoch):
                raise ExecutionError('s3.issue_permit_absent_or_spent')
            del self._permits[token.runtime_permit]

    def commit_capture(self, source, expected_revision, batch_occurrence, bytes, delta, next_cursor, context):
        cap=getattr(context,'control',None)
        with self._guard:control=self._controls.get(cap) if isinstance(cap,api.OpaqueControlCapability) else None
        account=reference(control[0],'account') if control else None
        if account is None:return api.rejected('s3.storage_control_denied')
        try:
            from .schema import validate_value
            validate_value(next_cursor,'K(Cursor)')
            source_data=source_binding(source)
            if not isinstance(bytes,tuple) or not bytes:raise ExecutionError('s3.bounded_raw_capture_required')
            if len({b.occurrence for b in bytes})!=len(bytes):raise ExecutionError('s3.duplicate_capture_identity')
            if any(source_binding(b.source)!=source_data for b in bytes):raise ExecutionError('s3.capture_source_mismatch')
            if sum(len(b.bytes) for b in bytes)>int(self.limits.max_external_bytes):raise ExecutionError('s3.capture_byte_limit')
            for captured in bytes:
                if captured.metadata.native_additions or captured.metadata.scientific_additions:raise ExecutionError('s3.freeze_owned_additions_before_commit')
                if captured.metadata.roots:raise ExecutionError('s3.capture_metadata_roots_require_explicit_delta')
            binding={'source':source_data,'occurrence':batch_occurrence,'expected_revision':expected_revision,
                'raw':[{'occurrence':b.occurrence,'digest':digest(b.bytes),'extent':b.extent,
                    'metadata':delta_binding(api.CommitDelta(b.metadata.records,(),b.metadata.dependencies),self.limits)} for b in bytes],
                'delta':delta_binding(delta,self.limits),'next_cursor':next_cursor}
            bound=digest(canonical(binding))
            # Reconcile before generating replacement evidence IDs/staging bytes.
            with self._db() as db:
                self._check(db,account,context,'write')
                prior=db.execute('SELECT * FROM transactions WHERE id=?',(batch_occurrence,)).fetchone()
                if prior:
                    if prior['account']!=account['target'] or json.loads(prior['fingerprint'])!=bound:raise ExecutionError('s3.transaction_binding_conflict')
                    commit=self._commit_value(db,prior);extra=json.loads(prior['extra'])
                    return api.CallResult('completed',api.CaptureCommit(commit,api.SourceIdentity(**extra['source']),batch_occurrence,tuple(extra['artifacts']),extra['cursor']))
            from crucis_causal.connections.model import Builder as S1Builder,contract as c1
            from crucis_causal.connections.evidence import capture_bytes
            from crucis_causal.connections.codec import dumps as s1dumps
            b=S1Builder('S1 raw capture for S3 durable history');artifacts=[]
            records=list(delta.records);dependencies=list(delta.dependencies)
            for captured in bytes:
                if captured.metadata.native_additions or captured.metadata.scientific_additions:raise ExecutionError('s3.freeze_owned_additions_before_commit')
                self.artifacts.stage(captured.bytes)
                artifacts.append(capture_bytes(b,captured.bytes,format_contract=c1('opaque_bytes')))
                records.extend(captured.metadata.records);dependencies.extend(captured.metadata.dependencies)
            view=codec.parse_snapshot(s1dumps(b.package(artifacts)),self.limits)
            references=[qualified(r,view.package_id) for r in artifacts];dependencies.append(view)
            commit_delta=api.CommitDelta(tuple(records),delta.roots,tuple(dependencies))
            source_key=digest(canonical(source_data))['value']
            checkpoint=(source_key,next_cursor) if next_cursor['state']=='known' else None
            commit,_,extra=self._append(account,expected_revision,batch_occurrence,commit_delta,context,binding,
                kind='capture',extra={'source':source_data,'artifacts':references,'cursor':next_cursor,
                    'members':[{'occurrence':captured.occurrence,'artifact':artifact,'digest':digest(captured.bytes),'extent':captured.extent}
                               for captured,artifact in zip(bytes,references)]},checkpoint=checkpoint)
            return api.CallResult('completed',api.CaptureCommit(commit,api.SourceIdentity(**extra['source']),batch_occurrence,tuple(extra['artifacts']),copy.deepcopy(extra['cursor'])))
        except ExecutionError as exc:return api.rejected(exc.code,scope(account))
        except Exception:return api.rejected('s3.capture_commit_unconfirmed',scope(account))

    def checkpoint(self, account, source, context):
        with self._db() as db:
            self._check(db,account,context,'read')
            key=digest(canonical(source_binding(source)))['value']
            row=db.execute('SELECT cursor FROM checkpoints WHERE account=? AND source=?',(account['target'],key)).fetchone()
            return json.loads(row['cursor']) if row else unknown('s3.no_committed_source_position')

    def capture_transaction(self, account, occurrence, context):
        """Recover the original capture identity/byte mapping, never replacement IDs."""
        try:
            with self._db() as db:
                self._check(db,account,context,'read')
                row=db.execute('SELECT * FROM transactions WHERE id=? AND account=? AND kind=?',(occurrence,account['target'],'capture')).fetchone()
                if row is None:raise ExecutionError('s3.capture_transaction_not_established')
                extra=json.loads(row['extra']);commit=self._commit_value(db,row)
                value=api.CaptureCommit(commit,api.SourceIdentity(**extra['source']),occurrence,tuple(extra['artifacts']),extra['cursor'])
            return api.CallResult('completed',value)
        except ExecutionError as exc:return api.rejected(exc.code,scope(account))
        except sqlite3.Error:return api.rejected('s3.capture_lookup_unconfirmed',scope(account))
