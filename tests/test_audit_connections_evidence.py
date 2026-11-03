from crucis.core.paths import ROOT as DATA_ROOT
"""Evidence identity/publication failures and partial capture (DLV-08, DLV-09)."""
import copy
import hashlib
import os
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from crucis.connections import Builder, WireError, known
from crucis.connections.evidence import Resolver, capture_bytes, capture_file, evidence_record, integrity_checks
from crucis.connections.model import contract, reference, scope, source, unresolved
from crucis.connections.store import IdentityConflict, PackageStore
from crucis.connections.validation import validate_wire


def package(data=b'{"":7,"x":[1,2]}'):
    b=Builder();snap=capture_bytes(b,data);root=evidence_record(b,[snap]);return b,b.package([root]),snap


class EvidenceCases(unittest.TestCase):
    def test_arbitrary_bytes_and_unknown_original_execution(self):
        for raw in (b'\xff\xfe\x00',b'\xef\xbb\xbf\r\n',b'{"edges":['):
            b,p,snap=package(raw)
            self.assertEqual(Resolver(p).bytes(snap),raw)
            self.assertTrue(validate_wire(p).ok,validate_wire(p).to_json())
            self.assertFalse(any(r["record_type"]=="s1.attempt" for r in p["records"]))

    def test_source_snapshot_cannot_mutate_through_builder_get(self):
        b,p,snap=package();record=b.get(snap)
        record["payload"]["content"]["text"]="changed"
        self.assertNotEqual(b.get(snap)["payload"]["content"]["text"],"changed")

    def test_json_pointer_empty_root_differs_from_slash_property(self):
        b,p,snap=package();resolver=Resolver(p)
        def sel(pointer):return resolver.select({"artifact":snap,"selector":known({"selector_type":"json_pointer","pointer":pointer})})
        self.assertEqual(sel("/"),7)
        self.assertEqual(sel("/x/1"),2)
        self.assertIsInstance(sel(""),dict)
        with self.assertRaises(WireError):sel("/x/01")
        with self.assertRaises(WireError):sel("/~2")

    def test_hash_mismatch_is_scoped_and_never_repaired(self):
        b,p,snap=package();bad=copy.deepcopy(p)
        next(r for r in bad["records"] if r["id"]==snap["target"])["payload"]["content"]["text"]="different"
        report=integrity_checks(bad,validate_wire(bad))
        self.assertTrue(report.ok)  # evidence is structurally preservable
        self.assertTrue(any(c.result=="fail" for c in report.checks))
        with self.assertRaises(WireError):report.require(["s1.snapshot_integrity"])

    def test_missing_external_is_not_broken_internal(self):
        b,p,snap=package()
        record=next(r for r in p["records"] if r["id"]==snap["target"])
        record["payload"]["content"]={"content_form":"external_snapshot","locations":[],"digest":unresolved("s1.not_retrieved")}
        report=integrity_checks(p,validate_wire(p))
        self.assertTrue(report.reference_ok)
        self.assertTrue(any(c.result=="unknown" for c in report.checks))
        p["roots"][0]["target"]=str(uuid.uuid4())
        self.assertFalse(validate_wire(p).reference_ok)

    def test_same_path_and_mtime_changed_bytes_get_new_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"output.bin";path.write_bytes(b"first");st=path.stat()
            b=Builder();first=capture_file(b,path,allowed_roots=[tmp])
            path.write_bytes(b"other");os.utime(path,ns=(st.st_atime_ns,st.st_mtime_ns))
            second=capture_file(b,path,allowed_roots=[tmp])
            p=b.package([first,second]);resolver=Resolver(p)
            self.assertEqual(resolver.bytes(first),b"first");self.assertEqual(resolver.bytes(second),b"other")
            self.assertNotEqual(first,second)
            with self.assertRaises(PermissionError):capture_file(b,path)

    def test_publish_is_immutable_and_record_identity_global_to_store(self):
        b,p,snap=package()
        with tempfile.TemporaryDirectory() as tmp:
            store=PackageStore(tmp);receipt=store.publish(p,["s1.snapshot_integrity"])
            self.assertEqual(store.load(p["package_id"],receipt["sha256"]),p)
            self.assertEqual(store.publish(p)["sha256"],receipt["sha256"])
            changed=copy.deepcopy(p);changed["package_id"]=str(uuid.uuid4())
            changed["records"][0]["payload"]["name"]="new name under old identity"
            with self.assertRaises(IdentityConflict):store.publish(changed)
            self.assertEqual(len(list((Path(tmp)/"packages").glob("*.json"))),1)

    def test_interrupted_staging_is_not_a_published_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=PackageStore(tmp)
            (Path(tmp)/"packages"/"unfinished.staged").write_bytes(b'{"records":')
            self.assertEqual(list((Path(tmp)/"packages").glob("*.json")),[])

    def test_partial_evidence_publishes_without_a_fake_graph(self):
        b,p,snap=package(b'{"edges":[')
        next(r for r in p["records"] if r["id"]==snap["target"])["payload"]["native_capture_extent"]="s1.partial_for_interface"
        with tempfile.TemporaryDirectory() as tmp:
            receipt=PackageStore(tmp).publish(p,["s1.snapshot_integrity"])
            self.assertTrue(receipt["checks"]["wire_reference_ok"])
            self.assertFalse(any(r["record_type"]=="s1.output" for r in p["records"]))

    def test_idempotent_import_is_occurrence_scoped(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=PackageStore(tmp);occ=str(uuid.uuid4());called=[]
            def create():called.append(True);return {"observation":str(uuid.uuid4())}
            one=store.import_once(occ,{"source":"one","decoder":"v1"},create)
            two=store.import_once(occ,{"source":"one","decoder":"v1"},create)
            self.assertEqual(one,two);self.assertEqual(len(called),1)
            with self.assertRaises(IdentityConflict):store.import_once(occ,{"source":"changed","decoder":"v1"},create)
            self.assertNotEqual(one,store.import_once(str(uuid.uuid4()),{"source":"one","decoder":"v1"},create))

    def test_current_selection_cas_preserves_pinned_basis(self):
        b,p,snap=package();selected=b.add("selection",{"purpose":"s1.current","selected":[snap],"rule":contract("explicit_selection"),"basis":[snap],"source":source()})
        p=b.package([selected]);namespace=str(uuid.uuid4())
        with tempfile.TemporaryDirectory() as tmp:
            store=PackageStore(tmp);store.publish(p)
            first=store.select_current(namespace,"result",selected)
            with self.assertRaises(IdentityConflict):store.select_current(namespace,"result",selected)
            second=store.select_current(namespace,"result",selected,selected)
            self.assertEqual(second["previous"],first["selected"])
            self.assertEqual(store.load(p["package_id"]),p)


if __name__=="__main__":unittest.main()
