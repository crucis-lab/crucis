"""Exact opt-in core entry points; no legacy consumer swap (DLV-08/09)."""
from pathlib import Path

from . import api
from .codec import WireError, dumps
from .model import contract, known, not_applicable, reference, scope, source, unresolved
from .semantics import validate as inspect_package


# Profiles promise only their named local guarantees. Unknown exact versions reject.
PROFILES = {
    's1.evidence_foundation': ('s1.wire_references','s1.connection_minimum'),
    's1.available_snapshots': ('s1.snapshot_integrity',),
    's1.graph_encoding': ('s1.graph_encoding',),
    's1.dag': ('s1.graph_encoding','s1.dag'),
    's1.finite_measure': ('s1.collection_members','s1.finite_measure'),
    's1.tensor_encoding': ('s1.axes','s1.tensor_encoding'),
    's1.event_history': ('s1.event_links','s1.event_precedence'),
}


def _checks(report, records, subjects=()):
    refs=[];gaps=[]
    for issue in report.issues+report.withheld:
        gap=records.gap(subjects,issue.code);gaps.append(gap)
    for c in report.checks:
        subject=next((r for r in records.snapshot() if r['id']==c.subject),None)
        refs.append(records.add('check',{'procedure':records.builder.producer,'contract_checked':contract(c.contract),
            'subjects':[reference(c.subject,subject['record_type'])] if subject else list(subjects),
            'inputs':list(subjects),'scope':scope(*subjects),'result':c.result,'diagnostics':[],
            'source':source('reconstructed',subjects,records.builder.producer)}))
    return tuple(refs),tuple(gaps)


def resolve(reference, context):
    try:
        record=context.resolver.record(reference)
        return api.Op('completed',api.ResolvedRecord(record,(),()))
    except (KeyError,OSError,WireError):
        return api.Op('rejected',diagnostics=(context.records.gap([reference],'s1.reference_not_resolved'),))


def validate(package, profiles, context):
    report=inspect_package(package,resolver=context.resolver);satisfied=[];withheld=[]
    for p in profiles:
        requirements=PROFILES.get(p['name']) if p==contract(p['name']) else None
        try:
            if requirements is None:raise WireError('unknown exact profile')
            report.require(requirements)
            if any(c.contract==p['name'] and c.result!='pass' for c in report.checks):raise WireError('critical extension withholds requested profile')
            satisfied.append(p)
        except WireError:withheld.append(p)
    checks,gaps=_checks(report,context.records,package['roots'])
    return api.ValidationReport(checks,gaps,tuple(satisfied),tuple(withheld))


def assess(rule, subjects, basis, parameters, context):
    checker=context.services.registry.rule(rule)
    if checker is None:
        return api.Op('rejected',diagnostics=(context.services.records.gap(subjects,'s1.unsupported_assessment'),))
    try:
        conclusions=checker(subjects,basis,parameters,context)
        ref=context.services.records.add('assessment',{'subjects':list(subjects),'rule':rule,'parameters':list(parameters),
            'basis':list(basis),'conclusions':conclusions,'cutoff':list(basis),'revises':[]})
        return api.Op('completed',ref)
    except (KeyError,OSError,ValueError,TypeError,WireError):
        return api.Op('rejected',diagnostics=(context.services.records.gap(subjects,'s1.assessment_not_established'),))


def outcome_observations(subjects,basis,parameters,context):
    """Conservative native-property facet rule: conflicts stay unresolved, no latest-wins.

    This classifies supplied observations, not authenticity, native success or
    scientific truth. Later assessments name a later cutoff without mutating this.
    """
    if parameters:raise WireError('this exact rule accepts no parameters')
    facets={}
    for ref in basis:
        r=context.resolver.record(ref)
        if r['record_type']!='s1.observation':raise WireError('observation basis required')
        p=r['payload']
        if p['subject'] not in subjects:raise WireError('observation outside assessment subjects')
        proposition=context.resolver.record(p['proposition'])['payload']
        if proposition['predicate']!=contract('native_property'):continue
        args={a['role']:a['value'] for a in proposition['arguments']};facet=args.get('s1.property','')
        if args.get('s1.subject')!=p['subject']:raise WireError('proposition and observation subject disagree')
        if not isinstance(facet,str) or not facet.startswith('s1.outcome.'):continue
        facets.setdefault(facet,[]).append((ref,p['value']))
    results=[]
    for facet,entries in facets.items():
        distinct={dumps(v) for _,v in entries};refs=[r for r,_ in entries]
        results.append({'facet':facet,'value':known(entries[0][1],refs) if len(distinct)==1 else unresolved('s1.conflicting_evidence',refs),
            'supporting':refs if len(distinct)==1 else [],'disputed':refs if len(distinct)>1 else []})
    return results


def _write_allowed(destination, context):
    policy=context.services.records.get(context.write_scope)
    if (policy['record_type']!='s1.policy' or policy['payload']['policy_contract']!=contract('local_publication')
        or destination not in policy['payload']['scope']['subjects']):raise WireError('destination not covered by explicit publication policy')


def publish(staged, policy, context):
    records=context.services.records
    try:
        if policy.backend!=contract('local_immutable_store'):raise WireError('unsupported publication backend')
        _write_allowed(policy.destination,context)
        store=context.services.identities.store
        if store is None:raise WireError('explicit package store required')
        location=records.get(policy.destination)['payload']
        if Path(location['locator']).resolve()!=store.root:raise WireError('destination differs from supplied store')
        report=inspect_package(staged,resolver=context.resolver)
        for profile in policy.allowed_profiles:
            if profile!=contract(profile['name']) or profile['name'] not in PROFILES:raise WireError('unsupported publication profile')
        for required in policy.required_checks:
            if required!=contract(required['name']):raise WireError('unsupported check version')
        for profile in policy.allowed_profiles:
            report.require(PROFILES[profile['name']])
            if any(c.contract==profile['name'] and c.result!='pass' for c in report.checks):raise WireError('profile withheld by extension')
        report.require([c['name'] for c in policy.required_checks])
        receipt=store.publish(staged,resolver=context.resolver)
        digest={'algorithm':'sha256','value':receipt['sha256'],'byte_length':str(len(dumps(staged))),'scope':{'kind':'full_content'}}
        return api.Op('completed',api.PublishedPackage(staged['package_id'],policy.destination,digest,
            tuple(reference(r['id'],r['record_type']) for r in staged['records'])))
    except (KeyError,OSError,ValueError,TypeError,WireError):
        return api.Op('rejected',diagnostics=(records.gap(staged.get('roots',()),'s1.publication_not_established'),))


def select_current(alias, selection, expected_previous, context):
    try:
        # Scope names the exact immutable selection. Alias identity remains a separate CAS.
        _write_allowed(selection,context)
        if expected_previous['state']=='known':previous=expected_previous['value']
        elif expected_previous['state']=='not_applicable' and expected_previous['rule']==contract('no_prior_selection'):previous=None
        else:raise WireError('unresolved previous alias is not compare-and-swap authority')
        store=context.services.identities.store
        if store is None:raise WireError('explicit package store required')
        receipt=store.select_current(alias.namespace,alias.name,selection,previous)
        return api.Op('completed',api.SelectionReceipt(alias,known(previous) if previous else not_applicable('no_prior_selection'),selection,receipt['generation']))
    except (KeyError,OSError,ValueError,TypeError,WireError):
        return api.Op('rejected',diagnostics=(context.services.records.gap([selection],'s1.selection_conflict_or_denied'),))


def import_legacy(record, binding, source, context, sink):
    from .legacy import import_record, encode
    from .model import source as provenance
    import hashlib
    source_spec=source
    try:
        if (binding.legacy_contract!=contract('legacy_runrecord_codec') or record.item!=binding.item or record.arm!=binding.arm):
            raise WireError('legacy binding mismatch')
        if binding.coordinate_basis not in ('original','shown','unresolved'):raise WireError('unknown coordinate basis')
        if source_spec.expected_contracts and contract('legacy_runrecord_codec') not in source_spec.expected_contracts:
            raise WireError('legacy source contract mismatch')
        builder=context.records.builder
        component=builder.get(builder.producer)['payload']
        identity_artifact=component['implementation']['value']['artifact']
        implementation=builder.get(identity_artifact)['payload']['content']
        source_digests=[hashlib.sha256(context.resolver.bytes(ref)).hexdigest() for ref in source_spec.sources]
        bound={'legacy_value':encode(record),'binding':__import__('dataclasses').asdict(binding),
            'sources':list(source_spec.sources),'source_digests':source_digests,'reader_implementation':implementation,
            'expected_contracts':list(source_spec.expected_contracts)}
        def create():
            with builder.transaction():
                before={r['id'] for r in context.records.snapshot()}
                result=import_record(record,builder=builder,domain=binding.domain,coordinate_basis=binding.coordinate_basis)
                receipt=context.records.add('import_receipt',{'import_occurrence':source_spec.import_occurrence,
                    'sources':[result['legacy_snapshot']],'reader':builder.producer,'configuration':unresolved(),
                    'operation_policy':contract('legacy_import'),'result_roots':[result['root']],
                    'native_occurrence':binding.source_identity,'source':provenance('reconstructed',[result['legacy_snapshot']])})
                return {'closure':list(context.records.snapshot()),'records':[r for r in context.records.snapshot() if r['id'] not in before],
                    'artifacts':[result['legacy_snapshot']],'subjects':[result['root'],receipt],'gaps':result['gaps']}
        imported=context.identities.import_once(source_spec.import_occurrence,bound,create)
        context.records.ingest(imported['closure'])
        delta=api.EvidenceDelta(tuple(imported['records']),tuple(imported['artifacts']),tuple(imported['subjects']),tuple(imported['gaps']),binding.source_identity)
        return api.Op('partial' if imported['gaps'] else 'completed',delta,tuple(imported['gaps']))
    except (KeyError,OSError,ValueError,TypeError,WireError):
        return api.Op('rejected',diagnostics=(context.records.gap(source_spec.sources,'s1.legacy_import_not_established'),))


def project_legacy(package, selection, context):
    from .legacy import project
    try:return api.Op('completed',project(package,selection,context.resolver))
    except (KeyError,ValueError,TypeError,WireError):
        return api.Op('rejected',diagnostics=(context.records.gap([selection.graph],'s1.legacy_projection_undefined'),))
