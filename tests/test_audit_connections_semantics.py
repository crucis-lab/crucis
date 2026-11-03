from crucis_causal.core.paths import ROOT as DATA_ROOT
"""Domain/mapping/graph/quantity fidelity across real recorded paths (DLV-08/09)."""
import copy
import sys
import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from crucis_causal.connections import Builder, WireError, known, number
from crucis_causal.connections.domains import directed_link, finite_domain, graph_body, mapped_graph, member, permutation
from crucis_causal.connections.evidence import capture_bytes
from crucis_causal.connections.model import contract, scope, source, unresolved
from crucis_causal.connections.semantics import validate
from crucis_causal.connections.legacy import echo, encode, import_record


def check_result(report,subject,kind):
    return next(c.result for c in report.checks if c.subject==subject["target"] and c.contract=="s1."+kind)


def quantity(b,subject,value,evidence=()):
    return b.output("quantity",{"quantity_kind":"s1.probability","subject":subject,"value":known(number(value)),
        "units":known({"name":"dimensionless","convention":contract("dimensionless")}),"conditioning":[],
        "basis":known(evidence[0]) if evidence else unresolved(),"procedure":b.producer,"associated_rule":unresolved()},evidence=evidence)


class SemanticCases(unittest.TestCase):
    def test_duplicate_labels_do_not_merge_variables(self):
        b=Builder();d=finite_domain(b,["score","score"])
        p=b.package([d]);validate(p).require(["s1.domain"],subjects=[d["target"]])
        members=b.get(d)["payload"]["members"]
        self.assertNotEqual(members[0]["variable"],members[1]["variable"])

    def test_duplicate_coordinate_identity_cannot_disguise_self_node(self):
        b=Builder();d=finite_domain(b,["X"]);p=b.package([d])
        dom=next(r for r in p["records"] if r["id"]==d["target"])
        dom["payload"]["members"].append({**copy.deepcopy(dom["payload"]["members"][0]),"key":"alias"})
        self.assertEqual(check_result(validate(p),d,"domain"),"fail")

    def test_native_dag_cycle_is_preserved_and_not_repaired(self):
        b=Builder();d=finite_domain(b,["A","B"])
        g=b.output("graph",graph_body(d,[directed_link(d,0,1),directed_link(d,1,0)],"dag"))
        p=b.package([g]);r=validate(p)
        self.assertTrue(r.ok)
        self.assertEqual(check_result(r,g,"dag"),"fail")
        self.assertEqual(len(b.get(g)["payload"]["body"]["links"]),2)
        with self.assertRaises(WireError):r.require(["s1.dag"],subjects=[g["target"]])

    def test_pag_endpoint_capture_does_not_claim_full_family_validation(self):
        b=Builder();d=finite_domain(b,["A","B"]);link=directed_link(d,0,1)
        link["relation"]=contract("endpoint_relation");link["endpoint_marks"]=["s1.circle","s1.arrowhead"]
        g=b.output("graph",graph_body(d,[link],"pag"));r=validate(b.package([g]))
        self.assertEqual(check_result(r,g,"graph_encoding"),"pass")
        self.assertEqual(check_result(r,g,"graph_family"),"unknown")

    def test_mapping_clones_linked_probability_proposition(self):
        b=Builder();native=finite_domain(b,["V1","V2","V3"])
        original=b.get(native)["payload"]
        mapped_members=[{**copy.deepcopy(original["members"][1]),"key":"age"},
                        {**copy.deepcopy(original["members"][2]),"key":"smoking"},
                        {**copy.deepcopy(original["members"][0]),"key":"outcome"}]
        target=b.add("domain",{**original,"members":mapped_members})
        m=permutation(b,native,target,[("0","outcome"),("1","age"),("2","smoking")])
        prop=b.add("proposition",{"predicate":contract("direct_relation"),"arguments":[
            {"role":"s1.cause","value":member(native,1)},{"role":"s1.effect","value":member(native,0)}],
            "conditioning":[],"scope":scope(native)})
        raw=capture_bytes(b,b'{"probability":0.7}')
        q=quantity(b,prop,"0.7",[raw]);body=graph_body(native,[directed_link(native,1,0)]);body["quantities"]=[q]
        g=b.output("graph",body,evidence=[raw]);view=mapped_graph(b,b.package([g]),g,m)
        p=b.package([view]);r=validate(p);self.assertTrue(r.ok,r.to_json())
        edge=b.get(view)["payload"]["body"]["links"][0]
        self.assertEqual((edge["left"]["key"],edge["right"]["key"]),("age","outcome"))
        new_q=b.get(b.get(view)["payload"]["body"]["quantities"][0])
        new_prop=b.get(new_q["payload"]["body"]["subject"])
        self.assertEqual([a["value"]["key"] for a in new_prop["payload"]["arguments"]],["age","outcome"])
        self.assertNotEqual(new_prop["id"],prop["target"])

    def test_missing_and_ambiguous_maps_do_not_zero_fill(self):
        b=Builder();d=finite_domain(b,["X","Y"]);m=permutation(b,d,d,[("0","0")])
        r=validate(b.package([m]));self.assertEqual(check_result(r,m,"mapping"),"fail")
        g=b.output("graph",graph_body(d,[directed_link(d,0,1)]));before=len(b.package([g])["records"])
        with self.assertRaises(WireError):mapped_graph(b,b.package([g]),g,m)
        self.assertEqual(len(b.package([g])["records"]),before)

    def test_equal_names_do_not_prove_cross_domain_identity(self):
        b=Builder();a=finite_domain(b,["X"]);z=finite_domain(b,["X"]);m=permutation(b,a,z,[("0","0")])
        r=validate(b.package([m]));self.assertEqual(check_result(r,m,"mapping_identity"),"unknown")

    def test_probability_for_candidate_absent_from_graph_and_bad_native_range(self):
        b=Builder();d=finite_domain(b,["A","B"])
        prop=b.add("proposition",{"predicate":contract("direct_relation"),"arguments":[
            {"role":"s1.cause","value":member(d,1)},{"role":"s1.effect","value":member(d,0)}],"conditioning":[],"scope":scope(d)})
        g=b.output("graph",graph_body(d,[]));q=quantity(b,prop,"1.2")
        r=validate(b.package([g,q]));self.assertTrue(r.ok,r.to_json())
        self.assertEqual(check_result(r,q,"quantity_value"),"fail")
        self.assertEqual(b.get(q)["payload"]["body"]["value"]["value"]["text"],"1.2")

    def test_temporal_self_history_is_not_same_node_loop(self):
        b=Builder();d=finite_domain(b,["X"]);p=b.get(d)["payload"]
        var=p["members"][0]["variable"]
        p["domain_kind"]="relative_temporal";p["coordinate_contract"]=known(contract("relative_steps"))
        p["members"]=[{"key":key,"variable":var,"coordinates":[{"dimension":contract("relative_step"),
            "value":number(offset),"reference":unresolved()}]} for key,offset in (("past",-1),("now",0))]
        t=b.add("domain",p);g=b.output("graph",graph_body(t,[directed_link(t,"past","now")],"dag"))
        r=validate(b.package([g]));self.assertEqual(check_result(r,g,"dag"),"pass")

    def test_native_claim_scope_cannot_extend_outside_declared_queries(self):
        b=Builder();d=finite_domain(b,["A","B"])
        coverage={"pairing":"ordered","domain":d,"include_same_node":False,"pairs":[],"extent":"listed_only"}
        g=b.output("graph",graph_body(d,[directed_link(d,0,1)],coverage=coverage))
        self.assertEqual(check_result(validate(b.package([g])),g,"graph_encoding"),"fail")

    def test_lossless_legacy_codec_keeps_fields_summary_drops(self):
        from crucis_causal.core.runs import RunRecord
        from crucis_causal.core.graph import Graph
        g=Graph.from_edges(2,[(0,1)]);rec=RunRecord("toy","item","real","ok",graph=g,
            confidence={(0,1):0.7},edge_source={(0,1):"llm"},variants={"S0":g},stages=[("S0",g)],
            notes={"file_read":"important-seed-name","replicates":[RunRecord("toy","item","real","host_error")]})
        imported=import_record(rec);back=echo(imported["package"],imported["legacy_snapshot"])
        self.assertEqual(encode(back),encode(rec));self.assertTrue(validate(imported["package"]).ok)
        self.assertEqual(back.notes["file_read"],"important-seed-name")

    @unittest.skipUnless((DATA_ROOT / "runs/ab06").is_dir() and (DATA_ROOT / "external/causalarena").is_dir(),"recorded sources absent")
    def test_real_method_and_name_hybrid_sources_import_without_running(self):
        from crucis_causal.core import adapter,battery
        for name,bid,arm in (("pc","ca-semantic","released"),("causaliq","ca-ab06","real"),("matmcd","ca-ab06","real")):
            ad=adapter.get(name);bt=battery.get(bid);item=bt.items[0]
            with patch.object(ad,"run",side_effect=AssertionError("must not execute native system")):
                rec=ad.recorded(item,arm);self.assertEqual(rec.status,"ok")
                imported=import_record(rec,n=item.n)
            r=validate(imported["package"])
            self.assertTrue(r.ok,(name,r.to_json()))
            self.assertEqual(encode(echo(imported["package"],imported["legacy_snapshot"])),encode(rec))

    @unittest.skipUnless((DATA_ROOT / "runs/ab06/causaliq/apartment_heat_exposure_shading_ac/real/calls.jsonl").is_file(),"native response evidence absent")
    def test_native_probabilities_preserve_prompt_meaning_and_coordinates(self):
        from crucis_causal.connections.legacy import recorded
        from crucis_causal.connections.integrations.causaliq import attach_recorded_fields
        imported=recorded("causaliq","ca-ab06",arm="real")
        path=DATA_ROOT / "runs/ab06/causaliq/apartment_heat_exposure_shading_ac/real"
        attach_recorded_fields(imported,path,allowed_root=DATA_ROOT)
        report=validate(imported["package"]);self.assertTrue(report.ok,report.to_json())
        values=[r for r in imported["package"]["records"] if r["record_type"]=="s1.output" and r["payload"]["output_type"]=="quantity"
                and r['payload']['body']['associated_rule'].get('value',{}).get('name','').startswith('causaliq.')]
        self.assertGreater(len(values),0)
        self.assertEqual({r["payload"]["body"]["quantity_kind"] for r in values},{"s1.probability","s1.score"})
        self.assertTrue(all(check_result(report,{"target":r["id"]},"quantity_value")=="pass" for r in values))
        self.assertFalse(any(r["record_type"]=="s1.attempt" for r in imported["package"]["records"]))
        with tempfile.TemporaryDirectory() as tmp:
            wrong=Path(tmp)/"result.json";wrong.write_text('{"shown_order":[],"perm":[]}',encoding="utf-8")
            with self.assertRaises(WireError):attach_recorded_fields(imported,tmp,allowed_root=tmp)


if __name__=="__main__":unittest.main()
