"""Selected collection/local/model/tensor contracts; DLV-08, DLV-09.

No averaging, graph selection, factor alignment criterion or scientific metric is
silently chosen. Native declarations remain intact when checks fail.
"""
import io
import json
from decimal import Decimal
from fractions import Fraction

from .codec import WireError, _constant, _pairs
from .model import VERSION
from .validation import Check, decimal_value


def _shape_flat(value):
    if not isinstance(value,list):return (),[value]
    children=[_shape_flat(v) for v in value]
    if children and any(s!=children[0][0] for s,_ in children):raise WireError("ragged tensor has no declared rectangular shape")
    return (len(value),)+(children[0][0] if children else ()),[v for _,vs in children for v in vs]


def tensor_values(value,resolver):
    raw=resolver.select(value["payload"])
    contract=value["entry_contract"]
    name=contract["name"]
    if contract["version"]!=VERSION:raise WireError("unsupported exact tensor entry version")
    if name in {"s1.json_numeric_tensor","s1.json_probability_tensor","s1.json_count_tensor"}:
        if isinstance(raw,bytes):raw=json.loads(raw.decode("utf-8"),parse_float=Decimal,parse_constant=_constant,object_pairs_hook=_pairs)
        # Resolver JSON pointers preserve native source bytes. Use Decimal for a fresh root decode.
        shape,values=_shape_flat(raw)
    elif name in {"s1.npy_numeric_tensor","s1.npy_probability_tensor","s1.npy_count_tensor"}:
        import numpy as np
        if not isinstance(raw,bytes):raise WireError("npy selector must yield exact bytes")
        a=np.load(io.BytesIO(raw),allow_pickle=False)
        if a.dtype.hasobject or a.dtype.kind not in "iuf":raise WireError("unsupported tensor dtype")
        shape,values=a.shape,list(a.flat)
    else:raise WireError("entry reader unsupported: "+name)
    return tuple(shape),values,name


def check_families(package,report,resolver):
    records={r["id"]:r for r in package["records"]}
    def get(ref):return records.get(ref.get("target")) if isinstance(ref,dict) and ref.get("binding")=="internal" else None
    def out(ref):
        r=get(ref);return r["payload"] if r and r["record_type"]=="s1.output" else None
    def member_key(m):return m["domain"].get("target"),m["key"]
    def domain_members(ref):
        d=get(ref)
        return {(d["id"],m["key"]) for m in d["payload"]["members"]} if d and d["record_type"]=="s1.domain" else None
    def valid_member(m):
        members=domain_members(m["domain"])
        return members is not None and member_key(m) in members
    def check(subject,name,condition,details=""):
        report.checks.append(Check(subject,"s1."+name,"unknown" if condition is None else "pass" if condition else "fail",details))
    for record in package["records"]:
        if record["record_type"]!="s1.output":continue
        rid,p=record["id"],record["payload"];body=p["body"];kind=p["output_type"]
        if kind in ("set","claims"):
            decisions=body["decisions"];seen={};consistent=True
            for d in decisions:
                pid=d["proposition"].get("target")
                if pid in seen and seen[pid]!=d["decision"]:consistent=False
                seen[pid]=d["decision"]
            check(rid,"claim_decisions",True if consistent else None,"conflicting native decisions retained; no majority/latest resolution")
            if kind=="set":
                candidates=domain_members(body["candidates"]);members=[member_key(m) for m in body["members"]]
                valid=candidates is not None and len(set(members))==len(members) and set(members)<=candidates
                valid &= all(valid_member(m) for m in body["targets"])
                check(rid,"local_set",valid,"membership scope is the declared candidate domain; no global negatives")
        elif kind=="ranking":
            groups=body["groups"];ranked=[member_key(m) for g in groups for m in g]
            unranked=[member_key(m) for m in body["unranked"]];excluded=[member_key(m) for m in body["excluded"]]
            all_values=ranked+unranked+excluded;domain=domain_members(body["domain"])
            valid=all(groups) and len(all_values)==len(set(all_values)) and domain is not None and set(all_values)<=domain
            complete=domain is not None and set(all_values)==domain
            check(rid,"ranking",valid if complete or not valid else None,"ties preserved; undispositioned domain members remain unresolved, not invented unranked values")
        elif kind=="order":
            from .semantics import _cycle
            domain=domain_members(body["domain"])
            seq=[member_key(m) for m in body["sequence"]]
            pairs=[(member_key(m["left"]),member_key(m["right"])) for m in body["pairs"]]
            valid=domain is not None
            if body["representation"]=="sequence":valid &= not pairs and len(seq)==len(set(seq)) and set(seq)==domain
            else:
                valid &= not seq and len(pairs)==len(set(pairs)) and all(a!=b and a in domain and b in domain for a,b in pairs) if domain is not None else False
                valid &= not _cycle(pairs)
            check(rid,"order_constraints",valid,"cover pairs are not required to contain their transitive closure")
            if body["representation"]=="relation_pairs":check(rid,"order_completeness",None,"omission/incomparability is not inferred from a partial relation list")
        elif kind=="collection":
            members=body["members"];keys=[m["key"] for m in members]
            valid=len(keys)==len(set(keys)) and all(int(m["multiplicity"])>0 and out(m["object"]) is not None for m in members)
            if body["collection_kind"]=="set":valid &= len({m["object"].get("target") for m in members})==len(members) and all(m["multiplicity"]=="1" for m in members)
            for m in members:
                roles=[x["role"] for x in m["associated"]]
                valid &= len(roles)==len(set(roles))
                for association in m["associated"]:
                    target=out(association["target"])
                    if target is None:valid=False
                    elif association["role"]=="s1.parameters":
                        q=target.get("body",{});subject=out(q.get("subject",{}))
                        if subject and subject["output_type"]=="model_reference":
                            valid &= any(ref.get("target")==m["object"].get("target") for ref in subject["body"]["associated"])
                        elif subject and subject['output_type']=='graph':
                            valid &= q['subject']==m['object']
            supported={'s1.output','s1.graph','s1.quantity','s1.claims','s1.set','s1.order','s1.ranking','s1.model_reference'}
            declarations=body['member_contracts'];names={c['name'] for c in declarations}
            known=bool(declarations) and all(c['name'] in supported and c['version']==VERSION for c in declarations)
            matched=all(out(m['object']) is not None and ('s1.output' in names or 's1.'+out(m['object'])['output_type'] in names) for m in members)
            check(rid,'collection_member_contract',matched if known else None,'declared member types form alternatives, not incidental array pairing')
            check(rid,"collection_members",valid,"same graph content can be distinct draws; native member order is retained")
            if body["collection_kind"]=="finite_measure":
                weights={};total=Fraction(0);complete=True
                for m in members:
                    if m["multiplicity"]!="1":complete=False;continue
                    associated=[x["target"] for x in m["associated"] if x["role"]=="s1.weight"]
                    if len(associated)!=1:complete=False;continue
                    q=out(associated[0]);v=q["body"].get("value",{}) if q else {}
                    if not q or q["output_type"]!="quantity" or v.get("state")!="known":complete=False;continue
                    proposition=get(q["body"]["subject"])
                    args={a["role"]:a["value"] for a in proposition["payload"].get("arguments",[])} if proposition else {}
                    if not proposition or proposition['record_type']!='s1.proposition' or proposition['payload']['predicate']!={'name':'s1.native_property','version':VERSION}:
                        complete=False;continue
                    subject=args.get('s1.subject')
                    if (args.get("s1.property")!="s1.collection_member" or args.get("s1.value")!=m["key"]
                            or not isinstance(subject,dict) or subject.get('target')!=rid):complete=False;continue
                    if q["body"]["quantity_kind"] not in ("s1.probability","s1.weight"):complete=False;continue
                    val=decimal_value(v["value"])
                    if not val.is_finite() or val<0:complete=False;continue
                    weights[associated[0]["target"]]=True
                    total+=Fraction(val)
                declared={x.get("target") for x in body["weights"]}
                check(rid,"finite_measure",valid and complete and declared==set(weights) and total==1,
                      "exact per-atom decimal/rational mass; sample multiplicity is not silently multiplied into probability mass")
        elif kind=="quantity" and body["value"].get("value_type")=="tensor":
            v=body["value"]
            try:
                axes=get(v["axes"])
                if not axes or axes["record_type"]!="s1.schema":raise WireError("tensor axes unresolved")
                shape,values,reader=tensor_values(v,resolver)
                valid=shape==tuple(int(a["length"]) for a in axes["payload"]["axes"])
                missing=v["missing"]["name"]
                if v['missing']['version']!=VERSION or missing not in {'s1.no_missing','s1.explicit_null_missing','s1.explicit_nan_missing'}:
                    raise WireError('exact missingness contract not supported')
                for item in values:
                    if item is None:
                        valid &= missing=="s1.explicit_null_missing";continue
                    if isinstance(item,bool):valid=False;continue
                    try:n=Decimal(str(item))
                    except Exception:valid=False;continue
                    if n.is_nan() and missing=="s1.explicit_nan_missing":continue
                    valid &= n.is_finite()
                    if "probability" in reader:valid &= n.is_finite() and 0<=n<=1
                    if "count" in reader:valid &= n.is_finite() and n>=0 and n==n.to_integral_value()
                check(rid,"tensor_encoding",valid,"axis binding and numeric entry contract; no causal/calibration assertion")
            except (OSError,ValueError,KeyError,TypeError,WireError) as exc:
                check(rid,"tensor_encoding",None,str(exc))
        elif kind=="quantity" and body["value"].get("value_type")=="interval":
            level=body["value"]["level"]
            if level["state"]=="known":
                v=decimal_value(level["value"]);check(rid,"interval_level",v.is_finite() and 0<=v<=1)
            else:check(rid,"interval_level",None,"nominal level unavailable; bounds retained")
        elif kind=="quantity" and body["associated_rule"]["state"]=="known" and body["associated_rule"]["value"]["name"]=="s1.count_ratio":
            if body['associated_rule']['value']['version']!=VERSION:
                check(rid,'ratio_basis',None,'unknown exact ratio rule version');continue
            basis=get(body["basis"].get("value",{}))
            endpoints={e["role"]:out(e["target"]) for e in basis["payload"].get("endpoints",[])} if basis else {}
            a,b=endpoints.get("s1.numerator"),endpoints.get("s1.denominator")
            valid=None
            if a and b and a['output_type']==b['output_type']=='quantity':
                av,bv=a["body"]["value"],b["body"]["value"]
                if av.get("state")==bv.get("state")=="known":
                    n,d=decimal_value(av["value"]),decimal_value(bv["value"])
                    valid=(a['body']['quantity_kind']==b['body']['quantity_kind']=='s1.count'
                        and n.is_finite() and d.is_finite() and d>0 and n>=0
                        and n==n.to_integral_value() and d==d.to_integral_value())
                    observed=body['value']
                    if valid and observed.get('state')=='known':
                        ratio=decimal_value(observed['value'])
                        valid=ratio.is_finite() and Fraction(ratio)==Fraction(n)/Fraction(d)
                    elif valid:valid=None
            elif a and b:valid=False
            check(rid,"ratio_basis",valid,"zero/unknown denominator never silently becomes zero frequency")
        elif kind=="model_reference":
            domains={r.get("target") for r in body["input_domains"]+body["output_domains"]}
            valid=all(domain_members(d) is not None for d in body["input_domains"]+body["output_domains"])
            for ref in body["associated"]:
                other=out(ref)
                if other and other["output_type"]=="graph":valid &= other["body"]["domain"].get("target") in domains
            check(rid,"model_associations",valid,"reader/state execution and factor alignment are separate guarantees")
            check(rid,"model_internals",None,"native model deserializer/execution is not part of a reference contract")
        elif kind=="message":
            content=get(body["content"]);correlation=get(body["correlation"])
            check(rid,"message_references",content is not None and correlation is not None,"completion remains scoped to the message operation")
        elif kind=="native_report":check(rid,"native_interpretation",None,"native bytes/type declaration retained without inventing a supported semantic type")
    return report
