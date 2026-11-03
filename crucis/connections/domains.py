"""Reusable variable identity, coordinate maps and views; DLV-08, DLV-09."""
import copy
import uuid
from .codec import WireError
from .model import contract, known, reference, scope, source, unresolved


def finite_domain(builder, names, evidence=(), namespace=None, roles=None):
    """Labels can repeat. Source-scoped variable IDs, not labels, establish identity."""
    members=[]
    for i,name in enumerate(names):
        var=builder.add("variable",{"namespace":namespace or builder.producer,"meaning":known(str(name),evidence),
            "roles":known(roles,evidence) if roles is not None else unresolved(),"value_space":unresolved(),
            "source":source("reported",evidence,builder.producer),"derivation":[]})
        members.append({"key":str(i),"variable":var,"coordinates":[]})
    return builder.add("domain",{"domain_kind":"finite","members":members,"coordinate_contract":unresolved(),
        "extent":"s1.full_for_interface","source":source("reported",evidence,builder.producer)})


def member(domain,key):
    return {"domain":copy.deepcopy(domain),"key":str(key)}


def permutation(builder,from_domain,to_domain,pairs,evidence=()):
    entries=[{"from":[member(from_domain,a)],"to":[member(to_domain,b)],"source":source("observed",evidence,builder.producer)} for a,b in pairs]
    return builder.add("mapping",{"mapping_kind":"permutation","from":from_domain,"to":to_domain,
        "entries":entries,"procedure":builder.producer,"purpose":"s1.coordinate_interpretation",
        "coverage":scope(from_domain,to_domain),"properties":[],"checks":[],
        "source":source("observed",evidence,builder.producer)})


def member_map(package,mapping_ref,declared_alignment=False):
    from .semantics import validate
    records={r["id"]:r for r in package["records"]}
    record=records[mapping_ref["target"]]
    report=validate(package)
    if not declared_alignment:report.require(["s1.mapping"],subjects=[record["id"]])
    else:report.require()
    p=record["payload"]
    if p['from'].get('target_type')!='s1.domain' or p['to'].get('target_type')!='s1.domain':
        raise WireError('member-coordinate view requires explicit source/target domains')
    if p["mapping_kind"] not in (("semantic_alignment",) if declared_alignment else ("permutation","partial_correspondence","native_decode")):
        raise WireError("mapping is not a supported identity-coordinate view")
    pairs={}
    for entry in p["entries"]:
        if len(entry["from"])!=1 or len(entry["to"])!=1: raise WireError("coordinate view requires singleton mappings")
        a,b=entry["from"][0],entry["to"][0]
        if a['domain']!=p['from'] or b['domain']!=p['to']:raise WireError('mapping entry is outside its declared source/target domain')
        for m in (a,b):
            d=records.get(m["domain"].get("target"))
            if not d or not any(x["key"]==m["key"] for x in d["payload"]["members"]):raise WireError("unresolved alignment member")
        if (a["domain"]["target"],a["key"]) in pairs:raise WireError("ambiguous mapping source")
        pairs[(a["domain"]["target"],a["key"])]=copy.deepcopy(b)
    if len({_key_pair(v) for v in pairs.values()})!=len(pairs):raise WireError("noninjective coordinate/alignment view needs an explicit aggregation rule")
    return pairs,p


def _key_pair(value):return value["domain"].get("target"),value["key"]


def map_value(value,pairs):
    """Map all nested Member instances, including proposition/quantity/parameter axes."""
    if isinstance(value,dict):
        if set(value)=={"domain","key"}:
            key=(value["domain"].get("target"),value["key"])
            if key not in pairs: raise WireError("unmapped member; no implicit deletion or zero-fill: "+str(key))
            return copy.deepcopy(pairs[key])
        return {k:map_value(v,pairs) for k,v in value.items()}
    if isinstance(value,list):return [map_value(v,pairs) for v in value]
    return copy.deepcopy(value)


def mapped_graph(builder,package,graph_ref,mapping_ref,*,declared_alignment=False):
    pairs,mapping=member_map(package,mapping_ref,declared_alignment)
    records={r["id"]:r for r in package["records"]}
    record=records[graph_ref["target"]];body=record["payload"]["body"]
    if record["payload"]["output_type"]!="graph":raise WireError("graph view needs a graph object")
    if body['domain']!=mapping['from']:raise WireError('graph is not in the mapping source domain; do not map an already converted graph twice')
    if mapping["mapping_kind"]!="permutation" and not declared_alignment:raise WireError("partial graph projection needs explicit coverage/loss policy")
    from .semantics import validate
    if not declared_alignment:validate(package).require(["s1.mapping_identity"],subjects=[mapping_ref["target"]])
    else:
        if {m["key"] for m in records[body["domain"]["target"]]["payload"]["members"]}!={e["from"][0]["key"] for e in mapping["entries"]}:
            raise WireError("partial learned-factor projection requires explicit lost-coverage policy")
        if {m["key"] for m in records[mapping["to"]["target"]]["payload"]["members"]}!={e["to"][0]["key"] for e in mapping["entries"]}:
            raise WireError("unmapped target variables must not acquire negative graph predictions")
    memo={}
    eligible={"s1.output","s1.proposition","s1.schema"}
    def transform(value):
        if isinstance(value,dict):
            if set(value)=={"domain","key"}:return map_value(value,pairs)
            if value.get("binding")=="internal":
                if value==mapping["from"]:return copy.deepcopy(mapping["to"])
                old=records.get(value["target"])
                if old and old["record_type"] in eligible:return clone(value)
                return copy.deepcopy(value)
            return {k:transform(v) for k,v in value.items()}
        if isinstance(value,list):return [transform(v) for v in value]
        return copy.deepcopy(value)
    def clone(ref):
        if ref["target"] in memo:return memo[ref["target"]]
        original=records[ref["target"]]
        newref=reference(str(uuid.uuid4()),original["record_type"])
        memo[ref["target"]]=newref
        payload=transform(original["payload"])
        if "source" in payload:payload["source"]=source("derived",[ref,mapping_ref],builder.producer,[ref,mapping_ref])
        if original["record_type"]=="s1.output":
            payload["role"]=known("s1.derived_view" if declared_alignment else "s1.standardized_interpretation")
            payload["checks"]=[]
        builder.add(original["record_type"],payload,record_id=newref["target"])
        builder.add("relation",{"relation_contract":contract("representation_of"),
            "endpoints":[{"role":"s1.source","target":ref},{"role":"s1.view","target":newref}],
            "parameters":[mapping_ref],"scope":scope(ref,newref),
            "source":source("derived",[ref,mapping_ref],builder.producer,[ref,mapping_ref])})
        return newref
    with builder.transaction():return clone(graph_ref)


def graph_body(domain,links,family="directed_graph",coverage=None,omission="asserted_absence"):
    return {"family":contract(family),"domain":domain,
        "coverage":coverage or {"pairing":"ordered","domain":domain,"include_same_node":False,"pairs":[],"extent":"all_in_domain"},
        "omission":{"within_coverage":omission,"outside_coverage":"no_assertion"},"links":links,
        "native_assertions":[],"quantities":[]}


def directed_link(domain,a,b,key=None):
    return {"key":key or str(a)+"->"+str(b),"left":member(domain,a),"right":member(domain,b),
        "relation":contract("direct_relation"),"endpoint_marks":[],"properties":[],"quantities":[]}
