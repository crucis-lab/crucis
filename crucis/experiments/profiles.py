"""Independent scoped profiles; no single scientific-valid flag (DLV-08/09)."""
from .api import PlanIssue,PlanValidationReport,PlanOp,InterpretedValue
from .errors import ServiceError
from .model import contract,walk,qualified
from .operations import atomic,get,assessment
from .schema import catalog

def _reachable(roots,context):
    read=context.read;pending=[(r,0) for r in roots];seen=set();packages=set()
    while pending:
        ref,depth=pending.pop()
        if depth>int(read.limits.max_reference_depth):raise ServiceError('s2.reference_depth_limit')
        found=read.resolver.record(ref,read.active_package,read.access,read.limits)
        key=found.package_id,found.record['id']
        if key in seen:continue
        seen.add(key)
        if len(seen)>int(read.limits.max_records):raise ServiceError('s2.record_limit')
        if found.package_id not in packages:
            packages.add(found.package_id)
            view=read.resolver.lookup(found.package_id,read.access,read.limits)
            yield {'extensions':view.package['extensions']}
        yield found.record
        for _,item,_ in walk(found.record):
            if isinstance(item,dict) and item.get('binding') in ('internal','external'):
                pending.append((qualified(item,found.package_id),depth+1))

def assess(roots,claims,context):
    def build(tx):
        if not roots:raise ServiceError('s2.assessment_subject_required')
        for ref in roots:get(ref,context)
        satisfied=[];withheld=[];assessments=[];allissues=[]
        supported=catalog()['profiles']
        for claim in claims:
            profile=claim['profile'];name=profile['name'];issues=[];results=[]
            if not claim['scope']['subjects']:raise ServiceError('s2.scoped_profile_required')
            if any(r not in roots for r in claim['scope']['subjects']) or any(r not in claim['scope']['subjects'] for r in roots):raise ServiceError('s2.profile_scope_mismatch')
            for ref in claim['scope']['subjects']:get(ref,context)
            if profile not in supported.values():
                issues.append(PlanIssue('s2.profile_unsupported'));results.append('not_checked')
            else:
                # Preservation is local shape/identity and explicit limits, not a
                # promise that unknown external native evidence was retrieved.
                try:records=list(_reachable(roots,context)) if name!='s2.preserve' else [get(ref,context) for ref in roots]
                except ServiceError as exc:
                    records=[];issues.append(PlanIssue(exc.code));results.append('not_checked')
                if name=='s2.preserve':
                    for ref in roots:
                        located=context.read.resolver.record(ref,context.read.active_package,context.read.access,context.read.limits)
                        records.append({'extensions':context.read.resolver.lookup(located.package_id,context.read.access,context.read.limits).package['extensions']})
                for record in records:
                    for path,item,_ in walk(record):
                        if isinstance(item,dict) and profile['name'] in item.get('critical_for',[]):
                            if item['contract'] not in claim['families'] or context.read.registry.lookup(item['contract']) is None:
                                issues.append(PlanIssue('s2.critical_extension_uninterpreted',path));results.append('not_checked')
                if name!='s2.preserve':
                    if not claim['families']:
                        issues.append(PlanIssue('s2.named_family_required'));results.append('unknown')
                    for family in claim['families']:
                        reader=context.read.registry.lookup(family)
                        if reader is None:
                            issues.append(PlanIssue('s2.family_reader_unavailable'));results.append('not_checked');continue
                        for ref in roots:
                            record=get(ref,context)
                            if reader.input_contract!=record['contract']:
                                issues.append(PlanIssue('s2.family_input_mismatch'));results.append('unknown');continue
                            output=reader.read(ref,context)
                            if not isinstance(output,PlanOp) or not isinstance(output.value,InterpretedValue) or output.value.contract!=reader.output_contract:
                                issues.append(PlanIssue('s2.reader_result_contract'));results.append('unknown');continue
                            if ref not in output.value.subjects:
                                issues.append(PlanIssue('s2.reader_scope_mismatch'));results.append('unknown')
                            if output.state!='completed' or output.value.limits:
                                limits=output.diagnostics or output.value.limits or (PlanIssue('s2.family_interpretation_unestablished'),)
                                issues.extend(limits);results.append('fail' if any(i.code=='s2.constraint_failed' for i in limits) else 'unknown')
                    if name!='s2.interpret':
                        procedure=context.procedures.lookup(profile)
                        if procedure is None:
                            issues.append(PlanIssue('s2.profile_procedure_unavailable'));results.append('not_checked')
                        else:
                            output=procedure.assess(tuple(roots),tuple(claim['evidence']),(),context)
                            if not isinstance(output,PlanOp) or not output.value:
                                issues.append(PlanIssue('s2.profile_result_unestablished'));results.append('unknown')
                            else:
                                if output.state!='completed':
                                    issues.extend(output.diagnostics or (PlanIssue('s2.profile_procedure_incomplete'),));results.append('unknown')
                                for ref in output.value:
                                    p=get(ref,context,'s2.assessment')['payload']
                                    if p['claim']!=profile or any(r not in p['subjects'] for r in roots):raise ServiceError('s2.procedure_assessment_scope_mismatch')
                                    results.append(p['result'])
                if not results:results.append('pass')
            result='fail' if 'fail' in results else 'not_checked' if 'not_checked' in results else 'unknown' if 'unknown' in results else 'pass'
            if result!='pass' and not issues:issues.append(PlanIssue('s2.profile_prerequisite_not_passed'))
            ref=assessment(tx,context,profile,roots,claim['evidence'],result,issues)
            assessments.append(ref);(satisfied if result=='pass' else withheld).append(claim);allissues.extend(issues)
        return PlanValidationReport(tuple(assessments),tuple(claims),tuple(satisfied),tuple(withheld),tuple(allissues)),(),assessments
    return atomic(context,build)
