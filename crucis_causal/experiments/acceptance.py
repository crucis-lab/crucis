"""Release-only traceability from approved obligations to executed cases (DLV-08/09/10)."""
import importlib
import json
from pathlib import Path
import subprocess
import sys

# Rows correspond in order to the immutable accepted DAG's must-show rows.
# Fragments identify functional assertions, not just shape/fixture counts.
ROWS={
'S2-A':[
 ['all_accepted_snapshots','all_eleven_typed_payload_formats'],['bad_json_never','parameters_keys_roles'],
 ['lexical_numbers_array_order'],['pretty_received_bytes','record_identity_conflict_even'],
 ['scope_access_no_locator','payload_fragment_and_unqualified'],['reader_limits_positive','structural_cycles_allowed'],['scope_access_no_locator']],
'S2-B':[
 ['runtime_outcomes_and_context_scope','test_API01','test_API20'],['no_add_without_transaction','known_false_predicate'],
 ['occurrence_identity_persisted','durable_import_rehydrates'],['new_writer_records_actual'],['exact_registry_no_implicit'],
 ['preserve_profile_and_missing','interpretation_requires_exact','test_API04'],['known_false_predicate','unknown_critical_extension']],
'S2-C':[
 ['unique_slot_resolution','complete_collection_detects','multiple_or_wrong_source'],['structural_cycles_allowed','recipe_predecessor_cycle','cycle_in_event_predecessors'],
 ['response_omission_scope','completion_cardinality_unknown','partial_contested_reference'],['duplicate_required_response','reference_must_be_declared'],
 ['source_scope_and_manifest','external_evidence_links_are_qualified'],['all_capability_and_composite_scopes']],
'S2-D':[
 ['evaluator_channel_cannot','supported_differently_named_operation','partial_exposure_survives'],['unique_slot_resolution','multiple_or_wrong_source','missing_materialization_and_subject'],
 ['complete_supplied_identity_realization','partial_transform_receipt'],['temporal_boundaries_units','temporal_large_window','temporal_ineligible_first'],
 ['relational_perspective_and_site','distributed_unknown_contributions'],['alignment_keeps_two'],
 ['native_weighted_collection','zero_negative_and_nonfinite','cyclic_derived_graph'],['unknown_intervention_targets','proxy_domain_not'],['random_repeat_key_does_not']],
'S2-E':[
 ['missing_observations_retain_every','exclusion_without_a_reason','no_unstated_denominator'],['abstention_or_intermediate','nonconforming_inclusion','missing_observations_retain_every'],
 ['explicit_current_metadata_population','scientific_metric_descriptor_absent'],['duplicate_unit_requires','particle_weight_and_native_retry','checkpoint_restart_is_new_attempt'],
 ['multiple_final_outputs','reference_must_be_declared'],['baseline_and_active_target','test_API12'],['scientific_metric_descriptor_absent','explicit_current_metadata_population']],
'S2-F':[
 ['future_bytes_in_dependency'],['commitment_pins_exact','amendment_retains_old_new'],['cycle_in_event_predecessors','commitment_pins_exact'],
 ['threshold_decision_records','negative_branch_and_evaluator','nonconforming_or_claimed_delivered'],['partial_exposure_survives','local_record_never'],
 ['local_record_never','evaluator_channel_cannot'],['amendment_retains_old_new','missing_materialization_and_subject']],
'S2-G':[
 ['supported_differently_named_operation','missing_native_support_or_exact'],['complex_cardinality_retained','s1_writer_and_s2_transaction'],
 ['external_evidence_links_are_qualified','handoff_pins_exact'],['projection_same_occurrence','changed_request_or_presentation','checkpoint_restart_is_new_attempt'],
 ['compiler_code_identity','new_writer_records_actual'],['frozen_R_and_later_O','future_bytes_in_dependency','amendment_retains_old_new'],
 ['supported_differently_named_operation','evaluator_channel_cannot'],['compiler_code_identity','test_API19']],
'S2-H':[
 ['all_eight_recorded_adapters_echo'],['source_scope_and_manifest','occurrence_reuse_preserves'],['exact_echo_preserves_statuses','source_scope_and_manifest'],
 ['source_scope_and_manifest','incompatible_source_labels'],['repeated_score_keys_reject'],['explicit_narrow_compatibility_view'],['cli_real_recorded_import','all_eight_recorded_adapters_echo']],
'S2-I':[
 ['all_accepted_snapshots','test_N01','test_N58','test_API01','test_API20'],['all_capability_and_composite_scopes','all_twenty_five_parameter_readers'],
 ['cli_real_recorded_import'],['cli_real_recorded_import','explicit_current_metadata_population'],
 ['all_eight_recorded_adapters_echo'],['schema_and_catalog_are_owned','new_writer_records_actual','all_capability_and_composite_scopes'],
 ['cli_real_recorded_import'],['compiler_code_identity','local_record_never']]
}

def build(root,plan,inventory,passed):
    """Only attest execution after the full discovered suite succeeds."""
    sys.path.insert(0,str(root/'tests'))
    cases=importlib.import_module('test_audit_experiments_integration')
    def match(fragment):
        matches=[x for x in inventory if fragment in x.rsplit('.',1)[-1]]
        if not matches:raise ValueError('missing executable acceptance check: '+fragment)
        return matches
    negative=[];api=[];bundles=[]
    for sid,spec in cases.NEGATIVES.items():
        functional=cases.SEMANTIC.get(sid)
        negative.append({'id':sid,'rule':spec.get('rule',spec['expected']),
            'accepted_expected':spec['expected'],'executed_test':match('test_'+sid)[0],
            'functional_fixture':'.'.join(functional) if functional else 'Exact accepted wire/byte mutation',
            'executed_and_passed':passed})
    for sid,spec in cases.SCENARIOS.items():
        api.append({'id':sid,'call':spec['call'],'accepted_expected':spec['expected'],
            'implementation_refinement':cases.API_REFINEMENTS.get(sid),'executed_test':match('test_'+sid)[0],
            'executed_and_passed':passed})
    for bundle in plan['bundles']:
        checks=ROWS[bundle['id']]
        if len(checks)!=len(bundle['must_show']):raise ValueError('must-show row count mismatch')
        bundles.append({'bundle':bundle['id'],'must_show':[{'requirement':text,'functional_tests':sorted({x for f in fragments for x in match(f)}),
            'common_evidence':'preservation/gate.json (numbers, certificates, original/S1 identities, test result)',
            'executed_and_passed':passed} for text,fragments in zip(bundle['must_show'],checks)]})
    if len(negative)!=58 or len(api)!=20:raise ValueError('accepted scenario inventory incomplete')
    return {'tickets':['DLV-08','DLV-09','DLV-10'],'scope':'Executed metadata/recorded checks, not native/scientific empirical coverage',
        'adverse_cases':negative,'api_scenarios':api,'bundles':bundles,'passed':passed}

def recorded_path(root,out):
    """Durable CLI and S2 evidence association using a common-gate recorded import."""
    from . import core,api
    from .model import reference,identity,qualified
    from .resolver import PlanResolver,ReadAccess,parse_snapshot
    from .services import FamilyRegistry
    from .writer import S2RecordWriter
    from .__main__ import _save
    from crucis_causal.connections.evidence import Resolver
    source=out/'preservation/connection_matmcd/package.json';p=json.loads(source.read_bytes())
    blob=next(r for r in p['records'] if r['record_type']=='s1.artifact_snapshot' and r['payload']['format'].get('value',{}).get('name')=='s1.legacy_runrecord_codec')
    destination=out/'s2-recorded-matmcd';commands=[]
    def command(*args):
        argv=[sys.executable,'-B','-m','crucis_causal.experiments',*map(str,args)]
        proc=subprocess.run(argv,cwd=root,capture_output=True,text=True)
        commands.append({'argv':argv,'returncode':proc.returncode})
        if proc.returncode:raise ValueError('S2 recorded CLI rejected: '+proc.stdout[:240]+proc.stderr[:120])
        return json.loads(proc.stdout)
    first=command('inspect',source);second=command('inspect',source)
    if first!=second:raise ValueError('non-deterministic inspection')
    imported=command('import',source,'--snapshot',blob['id'],'--occurrence',identity(),'--out',destination/'import','--battery','ca-ab06')
    files=sorted((destination/'import/dependencies').glob('*.json'))
    inputs=[x for f in files for x in ('--input',f)]
    command('project',destination/'import/package.json',*inputs,'--receipt',imported['receipt']['target'],
        '--selection',imported['selection']['target'],'--out',destination/'echo')
    command('validate',destination/'import/package.json',*inputs,'--out',destination/'validation')
    exact=json.loads((destination/'echo/legacy.json').read_bytes())[0]==json.loads(Resolver(p).bytes(reference(blob['id'],'s1.artifact_snapshot')))
    if not exact:raise ValueError('S2 recorded echo differs from actual encoded source')
    limits=api.ReaderLimits.standard();view=parse_snapshot((destination/'import/package.json').read_bytes(),limits)
    base=PlanResolver([view.source_bytes,*[f.read_bytes() for f in files]],limits=limits)
    w=S2RecordWriter(base,ReadAccess(frozenset(base._views)),limits);draft=w.context()
    subject=qualified(imported['receipt'],view.package_id);evidence=reference(blob['id'],'s1.artifact_snapshot',p['package_id'])
    association=core.link_evidence((subject,),(evidence,),draft)
    if association.state!='completed':raise ValueError('S2 recorded evidence association failed')
    binding=destination/'binding';binding.mkdir(parents=True)
    _save(w.frozen(association.additions.roots),w,binding)
    report={'tickets':['DLV-08','DLV-09','DLV-10'],'system':'matmcd','source':str(source),
        'source_snapshot':evidence,'import_receipt':subject,'binding':association.additions.roots,
        'echo_equal':exact,'inspection_deterministic':first==second,'commands':commands,
        'native_execution':False,'scope':'Current observer association of recorded encoded value; original native history/scientific validity unestablished','passed':True}
    (destination/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report
