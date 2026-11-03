"""Recorded native fields, not a new graph decision/calibration rule (DLV-08/09).

The recorded prompt defines existence as probability of a relationship and
orientation as confidence versus reverse. Keep the latter as a native score;
do not invent conditional probability semantics or multiply the two fields.
"""
import json
import hashlib
from decimal import Decimal
from pathlib import Path

from ..codec import WireError
from ..domains import member
from ..evidence import capture_file, capture_bytes, evidence_record
from ..model import contract, known, number, scope, source, unresolved


def _reply(text):
    cleaned=text.strip()
    if cleaned.startswith("```"):
        lines=cleaned.splitlines()
        if lines[0] not in ("```json","```") or lines[-1]!="```":raise WireError("unsupported native response framing")
        cleaned="\n".join(lines[1:-1])
    from ..codec import _pairs,_constant
    return json.loads(cleaned,parse_float=Decimal,object_pairs_hook=_pairs,parse_constant=_constant)


def attach_recorded_fields(imported,run_dir,*,allowed_root):
    b=imported["builder"];domain=imported["domain"]
    if domain is None or imported.get('coordinate_basis')!='original':raise WireError("native field decoding requires an established original-column domain")
    directory=Path(run_dir).resolve();root=Path(allowed_root).resolve()
    if directory!=root and root not in directory.parents:raise PermissionError("recorded source outside grant")
    from ..legacy import echo
    legacy=echo(imported["package"],imported["legacy_snapshot"])
    expected=(legacy.files.get("result") or {}).get("sha256")
    result_bytes=(directory/"result.json").read_bytes()
    if expected is None or hashlib.sha256(result_bytes).hexdigest()!=expected:
        raise WireError("native probability evidence does not bind to this legacy source; same shape is insufficient")
    manifest=json.loads(result_bytes.decode("utf-8"))
    names,perm=manifest["shown_order"],manifest["perm"]
    size=len(b.get(domain)["payload"]["members"])
    if (len(names)!=size or not all(isinstance(name,str) for name in names) or len(set(names))!=size or any(type(i) is not int for i in perm)
            or sorted(perm)!=list(range(size))):
        raise WireError("native name/coordinate mapping is ambiguous or incomplete")
    by_name={name:member(domain,perm[i]) for i,name in enumerate(names)}
    log=capture_file(b,directory/"calls.jsonl",allowed_roots=[root],native_extent="s1.full_for_interface")
    outputs=[];gaps=[];artifacts=[log]
    from ..evidence import Resolver
    def gap(subject):
        gaps.append(b.add('gap',{'subjects':[subject],'reasons':['s1.interpretation_failed'],
            'scope':scope(subject),'source':source('observed',[subject],b.producer)}))
    for line in Resolver(b.package([log])).bytes(log).decode('utf-8').splitlines():
        try:row=json.loads(line)
        except (ValueError,TypeError):gap(log);continue
        if not isinstance(row,dict):gap(log);continue
        if not row.get("ok") or not isinstance(row.get("response_text"),str):continue
        request=row.get('request');messages=request.get('messages') if isinstance(request,dict) else None
        if not isinstance(messages,list) or any(not isinstance(m,dict) or not isinstance(m.get('content',''),str) for m in messages):gap(log);continue
        prompt="\n".join(m.get('content','') for m in messages)
        if "existence: probability a relationship exists" not in prompt or "orientation: confidence source causes target vs reverse" not in prompt:
            gaps.append(b.add("gap",{"subjects":[log],"reasons":["s1.unsupported_semantics"],"scope":scope(log),"source":source("observed",[log],b.producer)}));continue
        raw=capture_bytes(b,row["response_text"].encode("utf-8"),basis="derived",origin=[log]);artifacts.append(raw)
        try:parsed=_reply(row['response_text'])
        except (ValueError,TypeError,WireError):gap(raw);continue
        if not isinstance(parsed,dict) or not isinstance(parsed.get('edges',[]),list):gap(raw);continue
        for edge in parsed.get("edges",[]):
            if not isinstance(edge,dict):gap(raw);continue
            if edge.get("source") not in by_name or edge.get("target") not in by_name:
                gaps.append(b.add("gap",{"subjects":[raw],"reasons":["s1.unresolved_identity"],"scope":scope(domain),"source":source("reported",[raw],b.producer)}));continue
            for field,kind,predicate in (("existence","s1.probability","causaliq.relationship_exists"),
                                          ("orientation","s1.score","causaliq.native_orientation_confidence")):
                if field not in edge:continue
                try:value=number(edge[field])
                except (ValueError,TypeError):gap(raw);continue
                prop=b.add("proposition",{"predicate":{"name":predicate,"version":"recorded-prompt-1"},
                    "arguments":[{"role":"s1.left","value":by_name[edge["source"]]},{"role":"s1.right","value":by_name[edge["target"]]}],
                    "conditioning":[],"scope":scope(domain,raw)})
                outputs.append(b.output("quantity",{"quantity_kind":kind,"subject":prop,"value":known(value,[raw]),
                    "units":known({"name":"dimensionless","convention":contract("dimensionless")}),"conditioning":[],
                    "basis":known(raw,[log]),"procedure":b.producer,"associated_rule":known({"name":predicate,"version":"recorded-prompt-1"})},
                    subjects=[raw],role="s1.support",evidence=[raw,log]))
    extra=evidence_record(b,artifacts,outputs,subjects=[log],gaps=gaps,context=[domain])
    imported["outputs"].extend(outputs);imported["gaps"].extend(gaps)
    imported["package"]=b.package([imported["root"],extra])
    imported["native_quantity_roots"]=[extra]
    return imported
