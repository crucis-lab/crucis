"""Exact evidence snapshots, selectors and scoped access; DLV-08, DLV-09."""
import base64
import hashlib
import io
import json
import uuid
import zipfile
from pathlib import Path

from .codec import WireError, loads
from .model import contract, index, known, reference, scope, source, unresolved
from .validation import Check, Issue, content_bytes


def capture_bytes(builder, data, *, format_contract=None, basis="observed", source_span=None,
                  native_extent="s1.extent_unresolved", origin=()):
    data = bytes(data)
    try:
        text = data.decode("utf-8",errors="strict")
        content = {"content_form":"inline_utf8","text":text}
    except UnicodeError:
        content = {"content_form":"inline_base64","data":base64.b64encode(data).decode("ascii")}
    sid = str(uuid.uuid4())
    snap = reference(sid,"artifact_snapshot")
    digest = hashlib.sha256(data).hexdigest()
    prop = builder.add("proposition",{"predicate":contract("native_property"),
        "arguments":[{"role":"s1.subject","value":snap},{"role":"s1.property","value":"s1.content_sha256"},
                     {"role":"s1.value","value":digest}],"conditioning":[],"scope":scope(snap)})
    obs = builder.add("observation",{"subject":snap,"proposition":prop,"value":digest,"scope":scope(snap),
        "source_time":unresolved(),"capture_time":unresolved(),
        "source":source("observed",origin,builder.producer),"event":unresolved()})
    builder.add("artifact_snapshot",{"content":content,"format":known(format_contract) if format_contract else unresolved("s1.unsupported_semantics"),
        "capture_scope":{"kind":"full_content"},"source_span":known(source_span) if source_span else unresolved(),
        "native_capture_extent":native_extent,"locations":[],"digest_claims":[obs],
        "source":source(basis,origin,builder.producer)},record_id=sid)
    return snap


def capture_file(builder, path, *, allowed_roots=(), **kwargs):
    """Snapshot bytes actually read, without trusting a size/mtime cache."""
    p = Path(path).resolve()
    if not any(p==Path(root).resolve() or Path(root).resolve() in p.parents for root in allowed_roots):
        raise PermissionError("file capture requires an explicit allowed root")
    if p.name.lower() == ".env":
        raise PermissionError("environment/credential files are outside evidence capture scope")
    return capture_bytes(builder,p.read_bytes(),**kwargs)


def captured_observation(builder, snapshot, predicate="s1.content_captured"):
    prop = builder.add("proposition",{"predicate":contract("native_property"),"arguments":[
        {"role":"s1.subject","value":snapshot},{"role":"s1.property","value":predicate},
        {"role":"s1.value","value":True}],"conditioning":[],"scope":scope(snapshot)})
    return builder.add("observation",{"subject":snapshot,"proposition":prop,"value":True,
        "scope":scope(snapshot),"source_time":unresolved(),"capture_time":unresolved(),
        "source":source("observed",[snapshot],builder.producer),"event":unresolved()})


def evidence_record(builder, artifacts, outputs=(), subjects=(), gaps=(), observations=(), context=(),
                    request=None, native_subject=None, output_extent="not_examined"):
    from .model import unknown_ref
    observations = list(observations) or ([captured_observation(builder,artifacts[0])] if artifacts else [])
    return builder.add("connection_observation",{"subjects":list(subjects) or list(artifacts),
        "request":request or unknown_ref("request"),"native_subject":native_subject or unknown_ref("component"),
        "information":index(extent="not_examined",subjects=subjects),"observations":observations,"gaps":list(gaps),
        "outputs":index(outputs,"complete_for_scope" if outputs else output_extent,subjects),
        "artifacts":index(artifacts,subjects=subjects),"context":list(context),"checks":[]})


class Resolver:
    """No network or implicit path search. External filesystem roots are caller supplied."""

    def __init__(self, package, root=None, allowed_roots=()):
        self.records={r["id"]:r for r in package["records"]}
        self.root=Path(root).resolve() if root else None
        self.allowed=tuple(Path(p).resolve() for p in allowed_roots)

    def record(self, ref):
        if ref["binding"] != "internal":
            raise FileNotFoundError("reference is not locally resolved")
        record=self.records[ref["target"]]
        if record["record_type"] != ref["target_type"]:
            raise WireError("reference target type mismatch")
        return record

    def _external(self, content):
        errors=[]
        for location in content["locations"]:
            descriptor=self.record(location)["payload"]
            locator=descriptor["locator"]
            try:
                if "://" in locator:
                    raise PermissionError("remote locations are descriptors only; no automatic fetch")
                p=Path(locator)
                if not p.is_absolute():
                    if self.root is None: raise PermissionError("relative location requires an explicit root")
                    p=(self.root / p).resolve()
                    if p != self.root and self.root not in p.parents: raise PermissionError("path escapes package root")
                else:
                    p=p.resolve()
                    if not any(p==r or r in p.parents for r in self.allowed):
                        raise PermissionError("external location has no read grant")
                if p.name.lower()==".env": raise PermissionError("credential file is outside evidence scope")
                data=p.read_bytes()
                expected=content["digest"]
                if expected["state"]!="known" or expected["value"]["scope"]!={"kind":"full_content"}:
                    raise WireError("external snapshot identity is unestablished; capture newly read content separately")
                digest=expected["value"]
                if hashlib.sha256(data).hexdigest()!=digest["value"] or len(data)!=int(digest["byte_length"]):
                    raise WireError("external snapshot content differs from its bound identity")
                return data
            except (OSError,WireError) as exc:
                errors.append(exc)
        if errors: raise errors[0]
        raise FileNotFoundError("external snapshot has no declared retrievable location")

    def bytes(self, snapshot):
        record=self.record(snapshot)
        if record["record_type"]!="s1.artifact_snapshot": raise FileNotFoundError("declaration has no captured bytes")
        return content_bytes(record["payload"]["content"],self._external)

    def select(self, payload_ref):
        raw=self.bytes(payload_ref["artifact"])
        selector=payload_ref["selector"]
        if selector["state"]!="known": raise WireError("selector meaning is unresolved")
        sel=selector["value"]; kind=sel["selector_type"]
        if kind=="byte_range":
            a,b=int(sel["start"]),int(sel["end_exclusive"])
            if not 0<=a<=b<=len(raw): raise WireError("selector lies outside captured bytes")
            return raw[a:b]
        if kind=="archive_member":
            with zipfile.ZipFile(io.BytesIO(raw)) as archive: data=archive.read(sel["name"])
            expected=sel["member_digest"]
            if expected["state"]=="known":
                d=expected["value"]
                if hashlib.sha256(data).hexdigest()!=d["value"] or len(data)!=int(d["byte_length"]):
                    raise WireError("archive member identity mismatch")
            return data
        from decimal import Decimal
        from .codec import _pairs,_constant,_unicode
        data=json.loads(raw.decode("utf-8"),parse_float=Decimal,object_pairs_hook=_pairs,parse_constant=_constant)
        _unicode(data)
        if kind=="json_pointer":
            pointer=sel["pointer"]
            if pointer=="": return data
            if not pointer.startswith("/"): raise WireError("invalid JSON pointer")
            for token in pointer[1:].split("/"):
                if __import__("re").search(r"~(?![01])",token): raise WireError("invalid JSON pointer escape")
                token=token.replace("~1","/").replace("~0","~")
                if isinstance(data,list):
                    if not token.isdigit() or (len(token)>1 and token.startswith("0")): raise WireError("invalid array pointer index")
                    data=data[int(token)]
                else: data=data[token]
            return data
        if kind=="member_key":
            if sel["member_contract"]!=contract("keyed_json_object") or not isinstance(data,dict):
                raise WireError("member selector requires the supported immutable keyed-object contract")
            return data[sel["key"]]
        if kind=="array_coordinate":
            schema=self.record(sel["axes"])["payload"]
            if len(schema["axes"])!=len(sel["coordinates"]): raise WireError("coordinate rank mismatch")
            for axis,coordinate in zip(schema["axes"],sel["coordinates"]):
                pos=int(coordinate)-(1 if axis["index_base"]=="one" else 0)
                if not 0<=pos<int(axis["length"]): raise WireError("array coordinate outside declared axis")
                data=data[pos]
            return data
        raise WireError("selector contract is unsupported")


def integrity_checks(package, report, resolver=None):
    resolver=resolver or Resolver(package)
    records=resolver.records
    for record in package["records"]:
        if record["record_type"]!="s1.artifact_snapshot": continue
        rid=record["id"]
        try:
            data=resolver.bytes({"binding":"internal","target":rid,"target_type":"s1.artifact_snapshot"})
            actual=hashlib.sha256(data).hexdigest()
            matched=True
            for ref in record["payload"]["digest_claims"]:
                obs=resolver.record(ref)
                prop=resolver.record(obs["payload"]["proposition"])
                args={a["role"]:a["value"] for a in prop["payload"]["arguments"]}
                if args.get("s1.property")=="s1.content_sha256":
                    if (args.get("s1.subject",{}).get("target")!=rid or obs["payload"]["subject"].get("target")!=rid
                            or obs["payload"]["value"]!=actual or args.get("s1.value")!=actual):
                        matched=False
            report.checks.append(Check(rid,"s1.snapshot_integrity","pass" if matched else "fail",
                                       "observed bytes checked; no authorship/scientific assertion"))
        except (OSError,KeyError,WireError,ValueError) as exc:
            report.checks.append(Check(rid,"s1.snapshot_integrity","unknown",str(exc)))
            report.withheld.append(Issue("s1.not_retrieved","",str(exc),rid))
    return report
