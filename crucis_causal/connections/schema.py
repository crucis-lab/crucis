"""SC-1 closed JSON Schema transcription (DLV-08, DLV-09).

Static field declarations transcribed from the accepted design; no runtime doc parsing
or external schema retrieval. JSON Schema 2020-12, validated with jsonschema.
"""
from functools import lru_cache
from .model import VERSION

ID_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
QNAME_PATTERN = r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$"
INTEGER_PATTERN = r"^-?(0|[1-9][0-9]*)$"
DECIMAL_PATTERN = r"^-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?$"
PAYLOAD_FIELDS = {
  "s1.component": {
    "name": "String",
    "role": "Code",
    "version": "K(String)",
    "implementation": "K(PayloadRef)",
    "configuration": "K(Ref(configuration))",
    "source": "Source"
  },
  "s1.configuration": {
    "component": "Ref(component)",
    "explicit_settings": "Ref(artifact_snapshot)",
    "resolved_defaults": "K(Ref(artifact_snapshot))",
    "scope": "Scope",
    "source": "Source"
  },
  "s1.request": {
    "operation": "Contract",
    "task_scope": "Scope",
    "deliverables": "Deliverable[]",
    "completion": "Contract",
    "completion_parameters": "Ref[]",
    "presentation_policy": "Ref(policy)",
    "resource_policy": "K(Ref(policy))",
    "recovery_policy": "K(Ref(policy))",
    "route": "Code",
    "source": "Source"
  },
  "s1.attempt": {
    "request": "Ref(request)",
    "native_identity": "K(NativeIdentity)",
    "initial_state": "K(Ref(output))",
    "binding": "K(Ref(binding))",
    "source": "Source"
  },
  "s1.connection_observation": {
    "subjects": "Ref[]",
    "request": "Ref(request)",
    "native_subject": "Ref(component)",
    "information": "IndexList(Ref(presentation))",
    "observations": "Ref(observation)[]",
    "gaps": "Ref(gap)[]",
    "outputs": "IndexList(Ref(output))",
    "artifacts": "IndexList(Ref(artifact_snapshot|artifact_declaration))",
    "context": "Ref[]",
    "checks": "Ref(check)[]"
  },
  "s1.observation": {
    "subject": "Ref",
    "proposition": "Ref(proposition)",
    "value": "ObservationValue",
    "scope": "Scope",
    "source_time": "K(Time)",
    "capture_time": "K(Time)",
    "source": "Source",
    "event": "K(Ref(event))"
  },
  "s1.gap": {
    "subjects": "Ref[]",
    "reasons": "Code[]",
    "scope": "Scope",
    "source": "Source"
  },
  "s1.assessment": {
    "subjects": "Ref[]",
    "rule": "Contract",
    "parameters": "Ref[]",
    "basis": "Ref[]",
    "conclusions": "Conclusion[]",
    "cutoff": "Ref[]",
    "revises": "Ref(assessment)[]"
  },
  "s1.variable": {
    "namespace": "Ref(component|domain|schema|output)",
    "meaning": "K(String)",
    "roles": "K(Code[])",
    "value_space": "K(ValueSpace)",
    "source": "Source",
    "derivation": "Ref[]"
  },
  "s1.domain": {
    "domain_kind": "finite|relative_temporal|absolute_temporal|component|grouped|learned|native_extension",
    "members": "DomainMember[]",
    "coordinate_contract": "K(Contract)",
    "extent": "Code",
    "source": "Source"
  },
  "s1.schema": {
    "payload": "PayloadRef",
    "axes": "Axis[]",
    "labels": "Label[]",
    "encoding": "Contract",
    "domain": "Ref(domain)",
    "source": "Source"
  },
  "s1.mapping": {
    "mapping_kind": "permutation|partial_correspondence|value_conversion|feature_construction|semantic_alignment|native_decode",
    "from": "Ref(domain|schema)",
    "to": "Ref(domain|schema)",
    "entries": "MappingEntry[]",
    "procedure": "Ref(component)",
    "purpose": "Code",
    "coverage": "Scope",
    "properties": "Ref(proposition)[]",
    "checks": "Ref(check)[]",
    "source": "Source"
  },
  "s1.proposition": {
    "predicate": "Contract",
    "arguments": "Argument[]",
    "conditioning": "Ref(proposition)[]",
    "scope": "Scope"
  },
  "s1.output": {
    "output_type": "graph|claims|set|order|ranking|quantity|collection|model_reference|message|diagnostic|abstention|native_report",
    "native_producer": "Ref(component)",
    "subjects": "Ref[]",
    "role": "K(Code)",
    "designation": "K(Code)",
    "body": "OutputBody",
    "source": "Source",
    "relations": "Ref(relation)[]",
    "checks": "Ref(check)[]"
  },
  "s1.artifact_snapshot": {
    "content": "BytePayload",
    "format": "K(Contract)",
    "capture_scope": "ByteScope",
    "source_span": "K(ByteScope)",
    "native_capture_extent": "Code",
    "locations": "Ref(location)[]",
    "digest_claims": "Ref(observation)[]",
    "source": "Source"
  },
  "s1.artifact_declaration": {
    "native_identity": "K(NativeIdentity)",
    "reported_format": "K(Contract)",
    "locations": "Ref(location)[]",
    "claims": "Ref(observation)[]",
    "source": "Source"
  },
  "s1.location": {
    "locator": "String",
    "access_contract": "Contract",
    "expected_snapshot": "Ref(artifact_snapshot)",
    "retrievals": "Ref(observation)[]",
    "automatic_access": "false"
  },
  "s1.check": {
    "procedure": "Ref(component)",
    "contract_checked": "Contract",
    "subjects": "Ref[]",
    "inputs": "Ref[]",
    "scope": "Scope",
    "result": "pass|fail|unknown|not_checked",
    "diagnostics": "Ref(gap)[]",
    "source": "Source"
  },
  "s1.relation": {
    "relation_contract": "Contract",
    "endpoints": "Endpoint[]",
    "parameters": "Ref[]",
    "scope": "Scope",
    "source": "Source"
  },
  "s1.selection": {
    "purpose": "Code",
    "selected": "Ref[]",
    "rule": "Contract",
    "basis": "Ref[]",
    "source": "Source"
  },
  "s1.binding": {
    "request": "Ref(request)",
    "adapter": "Ref(component)",
    "route": "Code",
    "presented": "Ref(presentation)[]",
    "resolved_configuration": "Ref(configuration)[]",
    "prerequisites": "Ref(check)[]",
    "state": "ready|not_ready|unresolved",
    "gaps": "Ref(gap)[]"
  },
  "s1.presentation": {
    "information_contract": "Contract",
    "payload": "K(PayloadRef)",
    "endpoint": "K(Ref(endpoint))",
    "domain": "K(Ref(domain))",
    "schema": "K(Ref(schema))",
    "recipient": "Ref(component)",
    "state": "intended|permitted|delivered|access_observed|use_claimed",
    "attempt": "Ref(attempt)",
    "source": "Source"
  },
  "s1.policy": {
    "policy_contract": "Contract",
    "parameters": "Ref[]",
    "scope": "Scope",
    "authority": "K(Ref(component))",
    "source": "Source"
  },
  "s1.import_receipt": {
    "import_occurrence": "ID",
    "sources": "Ref(artifact_snapshot|artifact_declaration)[]",
    "reader": "Ref(component)",
    "configuration": "K(Ref(configuration))",
    "operation_policy": "Contract",
    "result_roots": "Ref[]",
    "native_occurrence": "K(NativeIdentity)",
    "source": "Source"
  },
  "s1.session": {
    "request": "Ref(request)",
    "native_identity": "K(NativeIdentity)",
    "parent": "K(Ref(session))",
    "membership": "IndexList(Ref)",
    "completion_rule": "Contract",
    "source": "Source"
  },
  "s1.event": {
    "subject": "Ref",
    "actor": "Ref(component)",
    "event_contract": "Contract",
    "content": "Ref",
    "native_time": "K(Time)",
    "local_sequence": "K(Sequence)",
    "predecessors": "Ref(event)[]",
    "correlation": "K(String)",
    "source": "Source"
  },
  "s1.endpoint": {
    "owner": "Ref(component)",
    "operation": "Contract",
    "request_contract": "Contract",
    "response_contract": "Contract",
    "input_domains": "Ref(domain)[]",
    "allowed_information": "Ref(policy)",
    "transport": "Contract",
    "source": "Source"
  },
  "s1.authority_evidence": {
    "actor": "Ref(component)",
    "policy": "Ref(policy)",
    "operation": "Contract",
    "subjects": "Ref[]",
    "permitted_effects": "Code[]",
    "decision": "permitted|denied|unresolved",
    "validity": "Scope",
    "source": "Source"
  },
  "s1.action_request": {
    "session": "Ref(session)",
    "attempt": "Ref(attempt)",
    "requester": "Ref(component)",
    "endpoint": "Ref(endpoint)",
    "arguments": "Ref[]",
    "question": "K(Ref(proposition))",
    "authority": "Ref(authority_evidence)",
    "native_action_identity": "K(NativeIdentity)",
    "source": "Source"
  },
  "s1.action_response": {
    "request": "Ref(action_request)",
    "responder": "Ref(component)",
    "content": "Ref[]",
    "response_state": "returned|abstained|rejected|failed|unresolved",
    "delivery": "Ref(presentation)[]",
    "source": "Source"
  },
  "s1.transmission": {
    "message": "Ref(action_request|action_response)",
    "sender": "Ref(component)",
    "recipient": "Ref(component)",
    "transport": "Contract",
    "native_receipt": "K(NativeIdentity)",
    "outcome": "submitted|acknowledged|rejected|contact_lost|unresolved",
    "source": "Source"
  },
  "s1.recovery": {
    "successor": "Ref(attempt)",
    "predecessor": "Ref(attempt)",
    "recovery_kind": "retry|checkpoint_continuation|warm_start|branch",
    "request_relation": "same_request|new_request",
    "state": "K(Ref(output))",
    "load": "K(Ref(state_load))",
    "reason": "K(Code)",
    "policy": "Ref(policy)",
    "source": "Source"
  },
  "s1.state_load": {
    "attempt": "Ref(attempt)",
    "snapshot": "Ref(output)",
    "requested_components": "Code[]",
    "observed_components": "StateComponent[]",
    "configuration_before": "Ref(configuration)[]",
    "configuration_after": "Ref(configuration)[]",
    "continuity": "exact_within_scope|partial|unresolved|contradicted",
    "scope": "Scope",
    "source": "Source"
  },
  "s1.replay": {
    "request": "Ref(request)",
    "attempt": "Ref(attempt)",
    "source_attempt": "Ref(attempt)",
    "transcript": "Ref(artifact_snapshot)",
    "match_rule": "Contract",
    "match_parameters": "Ref[]",
    "consumed": "ReplayMatch[]",
    "unmatched": "Ref(action_request)[]",
    "exhaustion": "stop|return_unresolved",
    "fresh_fallback": "forbidden",
    "source": "Source"
  },
  "s1.accounting": {
    "scope": "Scope",
    "quantities": "Ref(output)[]",
    "members": "Ref[]",
    "aggregation": "Contract",
    "coverage": "disjoint_members|inclusive_total|overlapping|unresolved",
    "revised": "Ref(accounting)[]",
    "source": "Source"
  },
  "s1.cancellation": {
    "subject": "Ref(attempt|session|action_request)",
    "requester": "Ref(component)",
    "policy": "Ref(policy)",
    "requested": "Ref(event)",
    "acknowledgment": "K(Ref(event))",
    "observed_stop": "K(Ref(event))",
    "source": "Source"
  }
}
BODY_FIELDS = {
  "graph": {
    "family": "Contract",
    "domain": "Ref(domain)",
    "coverage": "PairDomain",
    "omission": "Omission",
    "links": "Link[]",
    "native_assertions": "Ref(proposition)[]",
    "quantities": "Ref(output)[]"
  },
  "claims": {
    "propositions": "Ref(proposition)[]",
    "decisions": "Decision[]",
    "coverage": "Scope",
    "omission": "Code"
  },
  "set": {
    "predicate": "Contract",
    "targets": "Member[]",
    "candidates": "Ref(domain)",
    "members": "Member[]",
    "decisions": "Decision[]",
    "coverage": "Scope",
    "omission": "Code"
  },
  "order": {
    "predicate": "Contract",
    "domain": "Ref(domain)",
    "representation": "sequence|relation_pairs|cover_pairs",
    "sequence": "Member[]",
    "pairs": "MemberPair[]",
    "coverage": "Scope",
    "omission": "Code"
  },
  "ranking": {
    "predicate": "Contract",
    "domain": "Ref(domain)",
    "groups": "Member[][]",
    "direction": "earlier_higher|earlier_lower",
    "unranked": "Member[]",
    "excluded": "Member[]",
    "quantities": "Ref(output)[]"
  },
  "quantity": {
    "quantity_kind": "Code",
    "subject": "Ref",
    "value": "K(Number)|Tensor|Interval",
    "units": "K(Unit)",
    "conditioning": "Ref(proposition)[]",
    "basis": "K(Ref)",
    "procedure": "Ref(component)",
    "associated_rule": "K(Contract)"
  },
  "collection": {
    "collection_kind": "sequence|set|multiset|sample_bank|weighted_support|finite_measure",
    "member_contracts": "Contract[]",
    "members": "CollectionMember[]",
    "extent": "Scope",
    "ordering": "native_sequence|explicit_order|unordered",
    "generation": "K(Ref)",
    "weights": "Ref(output)[]"
  },
  "model_reference": {
    "model_role": "Code",
    "artifacts": "PayloadRef[]",
    "input_domains": "Ref(domain)[]",
    "output_domains": "Ref(domain)[]",
    "dependencies": "Ref[]",
    "associated": "Ref[]",
    "reader": "K(Contract)",
    "state_coverage": "IndexList(Ref)"
  },
  "message": {
    "message_kind": "action_request|action_response|native_message",
    "content": "Ref",
    "correlation": "Ref",
    "operation": "Contract",
    "participants": "Endpoint[]"
  },
  "diagnostic": {
    "code": "Code",
    "phase": "Code",
    "subjects": "Ref[]",
    "attribution": "K(Ref(component))",
    "details": "Ref(artifact_snapshot)[]",
    "source_error": "K(String)"
  },
  "abstention": {
    "query": "Ref(proposition|request)",
    "reason": "K(Code)",
    "scope": "Scope"
  },
  "native_report": {
    "type_claim": "K(Contract)",
    "payload": "PayloadRef",
    "interpretation_gap": "Ref(gap)[]"
  }
}

# Primitive/supporting shapes use the same closed notation as the payload catalog.
SHAPES = {
 "Contract": {"name":"QName","version":"NonemptyString"},
 "Scope": {"subjects":"Ref[]","qualifiers":"Ref[]"},
 "Source": {"basis":"reported|observed|reconstructed|derived|intrinsic","evidence":"Ref[]","procedure":"K(Ref(component))","inputs":"Ref[]"},
 "PayloadRef": {"artifact":"Ref(artifact_snapshot)","selector":"K(Selector)"},
 "ExternalPackage": {"package_id":"ID","locator":"K(String)","expected_digest":"K(Digest)","access":"Code"},
 "Extension": {"contract":"Contract","affects":"Ref[]","critical_for":"Code[]","payload":"BytePayload"},
 "Unit": {"name":"String","convention":"Contract"},
 "NativeIdentity": {"authority":"String","namespace":"String","native_id":"String","source":"Source"},
 "Deliverable": {"role":"Code","contract":"Contract","scope":"Scope","required":"Boolean","abstention":"allowed|forbidden"},
 "Conclusion": {"facet":"Code","value":"K(ObservationValue)","supporting":"Ref[]","disputed":"Ref[]"},
 "Argument": {"role":"Code","value":"Member|Ref|Number|String|Boolean"},
 "Member": {"domain":"Ref(domain)","key":"String"},
 "DomainMember": {"key":"String","variable":"Ref(variable)","coordinates":"Coordinate[]"},
 "Coordinate": {"dimension":"Contract","value":"String|Number|Ref","reference":"K(Ref)"},
 "Axis": {"name":"Code","axis_kind":"variable|sample|component|time|native","length":"Index","coordinates":"AxisCoordinate[]","index_base":"zero|one"},
 "AxisCoordinate": {"key":"String","member":"K(Member)","value":"K(String|Number|Ref)"},
 "Label": {"member":"Member","text":"String","audience":"Code"},
 "MappingEntry": {"from":"Member[]","to":"Member[]","source":"Source"},
 "ValueSpace": {"space_type":"boolean|categorical|ordered_categorical|integer|real|tensor|native_extension","contract":"Contract","units":"K(Unit)","levels":"Ref[]","axes":"Ref(domain)[]","missing":"Contract"},
 "Endpoint": {"role":"Code","target":"Ref"},
 "PairDomain": {"pairing":"ordered|unordered","domain":"Ref(domain)","include_same_node":"Boolean","pairs":"MemberPair[]","extent":"all_in_domain|listed_only"},
 "MemberPair": {"left":"Member","right":"Member"},
 "Omission": {"within_coverage":"asserted_absence|unreported|explicit_only|unresolved","outside_coverage":"no_assertion"},
 "Link": {"key":"String","left":"Member","right":"Member","relation":"Contract","endpoint_marks":"Code[]","properties":"Ref(proposition)[]","quantities":"Ref(output)[]"},
 "Decision": {"proposition":"Ref(proposition)","decision":"assert|deny|abstain|native_unresolved","reason":"K(Code)","source":"Source"},
 "CollectionMember": {"key":"String","object":"Ref(output)","multiplicity":"Index","associated":"Endpoint[]"},
 "Tensor": {"value_type":"tensor","payload":"PayloadRef","axes":"Ref(schema)","entry_contract":"Contract","missing":"Contract"},
 "Interval": {"value_type":"interval","lower":"K(Number)","upper":"K(Number)","lower_inclusive":"Boolean","upper_inclusive":"Boolean","construction":"Contract","level":"K(Number)","target":"Ref"},
 "Sequence": {"stream":"String","position":"Index","producer":"Ref(component)"},
 "StateComponent": {"component":"Code","identity":"K(String)","availability":"K(Ref(artifact_snapshot))","loaded":"K(Boolean)","evidence":"Ref[]"},
 "ReplayMatch": {"action":"Ref(action_request)","source_event":"Ref(event)","response":"Ref(action_response)","match_scope":"Scope","occurrence_key":"String","checks":"Ref(check)[]"},
}
ALIASES = {
 "ObservationValue":"Boolean|String|Number|Ref|Ref[]",
}
VARIANTS = {
 "Number": [
  {"number_type":"integer","text":"IntegerText"},
  {"number_type":"finite_decimal","text":"DecimalText"},
  {"number_type":"nonfinite","value":"positive_infinity|negative_infinity|nan"}],
 "Time": [
  {"time_type":"utc_instant","value":"String","precision":"second|fractional_second","clock":"K(Ref(component))","uncertainty_seconds":"K(Number)"},
  {"time_type":"native_report","text":"String","timezone":"K(String)","precision":"K(String)"}],
 "BytePayload": [
  {"content_form":"inline_utf8","text":"String"},
  {"content_form":"inline_base64","data":"String"},
  {"content_form":"external_snapshot","locations":"Ref(location)[]","digest":"K(Digest)"}],
 "ByteScope": [{"kind":"full_content"},{"kind":"byte_range","start":"Index","end_exclusive":"Index"}],
 "Selector": [
  {"selector_type":"json_pointer","pointer":"String"},
  {"selector_type":"byte_range","start":"Index","end_exclusive":"Index"},
  {"selector_type":"member_key","key":"String","member_contract":"Contract"},
  {"selector_type":"array_coordinate","axes":"Ref(schema)","coordinates":"Index[]"},
  {"selector_type":"archive_member","name":"String","member_digest":"K(Digest)"}],
}

def _split(expr):
    depth, start, parts = 0, 0, []
    for i, ch in enumerate(expr):
        if ch == "(": depth += 1
        elif ch == ")": depth -= 1
        elif ch == "|" and depth == 0:
            parts.append(expr[start:i]); start = i + 1
    return parts + [expr[start:]]

def _object(properties, required=None):
    return {"type":"object","properties":properties,"required":list(properties) if required is None else required,"additionalProperties":False}

def _reference(kinds=None):
    target = {"enum":["s1."+k for k in kinds]} if kinds else {"$ref":"#/$defs/QName"}
    shared = {"target":{"$ref":"#/$defs/ID"},"target_type":target}
    return {"oneOf":[
        _object({"binding":{"const":"internal"}, **shared}),
        _object({"binding":{"const":"external"},"package_id":{"$ref":"#/$defs/ID"}, **shared}),
        _object({"binding":{"const":"unresolved"},"target_type":target,"reason":{"$ref":"#/$defs/Code"},
                 "evidence":{"type":"array","items":{"$ref":"#/$defs/Ref"}},"source_labels":{"type":"array","items":{"type":"string"}}})
    ]}

def type_schema(expr):
    parts = _split(expr)
    if len(parts)>1: return {"anyOf":[type_schema(p) for p in parts]}
    if expr.endswith("[]"): return {"type":"array","items":type_schema(expr[:-2])}
    if expr.startswith("Ref("): return _reference(expr[4:-1].split("|"))
    if expr.startswith("K("):
        return {"oneOf":[
            _object({"state":{"const":"known"},"value":type_schema(expr[2:-1]),"basis":type_schema("Ref[]")}),
            _object({"state":{"const":"unresolved"},"reasons":{**type_schema("Code[]"),"minItems":1},"evidence":type_schema("Ref[]")}),
            _object({"state":{"const":"not_applicable"},"rule":type_schema("Contract"),"scope":type_schema("Ref[]")})]}
    if expr.startswith("IndexList("):
        return _object({"members":type_schema(expr[10:-1]+"[]"),"extent":{"enum":["complete_for_scope","partial_for_scope","not_examined","unresolved"]},"scope":type_schema("Scope"),"gaps":type_schema("Ref(gap)[]")})
    if expr == "true": return {"const":True}
    if expr == "false": return {"const":False}
    if expr[0].islower(): return {"const":expr}
    return {"$ref":"#/$defs/"+expr}

def fields_schema(fields):
    props = {key.rstrip("?"):type_schema(value) for key,value in fields.items()}
    return _object(props, [key for key in fields if not key.endswith("?")])

@lru_cache(maxsize=1)
def _schema():
    defs = {
        "String":{"type":"string"}, "NonemptyString":{"type":"string","minLength":1},
        "Boolean":{"type":"boolean"}, "ID":{"type":"string","pattern":ID_PATTERN},
        "QName":{"type":"string","pattern":QNAME_PATTERN},
        "Code":{"type":"string","pattern":QNAME_PATTERN},
        "IntegerText":{"type":"string","pattern":INTEGER_PATTERN},
        "DecimalText":{"type":"string","pattern":DECIMAL_PATTERN},
        "Index":{"type":"string","pattern":r"^(0|[1-9][0-9]*)$"},
        "Ref":_reference(),
    }
    defs.update({name:fields_schema(fields) for name,fields in SHAPES.items()})
    defs.update({name:type_schema(expr) for name,expr in ALIASES.items()})
    defs.update({name:{"oneOf":[fields_schema(fields) for fields in cases]} for name,cases in VARIANTS.items()})
    defs["Digest"] = _object({"algorithm":{"const":"sha256"},"value":{"type":"string","pattern":"^[0-9a-f]{64}$"},"byte_length":type_schema("Index"),"scope":type_schema("ByteScope")})
    defs["OutputBody"] = {"anyOf":[fields_schema(fields) for fields in BODY_FIELDS.values()]}
    record_cases = []
    for name, fields in PAYLOAD_FIELDS.items():
        payload = fields_schema(fields)
        if name == "s1.output":
            payload = fields_schema({**fields,"body":"OutputBody"})
            payload["allOf"]=[{"if":{"properties":{"output_type":{"const":kind}}},
                               "then":{"properties":{"body":{"$ref":"#/$defs/Body_"+kind}}}} for kind in BODY_FIELDS]
        record_cases.append({"if":{"properties":{"record_type":{"const":name}}},
                             "then":{"properties":{"contract":_object({"name":{"const":name},"version":{"const":VERSION}}),"payload":payload}}})
    for name, fields in BODY_FIELDS.items(): defs["Body_"+name]=fields_schema(fields)
    defs["Record"]=_object({"id":type_schema("ID"),"record_type":{"enum":list(PAYLOAD_FIELDS)},
                            "contract":type_schema("Contract"),"producer":type_schema("Ref(component)"),
                            "created_at":type_schema("K(Time)"),"payload":{"type":"object"},"extensions":type_schema("Extension[]")})
    defs["Record"]["allOf"]=record_cases
    package = _object({"format":_object({"name":{"const":"s1.connection_package"},"version":{"const":VERSION}}),
                       "package_id":type_schema("ID"),"roots":{**type_schema("Ref[]"),"minItems":1},
                       "records":type_schema("Record[]"),"external_packages":type_schema("ExternalPackage[]"),
                       "extensions":type_schema("Extension[]")})
    return {"$schema":"https://json-schema.org/draft/2020-12/schema","$id":"urn:dsc180:s1:sc1:"+VERSION,
            "title":"SC-1 connection package (DLV-08, DLV-09)",**package,"$defs":defs}


def schema():
    """A caller may inspect/edit its copy without changing subsequent validators."""
    import copy
    return copy.deepcopy(_schema())

