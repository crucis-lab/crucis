"""Immutable package publication and scoped CAS identities (DLV-08, DLV-09)."""
import contextlib
import copy
import hashlib
import os
import uuid
from pathlib import Path

from .codec import WireError, dumps, loads
from .schema import ID_PATTERN
from .validation import validate_wire
from .evidence import integrity_checks


class IdentityConflict(WireError):
    pass


def _id(value):
    import re
    if not re.fullmatch(ID_PATTERN,value): raise WireError("invalid identity")
    return value


@contextlib.contextmanager
def _lock(path):
    try: fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError as exc: raise IdentityConflict("concurrent transaction; retry explicitly") from exc
    try: yield
    finally:
        os.close(fd)
        Path(path).unlink()


def _atomic(path,data,replace=False):
    path=Path(path);tmp=path.with_name(path.name+"."+str(uuid.uuid4())+".staged")
    try:
        with tmp.open("xb") as stream:
            stream.write(data);stream.flush();os.fsync(stream.fileno())
        if replace: os.replace(tmp,path)
        elif os.name == 'nt': os.rename(tmp,path)  # Windows rename refuses an existing destination.
        else: os.link(tmp,path)  # atomic creation without replacing an existing immutable manifest
    finally:
        if tmp.exists(): tmp.unlink()


class PackageStore:
    """Caller-selected local directory. No native input/output folder is moved."""

    def __init__(self,root):
        self.root=Path(root).resolve();self.root.mkdir(parents=True,exist_ok=True)
        for name in ("packages","records","imports","aliases"):(self.root/name).mkdir(exist_ok=True)

    def publish(self,package,required_checks=(),resolver=None):
        report=validate_wire(package)
        report.require()
        integrity_checks(package,report,resolver).require(required_checks)
        data=dumps(package);pid=_id(package["package_id"])
        for record in package["records"]:
            record_path=self.root/"records"/(_id(record["id"])+".json")
            encoded=dumps(record)
            if record_path.exists():
                if record_path.read_bytes()!=encoded: raise IdentityConflict("record ID already binds a different snapshot")
            else:
                try:_atomic(record_path,encoded)
                except FileExistsError:
                    if record_path.read_bytes()!=encoded: raise IdentityConflict("concurrent record identity conflict")
        path=self.root/"packages"/(pid+".json")
        if path.exists():
            if path.read_bytes()!=data: raise IdentityConflict("package identity already binds a different snapshot")
        else:
            try:_atomic(path,data)
            except FileExistsError:
                if path.read_bytes()!=data: raise IdentityConflict("concurrent package identity conflict")
        return {"package_id":pid,"path":str(path),"sha256":hashlib.sha256(data).hexdigest(),"checks":report.to_json()}

    def load(self,pid,expected_sha256=None):
        raw=(self.root/"packages"/(_id(pid)+".json")).read_bytes()
        if expected_sha256 and hashlib.sha256(raw).hexdigest()!=expected_sha256: raise IdentityConflict("manifest digest changed")
        return loads(raw)

    def import_once(self,occurrence,bound_inputs,create):
        """Occurrence key is caller-designated, not a digest of source content."""
        path=self.root/"imports"/(_id(occurrence)+".json")
        # Named encoding for import-key comparison only. Arrays and number lexemes retain order/value.
        dumps(bound_inputs)  # reject invalid text/nonfinite values before comparing a binding
        encoded=__import__("json").dumps(bound_inputs,sort_keys=True,separators=(",",":"),ensure_ascii=False)
        binding=hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        with _lock(path.with_suffix(".lock")):
            if path.exists():
                receipt=loads(path.read_bytes())
                if receipt["binding"]!=binding: raise IdentityConflict("changed input under an existing import occurrence")
                return copy.deepcopy(receipt["result"])
            result=create()
            receipt={"occurrence":occurrence,"comparison_contract":"s1.sorted_json_import_binding.v1",
                     "binding":binding,"result":result}
            _atomic(path,dumps(receipt))
            return copy.deepcopy(result)

    def select_current(self,namespace,name,selection,expected_previous=None):
        if selection.get("binding")!="internal" or selection.get("target_type")!="s1.selection":
            raise WireError("alias requires a resolved selection record")
        found=any(any(r["id"]==selection["target"] and r["record_type"]=="s1.selection" for r in loads(p.read_bytes())["records"])
                  for p in (self.root/"packages").glob("*.json"))
        if not found: raise WireError("current selection must be in a committed package")
        folder=self.root/"aliases"/_id(namespace);folder.mkdir(exist_ok=True)
        key=hashlib.sha256(name.encode("utf-8")).hexdigest()
        path=folder/(key+".json")
        with _lock(path.with_suffix(".lock")):
            old=loads(path.read_bytes()) if path.exists() else None
            if old and old["name"]!=name: raise IdentityConflict("alias-name hash collision")
            previous=old["selected"] if old else None
            if previous!=expected_previous: raise IdentityConflict("current selection changed since observation")
            receipt={"namespace":namespace,"name":name,"previous":previous,"selected":copy.deepcopy(selection),
                     "generation":str(int(old["generation"])+1) if old else "1"}
            _atomic(path,dumps(receipt),replace=True)
            return receipt
