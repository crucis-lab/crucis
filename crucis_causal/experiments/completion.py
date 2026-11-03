"""Optional S1 completion rule for exact role counts, never correctness (DLV-08/09)."""
import json
from .model import contract,known,unknown

def install(registry):
    def check(subjects,basis,parameters,context):
        request=next((context.resolver.record(r) for r in subjects if r['target_type']=='s1.request'),None)
        if request is None:raise ValueError('request required')
        requirements=[]
        for ref in parameters:
            record=context.resolver.record(ref)
            if record['record_type']=='s1.artifact_snapshot' and record['payload']['format'].get('value')==contract('s2.response_projection'):
                requirements.append(json.loads(context.resolver.bytes(ref)))
        if len(requirements)!=1:raise ValueError('exact projected requirements required')
        outputs=[];complete=False
        for ref in basis:
            record=context.resolver.record(ref)
            if record['record_type']=='s1.connection_observation' and record['payload']['request']['target']==request['id']:
                complete|=record['payload']['outputs']['extent']=='complete_for_scope'
                outputs.extend(context.resolver.record(r)['payload'] for r in record['payload']['outputs']['members'])
        result=bool(outputs);understood=requirements[0]['fulfillment_rule'] in (contract('s2.roles_or_abstention'),contract('s2.exact_roles'),contract('s2.exact_final_or_abstention'))
        for role in requirements[0]['deliverables']:
            matching=[p for p in outputs if p['role'].get('value')==role['role']]
            count=len(matching);minimum=int(role['cardinality']['minimum']);maximum=role['cardinality']['maximum']
            if count<minimum:result=False
            if maximum['kind']=='finite' and count>int(maximum['value']):result=False
            expected=role['contract']
            supported={'s1.graph':'graph','s1.claims':'claims','s1.order':'order','s1.quantity':'quantity','s1.collection':'collection','s1.model_reference':'model_reference','s1.abstention':'abstention','s1.set':'set','s1.ranking':'ranking'}
            if expected['name'] not in supported or expected['version']!=contract('s2.completion_roles')['version']:understood=False
            else:
                for p in matching:
                    if p['output_type']=='abstention' and role['abstention']=='allowed':continue
                    if p['output_type']!=supported[expected['name']]:result=False
        value=known(result) if complete and understood else unknown('s2.fulfillment_capture_or_contract_unestablished')
        return [{'facet':'s2.request_fulfillment','value':value,'supporting':list(basis),'disputed':[]}]
    registry.register_rule(contract('s2.completion_roles'),check)
