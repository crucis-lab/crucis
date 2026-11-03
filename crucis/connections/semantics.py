"""Named semantic checks on supported contracts, not scientific truth (DLV-08/09)."""
import json
from decimal import Decimal
from fractions import Fraction
from .model import VERSION
from .validation import Check, Issue, decimal_value, validate_wire, walk
from .evidence import integrity_checks


def _cycle(edges):
    children={};degree={}
    for a,b in set(edges):
        children.setdefault(a,[]).append(b);degree.setdefault(a,0);degree[b]=degree.get(b,0)+1
    ready=[n for n,d in degree.items() if d==0];seen=0
    while ready:
        n=ready.pop();seen+=1
        for child in children.get(n,()):
            degree[child]-=1
            if degree[child]==0:ready.append(child)
    return seen!=len(degree)


def _key(member):return member["domain"].get("target"),member["key"]


def validate(package, *, resolver=None, profiles=()):
    report=validate_wire(package)
    if not report.ok:return report
    records={r["id"]:r for r in package["records"]}
    def get(ref,kind=None):
        if ref.get("binding")!="internal":return None
        rec=records.get(ref["target"])
        return rec if rec and (kind is None or rec["record_type"]=="s1."+kind) else None
    def check(subject,name,condition,details=""):
        result="unknown" if condition is None else "pass" if condition else "fail"
        report.checks.append(Check(subject,"s1."+name,result,details))
    def member_exists(m):
        d=get(m["domain"],"domain")
        return d is not None and any(x["key"]==m["key"] for x in d["payload"]["members"])
    integrity_checks(package,report,resolver)
    for r in package["records"]:
        rid,p,kind=r["id"],r["payload"],r["record_type"]
        if kind=='s1.connection_observation':
            producer=get(r['producer'],'component')
            identified=producer is not None and producer['payload']['version']['state']=='known' and producer['payload']['implementation']['state']=='known'
            indexes=[p['information'],p['outputs'],p['artifacts']]
            indexed=all(not (v['extent']=='not_examined' and v['members']) for v in indexes)
            check(rid,'connection_minimum',bool(p['observations'] or p['gaps']) and identified and indexed,
                  'new observer identity and at least one scoped observation/gap; no original attempt is required')
        elif kind=="s1.domain":
            keys=[m["key"] for m in p["members"]]
            identities=[]
            for m in p["members"]:
                coords=[]
                for c in m["coordinates"]:
                    v=c["value"]
                    if isinstance(v,dict) and "number_type" in v:
                        n=decimal_value(v);v=str(Fraction(n)) if n.is_finite() else v
                    coords.append((json.dumps(c["dimension"],sort_keys=True),json.dumps(v,sort_keys=True)))
                identities.append((m["variable"].get("target"),tuple(sorted(coords))))
            known_identity=all(m["variable"]["binding"]=="internal" for m in p["members"])
            ok=len(keys)==len(set(keys)) and (not known_identity or len(identities)==len(set(identities)))
            check(rid,"domain",False if not ok else True if known_identity else None,"unique keys and established variable-coordinate identities")
            if p["domain_kind"] in ("relative_temporal","absolute_temporal"):
                check(rid,"temporal_domain",bool(p["members"]) and all(m["coordinates"] for m in p["members"]) and p["coordinate_contract"]["state"]=="known")
            if p["domain_kind"]=="native_extension":check(rid,"domain_extension",None,"reader-specific domain semantics not supplied")
        elif kind=="s1.schema":
            ok=True
            for axis in p["axes"]:
                coords=axis["coordinates"]
                ok &= len(coords)==int(axis["length"]) and len({c["key"] for c in coords})==len(coords)
                if axis["axis_kind"]=="variable":ok &= all(c["member"]["state"]=="known" and member_exists(c["member"]["value"]) for c in coords)
            check(rid,"axes",ok,"sample/time coordinates are not assumed causal variables")
        elif kind=="s1.mapping":
            entries=p["entries"];flat_from=[x for e in entries for x in e["from"]];flat_to=[x for e in entries for x in e["to"]]
            ok=all(member_exists(x) for x in flat_from+flat_to)
            if p["mapping_kind"] in ("permutation","partial_correspondence","native_decode"):
                ok &= all(len(e["from"])==len(e["to"])==1 for e in entries)
                ok &= len({_key(x) for x in flat_from})==len(flat_from) and len({_key(x) for x in flat_to})==len(flat_to)
                if p["mapping_kind"]=="permutation":
                    a,b=get(p["from"],"domain"),get(p["to"],"domain")
                    if not a or not b:check(rid,"mapping",None,"domain resolution required");continue
                    ok &= {_key(x) for x in flat_from}=={(a["id"],m["key"]) for m in a["payload"]["members"]}
                    ok &= {_key(x) for x in flat_to}=={(b["id"],m["key"]) for m in b["payload"]["members"]}
                    if not ok:
                        check(rid,"mapping",False,"invalid permutation coverage");continue
                    amap={m["key"]:m for m in a["payload"]["members"]};bmap={m["key"]:m for m in b["payload"]["members"]}
                    identical=True
                    for e in entries:
                        va,vb=amap[e["from"][0]["key"]]["variable"],bmap[e["to"][0]["key"]]["variable"]
                        ca,cb=amap[e["from"][0]["key"]]["coordinates"],bmap[e["to"][0]["key"]]["coordinates"]
                        identical &= va==vb and ca==cb
                    check(rid,"mapping_identity",True if identical else None,"established shared variable/coordinate identities; labels are not evidence")
                check(rid,"mapping",ok,"coverage/uniqueness and explicit identity basis; no inferred invertibility")
            else:check(rid,"mapping",None,"feature/value/alignment transform requires its declared procedure checks")
        elif kind=="s1.proposition":
            args=p["arguments"];roles=[a["role"] for a in args]
            ok=len(roles)==len(set(roles))
            ok &= all(member_exists(v) for _,v in walk(args) if isinstance(v,dict) and set(v)=={"domain","key"})
            expected={"s1.direct_relation":{"s1.cause","s1.effect"},"s1.adjacent":{"s1.left","s1.right"},
                "s1.ancestor":{"s1.ancestor","s1.descendant"},"s1.conditional_independence":{"s1.left","s1.right","s1.given"},
                "s1.member_of":{"s1.member","s1.set"},"s1.precedes":{"s1.before","s1.after","s1.order"},
                "s1.native_property":{"s1.subject","s1.property","s1.value"}}
            name=p["predicate"]["name"]
            values={a["role"]:a["value"] for a in args}
            member_roles={"s1.direct_relation":["s1.cause","s1.effect"],"s1.adjacent":["s1.left","s1.right"],
                          "s1.ancestor":["s1.ancestor","s1.descendant"],"s1.precedes":["s1.before","s1.after"],
                          "s1.member_of":["s1.member"]}
            for role in member_roles.get(name,()):
                v=values.get(role)
                ok &= isinstance(v,dict) and set(v)=={"domain","key"} and member_exists(v)
            if name=="s1.ancestor" and values.get("s1.ancestor")==values.get("s1.descendant"):ok=False
            if name=="s1.conditional_independence":
                ok &= all(isinstance(values.get(role),dict) and get(values[role],"domain") is not None for role in ("s1.left","s1.right","s1.given"))
            if name=="s1.native_property":
                import re
                ok &= isinstance(values.get("s1.subject"),dict) and "binding" in values["s1.subject"]
                ok &= isinstance(values.get("s1.property"),str) and re.fullmatch(r"[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+",values["s1.property"]) is not None
            check(rid,"proposition",ok and set(roles)==expected[name] if name in expected and p["predicate"]["version"]==VERSION else None)
        elif kind=="s1.output":
            body=p["body"];typ=p["output_type"]
            if typ=="graph":
                d=get(body["domain"],"domain");keys=set(m["key"] for m in d["payload"]["members"]) if d else set()
                links=body["links"];family=body["family"]["name"]
                ok=d is not None and len({l["key"] for l in links})==len(links)
                ok &= all(member_exists(l[side]) and l[side]["domain"]==body["domain"] for l in links for side in ("left","right"))
                ok &= body["coverage"]["domain"]==body["domain"]
                ok &= body["coverage"]["extent"]!="all_in_domain" or not body["coverage"]["pairs"]
                ok &= all(len(l["endpoint_marks"]) in (0,2) for l in links)
                if not body["coverage"]["include_same_node"]:ok &= all(l["left"]!=l["right"] for l in links)
                pairs=body["coverage"]["pairs"]
                ok &= all(member_exists(pair[side]) and pair[side]["domain"]==body["domain"] for pair in pairs for side in ("left","right"))
                if body["coverage"]["extent"]=="listed_only":
                    def pair_key(a,b):
                        result=(_key(a),_key(b))
                        return result if body["coverage"]["pairing"]=="ordered" else tuple(sorted(result))
                    allowed={pair_key(pair["left"],pair["right"]) for pair in pairs}
                    ok &= all(pair_key(l["left"],l["right"]) in allowed for l in links)
                known_marks=all(m in {"s1.tail","s1.arrowhead","s1.circle"} for l in links for m in l["endpoint_marks"])
                edges=[]
                for l in links:
                    marks=l["endpoint_marks"];relation=l["relation"]["name"]
                    if relation=="s1.direct_relation" and marks not in ([],["s1.tail","s1.arrowhead"]):ok=False
                    if relation=='s1.association' and marks:ok=False
                    if relation=='s1.bidirected_relation' and marks not in ([],['s1.arrowhead','s1.arrowhead']):ok=False
                    if relation=='s1.unresolved_adjacency' and marks not in ([],['s1.tail','s1.tail']):ok=False
                    if relation=="s1.direct_relation" and marks in ([],["s1.tail","s1.arrowhead"]):edges.append((l["left"]["key"],l["right"]["key"]))
                    elif marks==['s1.tail','s1.arrowhead']:edges.append((l['left']['key'],l['right']['key']))
                    elif marks==["s1.arrowhead","s1.tail"]:edges.append((l["right"]["key"],l["left"]["key"]))
                supported_relations={"s1.direct_relation","s1.adjacent","s1.unresolved_adjacency","s1.bidirected_relation","s1.association","s1.endpoint_relation"}
                known_relations=all(l["relation"]["name"] in supported_relations and l["relation"]["version"]==VERSION for l in links)
                check(rid,"graph_encoding",False if not ok else True if known_marks else None)
                if body["family"]["version"]!=VERSION:check(rid,"graph_family",None,"unknown exact family version")
                elif family=="s1.dag":check(rid,"dag",ok and len(edges)==len(links) and not _cycle(edges) if known_relations and known_marks else None)
                elif family in {"s1.directed_graph","s1.partly_directed_graph","s1.endpoint_graph","s1.weighted_graph","s1.association_graph","s1.legacy_graph"}:
                    if family=="s1.directed_graph":ok &= len(edges)==len(links)
                    if family=="s1.association_graph":ok &= all(l["relation"]["name"]=="s1.association" for l in links)
                    if family=="s1.partly_directed_graph":ok &= all("s1.circle" not in l["endpoint_marks"] and l["relation"]["name"]!="s1.bidirected_relation" for l in links)
                    check(rid,"graph_family",ok and known_marks if known_relations else None)
                else:check(rid,"graph_family",None,"full family-conformance checker not supplied; endpoints retained")
            elif typ=="quantity":
                value=body["value"];state=value.get("state")
                if state=="known":
                    n=decimal_value(value["value"]);qkind=body["quantity_kind"]
                    valid=n.is_finite()
                    if qkind in ("s1.probability","s1.p_value","s1.frequency"):valid=n.is_finite() and 0<=n<=1
                    elif qkind=="s1.count":valid=n.is_finite() and n>=0 and n==n.to_integral_value()
                    elif qkind=="s1.duration":valid=n.is_finite() and n>=0
                    elif qkind not in {'s1.coefficient','s1.parameter','s1.weight','s1.currency','s1.reported_cost','s1.score','s1.statistic'}:valid=None
                    check(rid,"quantity_value",valid)
                    if qkind in ('s1.probability','s1.p_value','s1.frequency'):
                        proposition=get(body['subject'],'proposition')
                        check(rid,'quantity_semantics',None,
                            'event/test/statistic meaning requires the exact declared rule reader; numeric range never establishes calibration')
                    check(rid,"quantity_basis",body["basis"]["state"]=="known" or None,"statistical meaning needs a declared native/derived basis")
                elif state in ("unresolved","not_applicable"):check(rid,"quantity_value",None,"quantity value is not established")
                elif value.get("value_type")=="tensor":check(rid,"quantity_tensor",None,"entry reader required")
                elif value.get("value_type")=="interval":
                    lo,hi=value["lower"],value["upper"]
                    result=None
                    if lo["state"]==hi["state"]=="known":
                        a,b=decimal_value(lo["value"]),decimal_value(hi["value"])
                        result=not a.is_nan() and not b.is_nan() and (a<b or a==b and value['lower_inclusive'] and value['upper_inclusive'])
                    check(rid,"interval",result)
    # Later selected families contribute independently scoped checks without changing wire semantics.
    from .families import check_families
    from .evidence import Resolver
    check_families(package,report,resolver or Resolver(package))
    from .history import check_history
    check_history(package,report)
    if profiles:report.require(profiles)
    return report
