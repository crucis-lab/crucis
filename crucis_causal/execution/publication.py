"""Qualified same-host immutable publication and revisioned copy store.

DLV-08/09. SQLite DELETE/FULL and exclusive flushed artifact installation are
reused. This is neither remote dissemination nor proof of erasing other copies.
"""
import builtins
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import sqlite3
from . import api,codec
from .authority import Authority
from .coordinator import typed_document,frozen,root_of
from .journal import resolve_binding,binding_digest
from .model import (Builder,ExecutionError,canonical,contract,digest,identity,index,
    known,qualified,reference,scope,unknown)
from .projection import validate_audience
from .registry import _verify_implementation
from .schema import validate_value,operation
from .store import ArtifactStore

BACKEND=contract('s3.local_immutable_store')
OPS=tuple(contract('s3.op.'+name) for name in ('publish','lookup_publication','select_current','locate_artifact','revoke_access','delete_artifact'))


class LocalPublicationStore:
    def __init__(self,root,component,implementation,journal,journal_context,owners,*,limits=None):
        self.root=Path(root).resolve()
        if str(self.root).startswith('\\\\'):raise ExecutionError('s3.network_store_not_qualified')
        validate_value(component,'KnownRef(component)');_verify_implementation(implementation)
        if not owners:raise ExecutionError('s3.required_owner_set_unestablished')
        self.component,self.implementation,self.journal,self.jctx,self.owners=component,implementation,journal,journal_context,tuple(owners)
        self.limits=limits or api.Limits();self.authority=Authority();self.root.mkdir(parents=True,exist_ok=True)
        self.artifacts=ArtifactStore(self.root/'artifacts',max_bytes=self.limits.max_external_bytes);self.path=self.root/'publication.sqlite3'
        self.copies=self.root/'copies';self.copies.mkdir(exist_ok=True)
        with self._db() as db:
            db.executescript('''
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS publications(id TEXT PRIMARY KEY,package TEXT NOT NULL,digest BLOB NOT NULL,binding BLOB NOT NULL,receipt BLOB NOT NULL,view BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS receipt_dependencies(id TEXT PRIMARY KEY,data BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS pointers(namespace TEXT NOT NULL,name TEXT NOT NULL,revision INTEGER NOT NULL,selection BLOB NOT NULL,PRIMARY KEY(namespace,name));
CREATE TABLE IF NOT EXISTS effects(transmission TEXT PRIMARY KEY,binding BLOB NOT NULL,result BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS copies(id TEXT PRIMARY KEY,digest BLOB NOT NULL,access INTEGER NOT NULL,retained INTEGER NOT NULL);
''')
            profile=canonical({'component':component,'implementation_reference':implementation.reference,'implementation_digest':implementation.content_digest}).decode()
            previous=db.execute('SELECT value FROM meta WHERE key=?',('profile',)).fetchone()
            existing=db.execute('SELECT value FROM meta WHERE key=?',('namespace',)).fetchone()
            if (previous and previous[0]!=profile) or (existing and not previous):raise ExecutionError('s3.publication_store_profile_migration_required')
            db.execute('INSERT OR IGNORE INTO meta VALUES(?,?)',('profile',profile))
            db.execute('INSERT OR IGNORE INTO meta VALUES(?,?)',('namespace',identity()))
            self.namespace=db.execute('SELECT value FROM meta WHERE key=?',('namespace',)).fetchone()[0]

    @contextmanager
    def _db(self):
        db=sqlite3.connect(self.path,isolation_level=None,timeout=5);db.row_factory=sqlite3.Row
        try:
            if db.execute('PRAGMA journal_mode=DELETE').fetchone()[0].lower()!='delete':raise ExecutionError('s3.store_journal_profile')
            db.execute('PRAGMA synchronous=FULL');db.execute('PRAGMA foreign_keys=ON')
            if db.execute('PRAGMA synchronous').fetchone()[0]!=2:raise ExecutionError('s3.store_sync_profile')
            yield db
        finally:db.close()

    def control(self):return self.authority.issue({'store':self.namespace,'component':self.component},control=True)

    def install(self,registry):
        from .registry import DeclaredDriver,supplied_callable,native_invocation
        def envelope(value):
            if not isinstance(value,dict) or set(value)!={'kind','recipient','channel','native_contract','native'} or value['kind']!='s3.native_invocation' or value['recipient']!=self.component or value['channel']!=BACKEND or value['native_contract']!=contract('s3.invocation.local_storage'):
                raise ExecutionError('s3.storage_invocation_grammar')
            if set(value['native'])!={'operation','binding_digest'} or value['native']['operation'] not in OPS:raise ExecutionError('s3.storage_invocation_grammar')
            validate_value(value['native']['binding_digest'],'Digest')
            return value
        def copy_scope(value):
            if not isinstance(value,dict) or set(value)!={'owner','subject','copies','rule'}:raise ExecutionError('s3.local_copy_scope_shape')
            for key in ('owner','subject'):validate_value(value[key],'KnownRef')
            validate_value(value['copies'],'KnownRef[]');validate_value(value['rule'],'Contract')
            return value
        for name,decoder in [('s3.invocation.local_storage',envelope),('s3.local_access_scope',copy_scope),('s3.local_copy_retention_scope',copy_scope)]:
            if not registry.payloads.supports(contract(name)):registry.payloads.register(contract(name),decoder)
        methods=(self.publish,self.lookup_commit,self.cas_pointer,self.locate,self.revoke,self.delete)
        descriptors=tuple(api.ExactDriverDescriptor(self.component,op,contract('s3.invocation.local_storage'),contract('s3.local_storage_return'),self.implementation,(),supplied_callable(method)) for op,method in zip(OPS,methods))
        def prepare(binding,inputs,context):
            _verify_implementation(self.implementation)
            return native_invocation(self.component,BACKEND,contract('s3.invocation.local_storage'),{'operation':binding.record['payload']['operation'],'binding_digest':binding_digest(binding)})
        self._declaration=DeclaredDriver(api.DriverDeclaration(self.component,descriptors,()),prepare)
        registry.drivers.install(self._declaration,registry)

    def issue_prepared(self,request,context,grants,issue_token,sink):
        """Explicit routing adapter; public Storage methods retain exact signatures."""
        from .registry import callable_value
        binding=request.binding;selected=binding.record['payload']['operation'];row=operation(selected)
        if row is None or not row['port'].startswith('Storage.'):return api.rejected('s3.storage_operation_mismatch')
        method=getattr(self,row['port'].split('.')[1])
        if callable_value(request.descriptor.method)!=method:return api.rejected('s3.actual_storage_method_required')
        resolver=codec.Resolver(context.read.views,limits=self.limits);pid=binding.context['package_id']
        p={v['key']:v['value']['value'] for v in binding.record['payload']['parameters'] if v['value']['state']=='known'}
        def role(name):return next(qualified(e.reference,e.source_package) for e in binding.inputs.entries if e.role=='s3.role.'+name)
        try:
            if selected==OPS[0]:
                view=resolver.view(p['package_id']);data=resolver.payload(p['closure'],pid,context.read.registry.payloads)
                dependencies=tuple(resolver.view(ref['package_id']) for ref in data['dependencies'])
                audience=api.AudienceClosure(data['audience'],tuple(data['members']),dependencies,data['policy'],tuple(data['checks']))
                result=self.publish(p['publication_id'],view.source_bytes,p['package_id'],p['digest'],audience,grants,issue_token,context)
            elif selected==OPS[1]:result=self.lookup_commit(p['publication_id'],p['package_id'],p['digest'],grants,issue_token,context)
            elif selected==OPS[2]:
                ref=role('selection');view=resolver.view(ref['package_id']);receipt_ref=role('committed_receipt');receipt,rpid=resolver.record(receipt_ref,pid)
                value=receipt['payload'];commit=api.PublicationReceipt(receipt_ref,value['subject_package'],value['digest']['value'],value['commit_status'])
                selection=api.PinnedSelection(ref,view,commit)
                result=self.cas_pointer(p['namespace'],p['name'],p['expected_revision'],selection,grants,issue_token,context)
            else:
                ref=role('subject');view=resolver.view(ref['package_id']);record,_=resolver.record(ref,pid)
                from crucis_causal.connections.validation import content_bytes
                if record['record_type']!='s1.artifact_snapshot':raise ExecutionError('s3.local_snapshot_subject_required')
                subject=api.PinnedArtifactIdentity(ref,digest(content_bytes(record['payload']['content'])),{'state':'not_applicable','rule':contract('s3.whole_artifact'),'scope':[]},view)
                if selected==OPS[3]:result=self.locate(subject,p['locator'],p['expected_digest'],grants,issue_token,context)
                else:
                    data=resolver.payload(p['scope' if selected==OPS[4] else 'copy_scope'],pid,context.read.registry.payloads)
                    if selected==OPS[4]:
                        selected_scope=api.AccessScope(data['owner'],tuple(data['copies']),(data['rule'],),subject)
                        result=self.revoke(subject,selected_scope,grants,issue_token,context)
                    else:
                        selected_scope=api.CopyRetentionScope(data['owner'],tuple(data['copies']),data['rule'],subject)
                        result=self.delete(subject,selected_scope,grants,issue_token,context)
            return self._as_evidence(result,request,issue_token,context)
        except ExecutionError as exc:return api.rejected(exc.code)

    def _as_evidence(self,result,request,token,context):
        if isinstance(result.value,api.DriverEvidence) or result.state=='rejected':return result
        if isinstance(result.value,api.PublicationReceipt):
            delta=result.records;receipts=index([result.value.receipt])
        else:
            value=result.value
            data={'state':value.state,'package_id':value.package_id,'digest':value.digest} if isinstance(value,api.CommitLookup) else {'namespace':value.namespace,'name':value.name,'previous_revision':value.previous_revision,'current_revision':value.current_revision,'selection':value.selection.reference}
            b=Builder('Exact local storage response');ref,storage=typed_document(b,contract('s3.local_storage_response'),data)
            root=root_of(request.source_view,codec.Resolver(context.read.views,limits=self.limits))
            projection=b.add('projection_view',{'view_role':'audience_projection','audience':qualified(root['audience'],request.source_view.package_id),'projection_contract':contract('s3.local_storage_response'),'members':index([ref]),'claims':index(),'limits':index()})
            from .coordinator import read_with
            read=read_with(context.read,*result.records.dependencies,storage,token.intent_commit.head.snapshot);view=frozen(b,projection,read)
            delta=api.RecordDelta((*result.records.records,*view.records),(),(*read.views,view));receipts=index([qualified(ref,view.package_id)])
        evidence=api.DriverEvidence(reference(request.binding.record['id'],'operation_binding',request.binding.context['package_id']),delta,index(),receipts,index(),())
        return api.CallResult(result.state,evidence,records=delta,issues=result.issues,effects=(api.EffectBoundary(token.command,'crossed',known(True),tuple(receipts['members']),token.transmission),))

    def _control(self,context):self.authority.check(context.control,{'store':self.namespace,'component':self.component})

    @staticmethod
    def _fault(context,label):
        if context.fault:context.fault(label)

    def _binding(self,selected,grants,token,context,parameters,subjects=()):
        self._control(context);_verify_implementation(self.implementation)
        if any(not context.read.access.permits(v.package_id) for v in context.read.views):raise ExecutionError('s3.read_denied')
        if not isinstance(token,api.IssueToken):raise ExecutionError('s3.actual_issue_token_required')
        resolver=codec.Resolver((*context.read.views,token.intent_commit.head.snapshot),limits=self.limits)
        command,pid=resolver.record(token.command,token.command.get('package_id',token.intent_commit.head.snapshot.package_id))
        if command['record_type']!='s3.effect_command' or command['payload']['operation']!=selected:raise ExecutionError('s3.storage_operation_mismatch')
        binding=resolve_binding(command['payload']['binding'],pid,resolver)
        if binding_digest(binding)!=token.binding_digest:raise ExecutionError('s3.storage_binding_mismatch')
        p={p['key']:p['value'] for p in binding.record['payload']['parameters']}
        if any(k not in p or p[k]['state']!='known' or p[k]['value']!=value for k,value in parameters.items()):raise ExecutionError('s3.storage_parameter_mismatch')
        for role,ref in subjects:
            actual=[e for e in binding.inputs.entries if e.role=='s3.role.'+role]
            record,rpid=resolver.record(ref,ref.get('package_id',pid))
            if len(actual)!=1 or actual[0].source_package!=rpid or canonical(actual[0].record)!=canonical(record):raise ExecutionError('s3.storage_subject_mismatch')
        d,dpid=resolver.record(token.transmission,token.transmission.get('package_id',pid))
        receiver,rpid=resolver.record(d['payload']['recipient'],dpid);expected,epid=resolver.record(self.component,self.component['package_id'])
        if d['payload']['command']['target']!=command['id'] or d['payload']['channel']!=BACKEND or canonical(receiver)!=canonical(expected) or rpid!=epid:raise ExecutionError('s3.storage_recipient_mismatch')
        dependencies=[resolver.record(r,pid)[0] for r in command['payload']['dependencies']['members']]
        code,_=resolver.record(self.implementation.reference,self.implementation.source_view.package_id)
        if expected not in dependencies or code not in dependencies:raise ExecutionError('s3.storage_implementation_not_pinned')
        if len(grants)!=len(self.owners):raise ExecutionError('s3.owner_group_incomplete')
        for (owner,owner_context),grant in zip(self.owners,grants):
            result=owner.check(grant,binding,selected,owner_context)
            if result.state!='completed' or result.value.decision!='permitted' or result.value.binding_digest!=token.binding_digest:raise ExecutionError('s3.owner_group_not_current')
        return binding,resolver,p

    def _enter(self,token):self.journal.consume(token,self.jctx)

    def _receipt(self,package_id,expected_digest,audience,token,context):
        b=Builder('Publication commit receipt outside the frozen subject')
        ref=b.add('publication_receipt',{'subject_package':package_id,'subject_format':contract('account_package'),'digest':known(expected_digest),
            'audience':audience,'operation':token.command,'commit_status':'committed','checks':index(),'basis':[token.transmission]})
        from .model import unknown_ref
        private=b.add('audience',{'purpose':contract('s3.private_publication_receipt'),'recipients':index(),'disclosure_policy':unknown_ref('s1.policy'),'authority':unknown()})
        projection=b.add('projection_view',{'view_role':'audience_projection','audience':private,'projection_contract':contract('s3.publication_commit_receipt'),
            'members':index([ref]),'claims':index(),'limits':index()})
        from .coordinator import read_with
        read=read_with(context.read,token.intent_commit.head.snapshot)
        view=frozen(b,projection,read)
        return qualified(ref,view.package_id),view,read.views

    def publish(self,publication_id,bytes,expected_id,expected_digest,audience,grants,issue_token,context):
        crossed=False
        try:
            validate_value(publication_id,'ID');validate_value(expected_id,'ID');validate_value(expected_digest,'Digest')
            if not isinstance(bytes,builtins.bytes) or digest(bytes)!=expected_digest:raise ExecutionError('s3.publication_digest_mismatch')
            view=codec.parse_snapshot(bytes,self.limits)
            if view.package_id!=expected_id:raise ExecutionError('s3.publication_identity_mismatch')
            binding,resolver,p=self._binding(OPS[0],grants,issue_token,context,{'publication_id':publication_id,'package_id':expected_id,'digest':expected_digest,'backend':BACKEND},[('view',view.package['roots'][0] | {'binding':'external','package_id':view.package_id}),('audience',audience.audience)])
            declared=resolver.payload(p['closure']['value'],binding.context['package_id'],context.read.registry.payloads)
            expected={'audience':audience.audience,'members':list(audience.allowed_records),'dependencies':[v.package['roots'][0]|{'binding':'external','package_id':v.package_id} for v in audience.allowed_dependencies],
                'policy':audience.policy,'checks':list(audience.checks)}
            if declared!=expected:raise ExecutionError('s3.audience_closure_binding_mismatch')
            validate_audience(view,audience,resolver,context.read.registry.payloads)
            publication_binding=canonical({'package_id':expected_id,'digest':expected_digest,'closure':expected})
            self._enter(issue_token);crossed=True
            for dependency in audience.allowed_dependencies:self.artifacts.stage(dependency.source_bytes)
            self.artifacts.stage(bytes);self._fault(context,'publication_after_stage')
            with self._db() as db:
                db.execute('BEGIN IMMEDIATE');old=db.execute('SELECT * FROM publications WHERE id=?',(publication_id,)).fetchone()
                if old:
                    if old['package']!=expected_id or json.loads(old['digest'])!=expected_digest or builtins.bytes(old['binding'])!=publication_binding:raise ExecutionError('s3.publication_correlation_conflict')
                    ref=json.loads(old['receipt']);receipt_view=codec.parse_snapshot(builtins.bytes(old['view']),self.limits)
                    receipt_dependencies=tuple(codec.parse_snapshot(builtins.bytes(r['data']),self.limits) for r in db.execute('SELECT data FROM receipt_dependencies'))
                else:
                    ref,receipt_view,receipt_dependencies=self._receipt(expected_id,expected_digest,audience.audience,issue_token,context)
                    for dependency in receipt_dependencies:
                        previous=db.execute('SELECT data FROM receipt_dependencies WHERE id=?',(dependency.package_id,)).fetchone()
                        if previous and builtins.bytes(previous[0])!=dependency.source_bytes:raise ExecutionError('s3.package_identity_conflict')
                        self.artifacts.stage(dependency.source_bytes)
                        db.execute('INSERT OR IGNORE INTO receipt_dependencies VALUES(?,?)',(dependency.package_id,dependency.source_bytes))
                    db.execute('INSERT INTO publications VALUES(?,?,?,?,?,?)',(publication_id,expected_id,canonical(expected_digest),publication_binding,canonical(ref),receipt_view.source_bytes))
                self._fault(context,'publication_before_commit');db.execute('COMMIT');self._fault(context,'publication_after_commit')
            value=api.PublicationReceipt(ref,expected_id,expected_digest,'committed')
            return api.CallResult('completed',value,records=api.RecordDelta(receipt_view.records,(),(*receipt_dependencies,receipt_view)))
        except ExecutionError as exc:return api.rejected(exc.code,effects=self._effects(issue_token,crossed))
        except Exception:return api.rejected('s3.publication_commit_unconfirmed',effects=self._effects(issue_token,crossed))

    @staticmethod
    def _effects(token,crossed):
        return (api.EffectBoundary(token.command,'may_have_crossed' if crossed else 'not_crossed',unknown('s3.storage_effect_unconfirmed'),(),token.transmission),) if isinstance(token,api.IssueToken) else ()

    def lookup_commit(self,publication_id,package_id,expected_digest,grants,issue_token,context):
        crossed=False
        try:
            binding,resolver,p=self._binding(OPS[1],grants,issue_token,context,{'publication_id':publication_id,'package_id':package_id,'digest':expected_digest})
            original=next(e for e in binding.inputs.entries if e.role=='s3.role.command')
            if original.record['payload']['operation']!=OPS[0]:raise ExecutionError('s3.original_publication_command_required')
            old=resolve_binding(original.record['payload']['binding'],original.source_package,resolver)
            values={p['key']:p['value'] for p in old.record['payload']['parameters']}
            if any(values[k]['value']!=v for k,v in [('publication_id',publication_id),('package_id',package_id),('digest',expected_digest)]):raise ExecutionError('s3.publication_correlation_conflict')
            self._enter(issue_token);crossed=True
            with self._db() as db:
                row=db.execute('SELECT * FROM publications WHERE id=?',(publication_id,)).fetchone()
                dependencies=tuple(codec.parse_snapshot(builtins.bytes(r['data']),self.limits) for r in db.execute('SELECT data FROM receipt_dependencies'))
            if row is None:return api.CallResult('completed',api.CommitLookup('not_committed',package_id,expected_digest,api.RecordDelta()))
            if row['package']!=package_id or json.loads(row['digest'])!=expected_digest:raise ExecutionError('s3.publication_correlation_conflict')
            self.artifacts.read(expected_digest)
            v=codec.parse_snapshot(builtins.bytes(row['view']),self.limits);delta=api.RecordDelta(v.records,(),(*dependencies,v))
            return api.CallResult('completed',api.CommitLookup('committed',package_id,expected_digest,delta),records=delta)
        except ExecutionError as exc:return api.rejected(exc.code,effects=self._effects(issue_token,crossed))
        except Exception:return api.CallResult('partial',api.CommitLookup('unknown',package_id,expected_digest,api.RecordDelta()),issues=(api.Issue('s3.publication_lookup_unconfirmed',scope(),()),))

    def cas_pointer(self,namespace,name,expected_revision,committed_selection,grants,issue_token,context):
        crossed=False
        try:
            validate_value(namespace,'ID');validate_value(name,'String');validate_value(expected_revision,'Index')
            if namespace!=self.namespace or not name:raise ExecutionError('s3.actual_pointer_namespace_required')
            if not isinstance(committed_selection,api.PinnedSelection) or committed_selection.commit_receipt.commit_state!='committed':raise ExecutionError('s3.committed_selection_required')
            v=committed_selection.source_view;receipt=committed_selection.commit_receipt
            if receipt.package_id!=v.package_id or receipt.digest!=v.digest:raise ExecutionError('s3.selection_commit_mismatch')
            binding,resolver,p=self._binding(OPS[2],grants,issue_token,context,{'namespace':namespace,'name':name,'expected_revision':expected_revision,'selection_digest':v.digest},[('selection',committed_selection.reference),('committed_receipt',receipt.receipt)])
            with self._db() as db:
                published=db.execute('SELECT * FROM publications WHERE package=? AND digest=?',(v.package_id,canonical(v.digest))).fetchone()
            if published is None:raise ExecutionError('s3.selection_not_committed_here')
            stored_ref=json.loads(published['receipt'])
            stored_view=codec.parse_snapshot(builtins.bytes(published['view']),self.limits)
            expected=next(r for r in stored_view.records if r['id']==stored_ref['target'])
            actual,_=resolver.record(receipt.receipt,receipt.receipt['package_id'])
            if canonical(actual)!=canonical(expected):raise ExecutionError('s3.selection_commit_receipt_mismatch')
            self._enter(issue_token);crossed=True
            with self._db() as db:
                db.execute('BEGIN IMMEDIATE');row=db.execute('SELECT * FROM pointers WHERE namespace=? AND name=?',(namespace,name)).fetchone();revision=row['revision'] if row else 0
                if revision!=int(expected_revision):raise ExecutionError('s3.pointer_revision_conflict')
                next_revision=revision+1
                db.execute('INSERT INTO pointers VALUES(?,?,?,?) ON CONFLICT(namespace,name) DO UPDATE SET revision=excluded.revision,selection=excluded.selection',(namespace,name,next_revision,canonical(committed_selection.reference)))
                db.execute('COMMIT');self._fault(context,'pointer_after_commit')
            return api.CallResult('completed',api.PointerReceipt(namespace,name,expected_revision,str(next_revision),committed_selection,api.RecordDelta()))
        except ExecutionError as exc:return api.rejected(exc.code,effects=self._effects(issue_token,crossed))
        except Exception:return api.rejected('s3.pointer_update_unconfirmed',effects=self._effects(issue_token,crossed))

    def install_copy(self,copy_id,data,context):
        """Explicit actual owner provisioning, not implicit locator fetching."""
        self._control(context);validate_value(copy_id,'ID');bound=digest(data)
        path=self.copies/copy_id
        with self._db() as db:old=db.execute('SELECT * FROM copies WHERE id=?',(copy_id,)).fetchone()
        if old:
            if json.loads(old['digest'])!=bound:raise ExecutionError('s3.copy_identity_conflict')
            if not old['retained'] or not old['access']:raise ExecutionError('s3.copy_lifecycle_closed')
            if not path.is_file():raise ExecutionError('s3.copy_presence_unconfirmed')
        self.artifacts.stage(data)
        if path.exists():
            if path.read_bytes()!=data:raise ExecutionError('s3.copy_identity_conflict')
        else:os.link(self.artifacts._path(bound['value']),path)
        with self._db() as db:
            old=db.execute('SELECT digest FROM copies WHERE id=?',(copy_id,)).fetchone()
            if old and json.loads(old[0])!=bound:raise ExecutionError('s3.copy_identity_conflict')
            db.execute('INSERT OR IGNORE INTO copies VALUES(?,?,1,1)',(copy_id,canonical(bound)))
        return bound

    def _subject(self,subject,context):
        if not isinstance(subject,api.PinnedArtifactIdentity):raise ExecutionError('s3.pinned_artifact_required')
        if any(not context.read.access.permits(v.package_id) for v in context.read.views):raise ExecutionError('s3.read_denied')
        from crucis_causal.connections.validation import content_bytes
        resolver=codec.Resolver(context.read.views,limits=self.limits);record,pid=resolver.record(subject.reference,subject.source_view.package_id)
        if resolver.view(pid).source_bytes!=subject.source_view.source_bytes or subject.selector['state']!='not_applicable':raise ExecutionError('s3.storage_whole_subject_required')
        if record['record_type']=='s1.artifact_snapshot' and digest(content_bytes(record['payload']['content']))!=subject.content_digest:raise ExecutionError('s3.storage_subject_digest_mismatch')
        return subject.content_digest

    def _evidence(self,selected,subject,data,token,context):
        b=Builder('Scoped local copy operation evidence, not global erasure')
        ref,storage=typed_document(b,selected,data)
        # The private receipt names unknown copies explicitly; no earlier
        # evidence record or publication is rewritten after revoke/delete.
        obligation=b.add('obligation',{'question':contract('s3.other_copies_and_prior_exposure'),'scope':scope(subject.reference),
            'owner':self.component,'disposition':'unresolved','basis':[ref],'follow_up':index(extent='unresolved')})
        ar=next(reference(r['id'],'audience',v.package_id) for v in context.read.views for r in v.records if r['record_type']=='s3.audience')
        root=b.add('projection_view',{'view_role':'audience_projection','audience':ar,'projection_contract':selected,'members':index([ref,obligation]),'claims':index(),'limits':index()})
        from .coordinator import read_with
        read=read_with(context.read,storage,token.intent_commit.head.snapshot);view=frozen(b,root,read)
        delta=api.RecordDelta(view.records,(),(*read.views,view));evidence=api.DriverEvidence(reference(resolve_binding_ref(token,read)['target'],'operation_binding',resolve_binding_ref(token,read)['package_id']),delta,index(),index([qualified(ref,view.package_id)]),index(),())
        return api.CallResult('completed',evidence,records=delta)

    def locate(self,subject,locator,expected_digest,grants,issue_token,context):
        crossed=False
        try:
            bound=self._subject(subject,context)
            if bound!=expected_digest:raise ExecutionError('s3.locator_does_not_repin_subject')
            validate_value(locator,'ID')
            self._binding(OPS[3],grants,issue_token,context,{'locator':locator,'retrieval_contract':contract('s3.local_copy_lookup'),'expected_digest':expected_digest},[('subject',subject.reference)])
            self._enter(issue_token);crossed=True
            with self._db() as db:row=db.execute('SELECT * FROM copies WHERE id=?',(locator,)).fetchone()
            available=bool(row and row['access'] and row['retained'] and json.loads(row['digest'])==expected_digest and (self.copies/locator).is_file())
            if available and digest((self.copies/locator).read_bytes())!=expected_digest:raise ExecutionError('s3.copy_integrity_mismatch')
            return self._evidence(contract('s3.local_copy_availability'),subject,{'copy':locator,'available':available,'expected_digest':expected_digest},issue_token,context)
        except ExecutionError as exc:return api.rejected(exc.code,effects=self._effects(issue_token,crossed))
        except Exception:return api.rejected('s3.copy_availability_unconfirmed',effects=self._effects(issue_token,crossed))

    def revoke(self,subject,scope,grants,issue_token,context):
        return self._copy_effect('revoke',subject,scope,grants,issue_token,context)

    def delete(self,subject,scope,grants,issue_token,context):
        return self._copy_effect('delete',subject,scope,grants,issue_token,context)

    def _copy_effect(self,method,subject,selected,grants,token,context):
        crossed=False
        try:
            bound=self._subject(subject,context)
            if selected.owner!=self.component or selected.subject!=subject:raise ExecutionError('s3.copy_owner_scope_mismatch')
            if method=='revoke' and selected.rights!=(contract('s3.local_copy_only'),):raise ExecutionError('s3.copy_scope_uninterpreted')
            if method=='delete' and selected.retention_rule!=contract('s3.local_copy_only'):raise ExecutionError('s3.copy_scope_uninterpreted')
            op=OPS[4] if method=='revoke' else OPS[5]
            binding,resolver,p=self._binding(op,grants,token,context,{},[('subject',subject.reference),('owner',self.component)])
            grammar='s3.local_access_scope' if method=='revoke' else 's3.local_copy_retention_scope'
            field='scope' if method=='revoke' else 'copy_scope'
            row,pid=resolver.record(p[field]['value'],binding.context['package_id'])
            if row['payload']['payload_contract']!=contract(grammar):raise ExecutionError('s3.copy_scope_uninterpreted')
            raw=resolver.payload(p[field]['value'],binding.context['package_id'],context.read.registry.payloads)
            expected={'owner':selected.owner,'subject':selected.subject.reference,'copies':list(selected.recipients if method=='revoke' else selected.copies),
                'rule':contract('s3.local_copy_only') if method=='revoke' else selected.retention_rule}
            if raw!=expected or p['revocation_rule' if method=='revoke' else 'retention_rule']['value']!=contract('s3.local_copy_only'):raise ExecutionError('s3.copy_scope_uninterpreted')
            copies=raw['copies']
            if not copies:raise ExecutionError('s3.explicit_copy_scope_required')
            ids=[]
            for ref in copies:
                record,rpid=resolver.record(ref,binding.context['package_id'])
                if record['record_type']!='s1.location':raise ExecutionError('s3.local_copy_location_required')
                ids.append(record['payload']['locator'])
            for copy_id in ids:validate_value(copy_id,'ID')
            if len(ids)!=len(set(ids)):raise ExecutionError('s3.unique_copy_scope_required')
            with self._db() as db:
                for copy_id in ids:
                    row=db.execute('SELECT * FROM copies WHERE id=?',(copy_id,)).fetchone()
                    if row is None or json.loads(row['digest'])!=bound:raise ExecutionError('s3.copy_owner_scope_mismatch')
            self._enter(token);crossed=True
            with self._db() as db:
                db.execute('BEGIN IMMEDIATE')
                if method=='delete':
                    for copy_id in ids:
                        self._fault(context,'copy_before_unlink')
                        (self.copies/copy_id).unlink(missing_ok=True)
                        self._fault(context,'copy_after_unlink')
                for copy_id in ids:db.execute('UPDATE copies SET '+('access=0' if method=='revoke' else 'retained=0')+' WHERE id=?',(copy_id,))
                db.execute('COMMIT');self._fault(context,'copy_after_'+method+'_commit')
            return self._evidence(contract('s3.local_copy_'+method),subject,{'copies':ids,'local_access_revoked':method=='revoke','local_copy_deleted':method=='delete','other_copies':unknown(),'prior_exposure_erased':False},token,context)
        except ExecutionError as exc:return api.rejected(exc.code,effects=self._effects(token,crossed))
        except Exception:return api.rejected('s3.copy_effect_unconfirmed',effects=self._effects(token,crossed))


def resolve_binding_ref(token,read):
    resolver=codec.Resolver((*read.views,token.intent_commit.head.snapshot),limits=read.limits)
    command,pid=resolver.record(token.command,token.command['package_id'])
    return qualified(command['payload']['binding'],pid)
