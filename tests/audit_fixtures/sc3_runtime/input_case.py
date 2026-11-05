"""Independently fixed B05 input/guard fixture, not a scientific experiment.

The manually stated oracle is distinct from the provider's CSV implementation.
No discovery request/run binding is invented to admit preparation.
"""
import copy
import csv
from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
from crucis_causal.execution import api,codec
from crucis_causal.execution.authority import DriverBoundary
from crucis_causal.execution.inputs import InputDriver,Realizer,RealizationProduct
from crucis_causal.execution.journal import Journal,resolve_binding,binding_digest
from crucis_causal.execution.model import (Builder,canonical,contract,digest,identity,index,known,
    not_applicable,qualified,reference,scope,unknown,unknown_ref)
from crucis_causal.execution.owners import LocalOwner,persist_owner_requests
from crucis_causal.execution.registry import supplied_callable
from crucis_causal.execution.staging import LocalCustodian,EndpointOwner

SOURCE=b'A,B,C\n0,1,0\n1,0,1\n'
EXPECTED=b'v0,v1,v2\n0,0,1\n1,1,0\n'
FIT_EXPECTED=b'v0,v1,v2\n0,-1,1\n1,0,0\n'
L=api.Limits()

def snapshot1(builder,roots,dependencies=()):
    from crucis_causal.connections.codec import dumps
    return codec.parse_snapshot(dumps(builder.package(roots,external_packages=[{'package_id':v.package_id,
        'locator':unknown(),'expected_digest':known(v.digest),'access':'s1.supplied_metadata'} for v in dependencies])),L)

def pin():
    from crucis_causal.connections.model import Builder as B1,contract as c1
    from crucis_causal.connections.evidence import capture_bytes
    root=Path(__file__).resolve().parents[3]
    directory=root/'crucis_causal/execution'
    files=[p for p in sorted(directory.iterdir()) if p.suffix in ('.py','.json')]
    identities={'execution/'+p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    identities['fixture/input_case.py']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    identities['test/test_audit_execution_inputs.py']=hashlib.sha256((root/'tests/test_audit_execution_inputs.py').read_bytes()).hexdigest()
    raw=canonical(identities)
    b=B1('Actual B05 fixture/code manifest');ref=capture_bytes(b,raw,format_contract=c1('code_identity_manifest'))
    view=snapshot1(b,[ref]);return api.PinnedArtifactIdentity(qualified(ref,view.package_id),digest(raw),not_applicable(),view)

def frame(builder,root,deps):return codec.parse_snapshot(codec.dumps(builder.package(root,deps),L),L)

def metadata():
    from crucis_causal.connections.model import Builder as B1,contract as c1
    from crucis_causal.connections.evidence import capture_bytes
    from crucis_causal.connections.domains import finite_domain,permutation
    from crucis_causal.experiments import api as a2
    from crucis_causal.experiments.model import contract as c2,source as s2
    from crucis_causal.experiments.writer import S2RecordWriter
    from crucis_causal.experiments.resolver import PlanResolver,ReadAccess
    b=B1('Prospective preparation source/representation')
    data=capture_bytes(b,SOURCE,format_contract=c1('csv'));domain=finite_domain(b,['A','B','C']);shown=finite_domain(b,['v0','v1','v2'])
    mapping=permutation(b,domain,shown,[('0','1'),('1','2'),('2','0')],evidence=[data])
    source=snapshot1(b,[data,domain,shown,mapping])
    limits=a2.ReaderLimits.standard();base=PlanResolver([source.source_bytes],limits=limits)
    writer=S2RecordWriter(base,ReadAccess(frozenset(base._views)),limits);draft=writer.context()
    data=qualified(data,source.package_id);mapping=qualified(mapping,source.package_id)
    with writer.begin(draft.author,draft.clock) as tx:
        inputs=tx.add('requirement',{'predicate':c2('s2.fixture.captured_csv'),'subjects':[data],'parameters':[],
            'scope':scope(data),'source':s2(draft.author)})
        preserves=tx.add('requirement',{'predicate':c2('s2.fixture.values_under_map'),'subjects':[data,mapping],
            'parameters':[],'scope':scope(data,mapping),'source':s2(draft.author)})
        spec=tx.add('transform_spec',{'operation':c2('s2.fixture.fixed_permutation'),'inputs':[inputs],'parameters':[],
            'preserves':[preserves],'produces':[],'randomness':[],'predecessors':[],
            'reference_rule':c2('s2.fixture.value_correspondence_only'),'source':s2(draft.author)})
        tx.commit()
    frozen=writer.frozen([spec]);writer.base=writer.base.with_view(frozen)
    writer.access=ReadAccess(frozenset(set(writer.access.packages)|{frozen.package_id}))
    views=tuple(codec.parse_snapshot(v.source_bytes,L) for v in writer.base.closure(frozen.package_id,writer.access,limits))
    return source,data,mapping,qualified(spec,frozen.package_id),qualified(preserves,frozen.package_id),draft,views

def provider(spec,requirement,mapping,views,counter,*,implementation,bad=False):
    from crucis_causal.connections.model import Builder as B1,contract as c1,source as src1
    from crucis_causal.connections.evidence import capture_bytes
    def execute(inputs):
        counter.append('actual_provider_entry')
        rows=list(csv.reader(io.StringIO(inputs.sources[0].bytes.decode('utf-8'))))
        stream=io.StringIO(newline='');writer=csv.writer(stream,lineterminator='\n');writer.writerow(['v0','v1','v2'])
        transformed=[[row[j] for j in (2,0,1)] for row in rows[1:]]
        if bad:transformed[0][0]='different'
        writer.writerows(transformed);raw=stream.getvalue().encode()
        preserved=all(new[j]==old[k] for old,new in zip(rows[1:],transformed) for j,k in enumerate((2,0,1)))
        b=B1('Observed preparation product and executed check')
        procedure=reference(identity(),'s1.component');configuration=reference(identity(),'s1.configuration')
        settings=capture_bytes(b,canonical({'permutation':['2','0','1'],'negative_control_bad_value':bad}),format_contract=c1('json'))
        b.add('component',{'name':'Explicit fixed CSV permutation/check fixture','role':'s1.preparation_provider','version':known('fixture-1'),
            'implementation':known({'artifact':implementation.reference,'selector':implementation.selector}),
            'configuration':known(configuration),'source':src1('intrinsic')},record_id=procedure['target'])
        b.add('configuration',{'component':procedure,'explicit_settings':settings,'resolved_defaults':not_applicable(),
            'scope':scope(procedure),'source':src1('observed')},record_id=configuration['target'])
        out=capture_bytes(b,raw,format_contract=c1('csv'),basis='observed')
        check=b.add('check',{'procedure':procedure,'contract_checked':{'name':'s2.fixture.values_under_map','version':'0.1.0-proposal.1'},
            'subjects':[spec,requirement],'inputs':[inputs.sources[0].reference,out,mapping],'scope':scope(spec,requirement),
            'result':'pass' if preserved else 'fail','diagnostics':[],'source':src1('derived',[out],procedure)})
        captured=snapshot1(b,[out,check],(*views,implementation.source_view))
        return RealizationProduct((*views,implementation.source_view,captured),(qualified(out,captured.package_id),),(mapping,),
            (qualified(check,captured.package_id),),known([]),(),{'name':'s2.fixture.value_correspondence_only','version':'0.1.0-proposal.1'})
    return execute

def fitted_case(implementation,counter):
    """Actual fit on a separate captured calibration source, before transformation."""
    from decimal import Decimal
    from crucis_causal.connections.model import Builder as B1,contract as c1,source as src1
    from crucis_causal.connections.evidence import capture_bytes
    from crucis_causal.experiments.model import contract as c2,source as src2
    from crucis_causal.experiments.resolver import parse_snapshot,ReadAccess
    _,data,_,_,_,draft,_=metadata();b=B1('Explicit calibration subset')
    calibration=capture_bytes(b,b'A\n1\n',format_contract=c1('csv'));calibration_view=snapshot1(b,[calibration])
    calibration=qualified(calibration,calibration_view.package_id)
    writer=draft.records;writer.base=writer.base.with_view(parse_snapshot(calibration_view.source_bytes,draft.read.limits))
    writer.access=ReadAccess(frozenset(set(writer.access.packages)|{calibration_view.package_id}))
    with writer.begin(draft.author,draft.clock) as tx:
        req=tx.add('requirement',{'predicate':c2('s2.fixture.exact_fitting_inputs'),'subjects':[calibration,data],
            'parameters':[],'scope':scope(calibration,data),'source':src2(draft.author)})
        check_req=tx.add('requirement',{'predicate':c2('s2.fixture.calibration_scope_and_arithmetic'),'subjects':[calibration,data],
            'parameters':[],'scope':scope(calibration,data),'source':src2(draft.author)})
        spec=tx.add('transform_spec',{'operation':c2('s2.fixture.fit_and_permute'),'inputs':[req],'parameters':[],
            'preserves':[check_req],'produces':[],'randomness':[],'predecessors':[],
            'reference_rule':c2('s2.fixture.no_automatic_truth_inheritance'),'source':src2(draft.author)})
        tx.commit()
    frozen=writer.frozen([spec]);writer.base=writer.base.with_view(frozen)
    writer.access=ReadAccess(frozenset(set(writer.access.packages)|{frozen.package_id}))
    spec=qualified(spec,frozen.package_id);check_req=qualified(check_req,frozen.package_id)
    views=tuple(codec.parse_snapshot(v.source_bytes,L) for v in writer.base.closure(frozen.package_id,writer.access,draft.read.limits))
    def validate(inputs):
        return len(inputs.sources)==2 and [v.reference for v in inputs.sources]==[calibration,data] and all(v.bytes is not None for v in inputs.sources)
    def execute(inputs):
        counter.append('actual_fitting_entry')
        calibration_rows=list(csv.reader(io.StringIO(inputs.sources[0].bytes.decode())))[1:]
        values=[Decimal(row[0]) for row in calibration_rows];mean=sum(values)/len(values)
        target=list(csv.reader(io.StringIO(inputs.sources[1].bytes.decode())))[1:]
        rows=[[row[2],str(Decimal(row[0])-mean),row[1]] for row in target]
        stream=io.StringIO(newline='');out_writer=csv.writer(stream,lineterminator='\n');out_writer.writerow(['v0','v1','v2']);out_writer.writerows(rows)
        b=B1('Observed calibration fit, fitted state and transformed output')
        procedure=reference(identity(),'s1.component');configuration=reference(identity(),'s1.configuration')
        settings=capture_bytes(b,canonical({'fit_sources':[calibration],'target_sources':[data],'method':'mean_of_A_then_center_and_permute'}),format_contract=c1('json'))
        b.add('component',{'name':'Fixture fit/calibration procedure','role':'s1.preparation_provider','version':known('fixture-1'),
            'implementation':known({'artifact':implementation.reference,'selector':implementation.selector}),
            'configuration':known(configuration),'source':src1('intrinsic')},record_id=procedure['target'])
        b.add('configuration',{'component':procedure,'explicit_settings':settings,'resolved_defaults':not_applicable(),
            'scope':scope(procedure),'source':src1('observed')},record_id=configuration['target'])
        transformed=capture_bytes(b,stream.getvalue().encode(),format_contract=c1('csv'),basis='observed')
        state=capture_bytes(b,canonical({'centering_mean':str(mean),'fitted_sources':[calibration]}),format_contract=c1('json'),basis='observed')
        check=b.add('check',{'procedure':procedure,'contract_checked':c2('s2.fixture.calibration_scope_and_arithmetic'),
            'subjects':[spec,check_req],'inputs':[calibration,data,transformed,state],'scope':scope(spec,check_req),
            'result':'pass' if len(values)==1 and mean==Decimal('1') else 'fail','diagnostics':[],
            'source':src1('derived',[transformed,state],procedure)})
        snapshot=snapshot1(b,[transformed,state,check],(*views,implementation.source_view))
        return RealizationProduct((*views,implementation.source_view,snapshot),(qualified(transformed,snapshot.package_id),qualified(state,snapshot.package_id)),(),
            (qualified(check,snapshot.package_id),),known([calibration]),(),c2('s2.fixture.no_automatic_truth_inheritance'))
    selected=Realizer(contract('s3.fixture.fit_and_permute'),c2('s2.fixture.fit_and_permute'),implementation,
        supplied_callable(execute),supplied_callable(validate))
    return spec,calibration,data,draft,views,selected

def skeleton(component,dependencies,*,operation,roles,parameters,account_id=None,receiver=None):
    b=Builder('Actual B05 preparation account');audience=b.add('audience',{'purpose':contract('s3.private_fixture'),
        'recipients':index(),'disclosure_policy':unknown_ref('s1.policy'),'authority':unknown()})
    target_subjects=[ref for role in roles for ref in role['members']['members']]
    target=b.add('target',{'definition':contract('s3.prospective_preparation'),'scope':scope(*target_subjects),'subjects':index(target_subjects),
        'requirements':index(),'relations':index()})
    account=b.add('account',{'purpose':'prepare','target':target,'related_accounts':index()},record_id=account_id)
    requirements=b.add('requirement_context',{'catalog':contract('s3.fixture.manual_preparation_checks'),
        'requested_claims':index(),'coverage':index(extent='not_examined')})
    frontier=b.add('frontier',{'local_records':index([account,target]),'source_positions':index(),'selection_rule':contract('s3.pre_effect_cutoff')})
    roles=[*roles,{'role':'s3.role.account','members':index([account])}]
    binding=b.add('operation_binding',{'operation':contract(operation),'roles':roles,
        'parameters':[{'key':key,'value':value} for key,value in parameters.items()]})
    command=b.add('effect_command',{'account':account,'operation':contract(operation),'binding':binding,'targets':scope(target),
        'dependencies':index([component]),'admission':unknown('s3.current_admission_is_separate'),'frontier':frontier})
    transmission=b.add('transmission',{'command':command,'channel':contract('s3.trusted_local_call'),'recipient':receiver or component,
        'ownership':unknown(),'sent_at':unknown(),'receipts':index()})
    disposition=b.add('disposition',{'kind':'selected','operations':index([command]),'requirements':requirements,'frontier':frontier,'basis':[]})
    root=b.add('account_view',{'account':account,'view_role':'full_account','audience':audience,'frontier':frontier,'requirements':requirements,
        'activities':index([command]),'evidence':index(),'assessments':index(),'disposition':disposition,'obligations':index(),'collections':index()})
    view=frame(b,root,dependencies)
    return view,qualified(account,view.package_id),qualified(binding,view.package_id),qualified(command,view.package_id),qualified(transmission,view.package_id)

def actor(implementation):
    b=Builder('Trusted input fixture actor',implementation=known({'artifact':implementation.reference,'selector':implementation.selector}))
    audience=b.add('audience',{'purpose':contract('s3.actor_metadata'),'recipients':index(),'disclosure_policy':unknown_ref('s1.policy'),'authority':unknown()})
    root=b.add('projection_view',{'view_role':'audience_projection','audience':audience,'projection_contract':contract('s3.actor_metadata'),
        'members':index([b.producer]),'claims':index(),'limits':index()})
    view=frame(b,root,(implementation.source_view,));return qualified(b.producer,view.package_id),view

def staging_metadata(component,dependencies,*,namespace,stability='snapshot'):
    import zipfile
    from crucis_causal.connections.model import Builder as B1,contract as c1,source as src1,unknown_ref as uref
    from crucis_causal.connections.evidence import capture_bytes
    b=B1('Selected native input and evaluator-only archive member')
    raw=io.BytesIO()
    with zipfile.ZipFile(raw,'w') as archive:
        archive.writestr('data.csv',SOURCE);archive.writestr('mask.csv',b'1,0,1\n')
        archive.writestr('evaluator-only-map.txt',b'private evaluator mapping; never native input')
    artifact=capture_bytes(b,raw.getvalue(),format_contract=c1('zip'))
    presentations=[]
    for name in ['data.csv','mask.csv']:
        presentations.append(b.add('presentation',{'information_contract':c1('table_input'),
            'payload':known({'artifact':artifact,'selector':known({'selector_type':'archive_member','name':name,'member_digest':unknown()})}),
            'endpoint':unknown(),'domain':unknown(),'schema':unknown(),'recipient':b.producer,'state':'permitted',
            'attempt':uref('attempt'),'source':src1('intrinsic')}))
    native=snapshot1(b,presentations)
    # The actual closed driver parameter bytes name only the permitted members.
    p=Builder('Exact trusted staging parameters');parameters={'members':[{'presentation':qualified(ref,native.package_id),'name':name} for ref,name in zip(presentations,['s3.member.data','s3.member.mask'])],
        'custody_namespace':namespace,'custody_epoch':'0','activation':'coherent_bundle'}
    storage=B1('Staging parameter capture');content=capture_bytes(storage,canonical(parameters),format_contract=c1('json'))
    storage_view=snapshot1(storage,[content])
    typed=p.add('typed_payload',{'payload_contract':contract('s3.payload.trusted_stage'),
        'content':{'artifact':qualified(content,storage_view.package_id),'selector':not_applicable()},
        'reference_context':{'package_id':p.package_id,'format':contract('account_package')}})
    audience=p.add('audience',{'purpose':contract('s3.staging_parameters'),'recipients':index(),'disclosure_policy':unknown_ref('s1.policy'),'authority':unknown()})
    root=p.add('projection_view',{'view_role':'audience_projection','audience':audience,'projection_contract':contract('s3.staging_parameters'),
        'members':index([typed]),'claims':index(),'limits':index()})
    pv=frame(p,root,(native,storage_view))
    views=(*dependencies,native,storage_view,pv)
    initial,account,binding,command,transmission=skeleton(component,views,operation='s3.op.stage_input',
        roles=[{'role':'s3.role.presentations','members':index([qualified(r,native.package_id) for r in presentations])},
            {'role':'s3.role.recipient','members':index([qualified(b.producer,native.package_id)])}],
        parameters={'transfer_contract':known(contract('s3.transfer.trusted_snapshot')),'native_parameters':known(qualified(typed,pv.package_id)),
            'stability':known(stability),'cleanup_rule':known(contract('s3.cleanup.revoke_trusted_interface'))})
    return (*views,initial),account,binding,command,transmission

def endpoint_metadata(component,dependencies,implementation,counter):
    from crucis_causal.connections.model import Builder as B1,contract as c1,source as src1,unknown_ref as uref
    from crucis_causal.connections.evidence import capture_bytes
    b=B1('Explicit bounded endpoint and native recipient')
    owner_ref=reference(identity(),'s1.component');recipient_ref=reference(identity(),'s1.component')
    endpoint_ref=reference(identity(),'s1.endpoint')
    settings=capture_bytes(b,canonical({'maximum_queries':'1','response_materialization':'per_query','source_profile':'process_local_fixture'}),format_contract=c1('json'))
    for ref,name,role in [(owner_ref,'Actual local endpoint source owner','s1.endpoint_provider'),(recipient_ref,'Trusted endpoint consumer','s1.native_fixture_consumer')]:
        b.add('component',{'name':name,'role':role,'version':known('fixture-1'),
            'implementation':known({'artifact':implementation.reference,'selector':implementation.selector}),
            'configuration':unknown(),'source':src1('intrinsic')},record_id=ref['target'])
    policy=b.add('policy',{'policy_contract':c1('s3.fixture.bounded_endpoint_information','0.1.0-proposal.3'),
        'parameters':[settings],'scope':scope(owner_ref,recipient_ref,endpoint_ref),'authority':unknown(),'source':src1('intrinsic')})
    operation=c1('fixture_endpoint_question')
    b.add('endpoint',{'owner':owner_ref,'operation':operation,'request_contract':c1('opaque_bytes'),'response_contract':c1('opaque_bytes'),
        'input_domains':[],'allowed_information':policy,'transport':c1('trusted_memory_endpoint'),'source':src1('intrinsic')},record_id=endpoint_ref['target'])
    presentation=b.add('presentation',{'information_contract':c1('bounded_oracle'),'payload':unknown(),'endpoint':known(endpoint_ref),
        'domain':unknown(),'schema':unknown(),'recipient':recipient_ref,'state':'permitted','attempt':uref('attempt'),'source':src1('intrinsic')})
    native=snapshot1(b,[presentation],(implementation.source_view,))
    owner_ref=qualified(owner_ref,native.package_id);recipient_ref=qualified(recipient_ref,native.package_id);endpoint_ref=qualified(endpoint_ref,native.package_id)
    def answer(arguments):counter.append('actual_endpoint_query');return b'bounded-answer:'+arguments
    owner=EndpointOwner(owner_ref,endpoint_ref,operation,supplied_callable(answer),max_queries='1')
    grant=owner.grant(recipient_ref)
    values={'presentation':qualified(presentation,native.package_id),'endpoint_namespace':owner.namespace,'generation':owner.generation,'maximum_queries':'1'}
    storage=B1('Endpoint parameter capture');content=capture_bytes(storage,canonical(values),format_contract=c1('json'));stored=snapshot1(storage,[content])
    p=Builder('Exact owner-managed endpoint staging parameters')
    typed=p.add('typed_payload',{'payload_contract':contract('s3.payload.trusted_endpoint_stage'),
        'content':{'artifact':qualified(content,stored.package_id),'selector':not_applicable()},
        'reference_context':{'package_id':p.package_id,'format':contract('account_package')}})
    audience=p.add('audience',{'purpose':contract('s3.endpoint_parameters'),'recipients':index(),'disclosure_policy':unknown_ref('s1.policy'),'authority':unknown()})
    root=p.add('projection_view',{'view_role':'audience_projection','audience':audience,'projection_contract':contract('s3.endpoint_parameters'),
        'members':index([typed]),'claims':index(),'limits':index()})
    params=frame(p,root,(native,stored));views=(*dependencies,native,stored,params)
    initial,account,binding,command,transmission=skeleton(component,views,receiver=owner_ref,operation='s3.op.stage_input',
        roles=[{'role':'s3.role.presentations','members':index([qualified(presentation,native.package_id)])},
            {'role':'s3.role.recipient','members':index([recipient_ref])}],
        parameters={'transfer_contract':known(contract('s3.transfer.trusted_endpoint')),'native_parameters':known(qualified(typed,params.package_id)),
            'stability':known('immutable_reference'),'cleanup_rule':known(contract('s3.cleanup.revoke_endpoint_proxy'))})
    return (*views,initial),account,binding,command,transmission,owner,grant

def manual_admission(root,source,account,binding_ref,command,transmission,driver_factory):
    """Real owner/journal admission for the guarded mechanism, not LiveAdmission.

    Broader scientific profile evaluation remains the B06 coordinator's gate.
    """
    from test_audit_execution_owners import owner_setup,packet,request as owner_request
    # Use the actual B03 owner APIs; no serialized receipt mints a live grant.
    resolver=codec.Resolver(source,limits=L);binding=resolve_binding(binding_ref,binding_ref['package_id'],resolver)
    owner=LocalOwner(root/'owner',{'s3.fixture_work':{'unit':contract('fixture_unit'),'capacity':{'number_type':'integer','text':'20'}}},
        native_operations=(binding.record['payload']['operation'],))
    control=owner.control(identity(),max_calls='100')
    with owner._db() as db:
        for row in db.execute('SELECT data FROM views'):resolver.add(codec.parse_snapshot(bytes(row[0]),L))
    read=api.PinnedReadContext(tuple(resolver._views.values()),api.supplied_read(resolver._views),None,L)
    octx=api.RuntimeContext(read,control)
    amounts={'entries':[{'resource':contract('s3.fixture_work'),'unit':contract('fixture_unit'),'quantity':{'number_type':'integer','text':'1'},
        'scope':scope(reference(binding.record['id'],'operation_binding',binding.context['package_id'])),'aggregation':contract('s3.aggregation.replace_then_disjoint_members')}]}
    refs,octx=packet(binding,octx,{'amounts':('reservation_amounts',amounts)})
    req=owner_request(owner,binding,'reserve',params={'amounts':refs['amounts'],'expected_revision':'0'})
    journal=Journal(root/'journal');jctx=api.RuntimeContext(octx.read,journal.control(account))
    initial=next(v for v in source if v.package_id==account['package_id'])
    opened=journal.append(account,'0',identity(),api.CommitDelta(initial.records,tuple(initial.package['roots']),tuple(octx.read.views)),jctx)
    if opened.state!='completed':raise AssertionError(opened.issues)
    planned=persist_owner_requests(journal,opened.value.head,(req,),jctx,octx.read)
    if planned.state!='completed':raise AssertionError(planned.issues)
    reserved=owner.reserve(req,octx)
    if reserved.state!='completed' or reserved.value.grant is None:raise AssertionError(reserved.issues)
    dependencies=(*octx.read.views,*reserved.records.dependencies)
    jctx=replace(jctx,read=replace(octx.read,views=dependencies,access=api.supplied_read(v.package_id for v in dependencies)))
    head=journal.head(account,jctx).value
    validity=api.ValidityContext((),unknown(),(),api.RecordDelta())
    token=journal.prepare_issue(command,head,api.OwnerBindingReceipts((reserved.value.receipt,),binding_digest(binding),validity),jctx,transmission)
    if token.state!='completed':raise AssertionError(token.issues)
    boundary=DriverBoundary(journal,jctx,((owner,octx),));driver=driver_factory(boundary)
    descriptor=driver.descriptors[binding.record['payload']['operation']['name']]
    request=api.ExactOperationRequest(command,binding,binding.inputs,descriptor,resolver.view(binding.context['package_id']))
    context=api.RuntimeContext(jctx.read,None)
    return driver,request,context,(reserved.value.grant,),token.value,owner,octx,journal,jctx
