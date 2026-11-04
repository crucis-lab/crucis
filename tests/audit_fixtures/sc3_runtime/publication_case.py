"""Explicit local fixture owner/authority; no provider or default publication."""
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
import base64
import dispatch_case as case
from crucis_causal.execution import api,codec
from crucis_causal.execution.clock import WallClock
from crucis_causal.execution.coordinator import AdmissionRule,Coordinator,OwnerAllocation,read_with
from crucis_causal.execution.journal import Journal
from crucis_causal.execution.model import (Builder,ExecutionError,canonical,contract,digest,identity,index,known,
    not_applicable,qualified,reference,scope,unknown,unknown_ref)
from crucis_causal.execution.owners import LocalOwner
from crucis_causal.execution.publication import LocalPublicationStore,OPS,BACKEND
from crucis_causal.execution.projection import AudiencePolicies,AudienceRule
from crucis_causal.execution.registry import (SuppliedRegistryContext,ExactDriverRegistry,ExactDecisionRegistry,PayloadRegistry,supplied_callable)
from crucis_causal.connections.model import Builder as B1,contract as c1,source as s1source
from crucis_causal.connections.evidence import capture_bytes

POLICY=contract('s3.fixture.exact_public_bytes')


def exact_permission(view,audience,claims,context):
    resolver=codec.Resolver(context.views,limits=context.limits);closure=resolver.closure(view.package_id)
    records=tuple(reference(r['id'],r['record_type'],v.package_id) for v in closure for r in v.records)
    # Explicit fixture policy permits every producer, policy and diagnostic byte
    # in this exact supplied subject. This is not a generic public-data classifier.
    return api.CallResult('completed',api.AudienceClosure(audience,records,tuple(v for v in closure if v.package_id!=view.package_id),POLICY,()))


class Environment(case.Environment):
    def __init__(self,root):
        super().__init__(root,SimpleNamespace(namespace='no_native_provider',epoch='0'),scientific_path=None,native_operations=OPS)
        self.store_fault=None
        self.store=LocalPublicationStore(self.root/'publications',self.component,self.pin,self.journal,self.jctx,((self.owner,self.octx),))
        self.store_control=self.store.control();self.store.install(self.registry)
        self.coordinator.audience_policies=AudiencePolicies((AudienceRule(POLICY,self.pin,supplied_callable(exact_permission)),))
        self.context=replace(self.context,storage=self.store)

    def admit(self,plan,*,group=None):
        actual,_,_=self.coordinator._actual(plan,self.context.read)
        self.octx=replace(self.octx,read=read_with(self.octx.read,*self.context.read.views))
        observed=self.owner.inspect(actual,self.octx)
        if observed.state!='completed':raise AssertionError(observed.issues)
        self.include(*observed.value.evidence.dependencies)
        allocation=OwnerAllocation('native_owner',self.owner,self.octx,self.amounts('0'),contract('s3.owner.same_request_exact_replay'),observed.value.revision['value'])
        runtime=api.RuntimeContext(self.context.read,self.store_control,fault=self.store_fault)
        cap=self.coordinator.bind(self.journal,self.jctx,self.store,(allocation,),('native_owner',),runtime,runtime,not_applicable('s3.no_absolute_deadline'),None)
        self.context=replace(self.context,control_capability=cap)
        return self.coordinator.admit(plan,self.journal.head(self.account,self.jctx).value,self.context,group or identity())

    def operation_amounts(self,actual):return self.amounts('0')

    def target(self,*,label='two-public-entities',opaque=False):
        b1=B1('Explicit fixture disclosure policy, public exact bytes')
        policy=b1.add('policy',{'policy_contract':POLICY,'parameters':[],'scope':scope(),'authority':unknown(),'source':s1source('reported')})
        extra=[]
        if opaque:
            raw=capture_bytes(b1,b'{"unknown_native_semantics":true}',format_contract=c1('json'));extra.append(raw)
        source=case.input_case.snapshot1(b1,[policy,*extra]);self.include(source)
        b=Builder('Explicitly permitted public fixture metadata')
        audience=b.add('audience',{'purpose':contract('s3.fixture.public_evidence'),'recipients':index(),'disclosure_policy':qualified(policy,source.package_id),'authority':unknown()})
        one=b.add('diagnostic',{'code':'s3.fixture.entity_one','scope':scope(),'details':'Public entity A','evidence':[]})
        two=b.add('diagnostic',{'code':'s3.fixture.entity_two','scope':scope(),'details':'Public entity B','evidence':[]})
        members=[one,two]
        if opaque:members.append(b.add('typed_payload',{'payload_contract':contract('s3.fixture.unknown_native'),'content':{'artifact':qualified(raw,source.package_id),'selector':not_applicable()},'reference_context':{'package_id':b.package_id,'format':contract('account_package')}}))
        root=b.add('projection_view',{'view_role':'audience_projection','audience':audience,'projection_contract':contract('s3.fixture.public_projection'),'members':index(members),'claims':index(),'limits':index()})
        view=case.frame(b,root,(source,));self.include(view)
        return view,qualified(audience,view.package_id)

    def freeze(self,view,audience,claims=()):return self.coordinator.freeze(view,audience,claims,self.context.read)

    def publish_request(self,draft,publication_id=None):
        a=draft.audience
        closure={'audience':a.audience,'members':list(a.allowed_records),'dependencies':[qualified(v.package['roots'][0],v.package_id) for v in a.allowed_dependencies],'policy':a.policy,'checks':list(a.checks)}
        ref,views=case.document(contract('s3.payload.audience_closure'),closure,self.context.read.views);self.include(*views)
        root=codec.parse_snapshot(draft.bytes,case.L).package['roots'][0]
        roles=tuple({'role':'s3.role.'+k,'members':index(refs)} for k,refs in [('view',[qualified(root,draft.package_id)]),('audience',[a.audience]),('checks',[])])
        values={'publication_id':known(publication_id or identity()),'package_id':known(draft.package_id),'digest':known(draft.digest),'backend':known(BACKEND),'closure':known(ref)}
        return api.OperationRequest(OPS[0],roles,tuple({'key':k,'value':v} for k,v in values.items()),identity())

    def lookup_request(self,original,draft,publication_id):
        return api.OperationRequest(OPS[1],({'role':'s3.role.command','members':index([original])},),
            tuple({'key':k,'value':known(v)} for k,v in [('publication_id',publication_id),('package_id',draft.package_id),('digest',draft.digest)]),identity())

    def pointer_request(self,view,receipt,revision):
        roles=({'role':'s3.role.selection','members':index([qualified(view.package['roots'][0],view.package_id)])},{'role':'s3.role.committed_receipt','members':index([receipt])})
        p={'namespace':self.store.namespace,'name':'current','expected_revision':revision,'selection_digest':view.digest}
        return api.OperationRequest(OPS[2],roles,tuple({'key':k,'value':known(v)} for k,v in p.items()),identity())

    def artifact(self,data=b'Explicit owned copy bytes'):
        b=B1('Named local copies retain original snapshot identity');artifact=capture_bytes(b,data,format_contract=c1('octets'));copy_id=identity()
        location=b.add('location',{'locator':copy_id,'access_contract':c1('explicit_local_fixture'),'expected_snapshot':artifact,'retrievals':[],'automatic_access':False})
        v=case.input_case.snapshot1(b,[artifact,location]);self.include(v)
        subject=api.PinnedArtifactIdentity(qualified(artifact,v.package_id),digest(data),not_applicable(),v)
        self.store.install_copy(copy_id,data,api.RuntimeContext(self.context.read,self.store_control))
        return subject,qualified(location,v.package_id),copy_id

    def locate_request(self,subject,copy_id,*,expected_digest=None):
        p={'locator':copy_id,'retrieval_contract':contract('s3.local_copy_lookup'),'expected_digest':expected_digest or subject.content_digest}
        return api.OperationRequest(OPS[3],({'role':'s3.role.subject','members':index([subject.reference])},),tuple({'key':k,'value':known(v)} for k,v in p.items()),identity())

    def copy_request(self,method,subject,location,*,owner=None):
        owner=owner or self.component
        data={'owner':owner,'subject':subject.reference,'copies':[location],'rule':contract('s3.local_copy_only')}
        selected=contract('s3.local_access_scope' if method=='revoke' else 's3.local_copy_retention_scope')
        ref,views=case.document(selected,data,self.context.read.views);self.include(*views)
        p={'scope':ref,'revocation_rule':contract('s3.local_copy_only')} if method=='revoke' else {'copy_scope':ref,'retention_rule':contract('s3.local_copy_only')}
        roles=tuple({'role':'s3.role.'+k,'members':index([v])} for k,v in [('subject',subject.reference),('owner',owner)])
        return api.OperationRequest(OPS[4] if method=='revoke' else OPS[5],roles,tuple({'key':k,'value':known(v)} for k,v in p.items()),identity())


def packet(env,plan,group,d):
    p=env.pin
    return {'root':str(env.root),'component':env.component,'account':env.account,'allocation':env.allocation,
        'command':plan.command,'source':plan.source_view.package_id,'group':group,'transmission':d,'view':env.view.package_id,
        'pin':{'reference':p.reference,'content_digest':p.content_digest,'selector':p.selector,'source':p.source_view.package_id},
        'views':[base64.b64encode(v.source_bytes).decode() for v in plan.dependencies.views]}


def reopen(value,*,fault=None):
    env=object.__new__(Environment);env.root=Path(value['root']);env.fault=None;env.store_fault=fault
    env.client=SimpleNamespace(namespace='no_native_provider',epoch='0');env.mechanics=case.Mechanics(value['component'],env.client)
    env.component=value['component'];env.account=value['account'];env.allocation=value['allocation'];env.launch_roles=None
    views=tuple(codec.parse_snapshot(base64.b64decode(raw),case.L) for raw in value['views']);resolver=codec.Resolver(views,limits=case.L)
    p=value['pin'];env.pin=api.PinnedArtifactIdentity(p['reference'],p['content_digest'],p['selector'],resolver.view(p['source']));env.view=resolver.view(value['view'])
    env.registry=SuppliedRegistryContext(ExactDriverRegistry(),ExactDecisionRegistry(),PayloadRegistry())
    read=api.PinnedReadContext(views,api.supplied_read(v.package_id for v in views),env.registry,case.L)
    env.journal=Journal(env.root/'journal');env.jctx=api.RuntimeContext(read,env.journal.control(env.account));h=env.journal.head(env.account,env.jctx)
    read=read_with(read,*h.records.dependencies,h.value.snapshot)
    env.owner=LocalOwner(env.root/'owner',{'s3.fixture_work':{'unit':contract('fixture_unit'),'capacity':case.number('20')}},native_operations=OPS,ttl_ns='300000000000')
    env.octx=api.RuntimeContext(read,env.owner.control(env.allocation,max_calls='1000'))
    env.store=LocalPublicationStore(env.root/'publications',env.component,env.pin,env.journal,env.jctx,((env.owner,env.octx),));env.store_control=env.store.control();env.store.install(env.registry)
    env.coordinator=Coordinator((AdmissionRule(contract('s3.fixture.native_profile'),OPS,env.pin,supplied_callable(case.eligible)),),audience_policies=AudiencePolicies((AudienceRule(POLICY,env.pin,supplied_callable(exact_permission)),)))
    runtime=api.RuntimeContext(read,env.store_control,fault=fault);allocation=OwnerAllocation('native_owner',env.owner,env.octx,env.amounts('0'),contract('s3.owner.same_request_exact_replay'),'0')
    cap=env.coordinator.bind(env.journal,env.jctx,env.store,(allocation,),('native_owner',),runtime,runtime,not_applicable('s3.no_absolute_deadline'),None)
    env.context=api.CoordinatorContext(read,env.journal,env.store,{'native_owner':env.owner},env.registry.drivers,env.registry.decisions,cap,WallClock(),case.L)
    result=env.coordinator.restore_prepared(value['command'],resolver.view(value['source']),read)
    if result.state!='completed':raise AssertionError(result.issues)
    return env,result.value
