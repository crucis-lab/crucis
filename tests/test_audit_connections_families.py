from crucis.core.paths import ROOT as DATA_ROOT
"""Output subtypes and associations (DLV-08, DLV-09); synthetic conformance only."""
import copy
import sys
import unittest
import uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from crucis.connections import Builder, WireError, known, number
from crucis.connections.domains import directed_link, finite_domain, graph_body, mapped_graph, member
from crucis.connections.evidence import capture_bytes
from crucis.connections.model import contract, reference, scope, source, unresolved
from crucis.connections.semantics import validate


def result(report,subject,name):return next(c.result for c in report.checks if c.subject==subject["target"] and c.contract=="s1."+name)


def scalar(b,kind,subject,value,basis=None,rule=None):
    return b.output("quantity",{"quantity_kind":"s1."+kind,"subject":subject,"value":known(number(value)),
        "units":known({"name":"dimensionless","convention":contract("dimensionless")}),"conditioning":[],
        "basis":known(basis) if basis else unresolved(),"procedure":b.producer,"associated_rule":known(rule) if rule else unresolved()})


class FamilyCases(unittest.TestCase):
    def test_repeated_graphs_and_parameter_members_stay_distinct(self):
        b=Builder();d=finite_domain(b,["A","B"]);body=graph_body(d,[directed_link(d,0,1)])
        a=b.output("graph",body);z=b.output("graph",body)
        pa=scalar(b,"coefficient",a,"0.2");pz=scalar(b,"coefficient",z,"0.9")
        c=b.output("collection",{"collection_kind":"sample_bank","member_contracts":[contract("output")],
            "members":[{"key":key,"object":obj,"multiplicity":"1","associated":[{"role":"s1.parameters","target":param}]} for key,obj,param in (("s1",a,pa),("s2",z,pz))],
            "extent":scope(d),"ordering":"native_sequence","generation":unresolved(),"weights":[]})
        r=validate(b.package([c]));self.assertTrue(r.ok,r.to_json());self.assertEqual(result(r,c,"collection_members"),"pass")
        members=b.get(c)["payload"]["body"]["members"]
        self.assertEqual(len(members),2);self.assertNotEqual(members[0]["object"],members[1]["object"])

    def test_finite_measure_uses_member_binding_and_exact_mass(self):
        for masses,expected in ((["0.4","0.6"],"pass"),(["0.4","0.3"],"fail"),(["1","0.0000000000000000000000000000000000000001"],"fail")):
            b=Builder();d=finite_domain(b,["X"]);g=b.output("graph",graph_body(d,[]));cid=str(uuid.uuid4());cref=reference(cid,"output")
            weights=[];members=[]
            for i,mass in enumerate(masses):
                key="sample"+str(i)
                prop=b.add("proposition",{"predicate":contract("native_property"),"arguments":[
                    {"role":"s1.subject","value":cref},{"role":"s1.property","value":"s1.collection_member"},
                    {"role":"s1.value","value":key}],"conditioning":[],"scope":scope(d)})
                q=scalar(b,"probability",prop,mass);weights.append(q)
                members.append({"key":key,"object":g,"multiplicity":"1","associated":[{"role":"s1.weight","target":q}]})
            payload={"output_type":"collection","native_producer":b.producer,"subjects":[],"role":known("s1.native_answer"),"designation":unresolved(),
                "body":{"collection_kind":"finite_measure","member_contracts":[contract("output")],"members":members,"extent":scope(d),"ordering":"unordered","generation":unresolved(),"weights":weights},
                "source":source(),"relations":[],"checks":[]}
            b.add("output",payload,record_id=cid);p=b.package([cref]);r=validate(p)
            self.assertTrue(r.ok,r.to_json());self.assertEqual(result(r,cref,"finite_measure"),expected)
            self.assertEqual([b.get(q)["payload"]["body"]["value"]["value"]["text"] for q in weights],masses)

    def test_ties_unranked_and_missing_scope_are_separate(self):
        b=Builder();d=finite_domain(b,["A","B","C","D"])
        body={"predicate":contract("predictive_rank"),"domain":d,"groups":[[member(d,0),member(d,1)],[member(d,2)]],
              "direction":"earlier_higher","unranked":[member(d,3)],"excluded":[],"quantities":[]}
        rank=b.output("ranking",body);r=validate(b.package([rank]));self.assertEqual(result(r,rank,"ranking"),"pass")
        body["unranked"]=[];partial=b.output("ranking",body)
        self.assertEqual(result(validate(b.package([partial])),partial,"ranking"),"unknown")
        self.assertEqual(len(b.get(rank)["payload"]["body"]["groups"][0]),2)

    def test_cover_order_does_not_need_transitive_closure(self):
        b=Builder();d=finite_domain(b,["A","B","C"])
        body={"predicate":contract("precedes"),"domain":d,"representation":"cover_pairs","sequence":[],
              "pairs":[{"left":member(d,0),"right":member(d,1)},{"left":member(d,1),"right":member(d,2)}],"coverage":scope(d),"omission":"s1.no_assertion"}
        order=b.output("order",body)
        self.assertEqual(result(validate(b.package([order])),order,"order_constraints"),"pass")
        body["pairs"].append({"left":member(d,2),"right":member(d,0)});bad=b.output("order",body)
        self.assertEqual(result(validate(b.package([bad])),bad,"order_constraints"),"fail")

    def test_local_membership_does_not_expand_to_global_graph(self):
        b=Builder();d=finite_domain(b,["A","B","Y"])
        body={"predicate":contract("parents"),"targets":[member(d,2)],"candidates":d,"members":[member(d,0)],
              "decisions":[],"coverage":scope(d),"omission":"s1.unreported"}
        local=b.output("set",body);p=b.package([local])
        self.assertEqual(result(validate(p),local,"local_set"),"pass")
        self.assertFalse(any(r["record_type"]=="s1.output" and r["payload"]["output_type"]=="graph" for r in p["records"]))

    def test_interval_and_zero_denominator_fail_without_repair(self):
        b=Builder();d=finite_domain(b,["X"])
        interval={"value_type":"interval","lower":known(number("0.9")),"upper":known(number("0.1")),
                  "lower_inclusive":True,"upper_inclusive":True,"construction":contract("native_interval"),"level":known(number("0.95")),"target":d}
        q=scalar(b,"score",d,"1");p=b.package([q]);next(r for r in p["records"] if r["id"]==q["target"])["payload"]["body"]["value"]=interval
        self.assertEqual(result(validate(p),q,"interval"),"fail")
        numerator=scalar(b,"count",d,0);denominator=scalar(b,"count",d,0)
        basis=b.add("relation",{"relation_contract":contract("ratio_components"),"endpoints":[{"role":"s1.numerator","target":numerator},{"role":"s1.denominator","target":denominator}],
              "parameters":[],"scope":scope(d),"source":source()})
        ratio=scalar(b,"frequency",d,"0",basis,contract("count_ratio"))
        self.assertEqual(result(validate(b.package([ratio])),ratio,"ratio_basis"),"fail")

    def test_learned_alignment_is_a_derived_view_and_partial_targets_rejected(self):
        b=Builder();a=finite_domain(b,["factor0","factor1"]);t=finite_domain(b,["truthA","truthB"])
        entries=[{"from":[member(a,i)],"to":[member(t,i)],"source":source()} for i in range(2)]
        m=b.add("mapping",{"mapping_kind":"semantic_alignment","from":a,"to":t,"entries":entries,"procedure":b.producer,
            "purpose":"s1.evaluation_alignment","coverage":scope(a,t),"properties":[],"checks":[],"source":source()})
        g=b.output("graph",graph_body(a,[directed_link(a,0,1)]))
        aligned=mapped_graph(b,b.package([g]),g,m,declared_alignment=True)
        self.assertEqual(b.get(aligned)["payload"]["role"]["value"],"s1.derived_view")
        self.assertEqual(b.get(g)["payload"]["body"]["domain"],a)
        self.assertTrue(validate(b.package([aligned])).ok)

    def test_tensor_preserves_sub_float_range_error_and_null_missingness(self):
        b=Builder();d=finite_domain(b,["X"]);raw=capture_bytes(b,b'[1.00000000000000000000000000001,null]')
        payload={"artifact":raw,"selector":known({"selector_type":"json_pointer","pointer":""})}
        axes=b.add("schema",{"payload":payload,"axes":[{"name":"s1.sample","axis_kind":"sample","length":"2","coordinates":[
            {"key":str(i),"member":unresolved(),"value":known(str(i))} for i in range(2)],"index_base":"zero"}],
            "labels":[],"encoding":contract("json"),"domain":d,"source":source()})
        tensor={"value_type":"tensor","payload":payload,"axes":axes,"entry_contract":contract("json_probability_tensor"),"missing":contract("explicit_null_missing")}
        q=scalar(b,"probability",d,"0");p=b.package([q]);next(r for r in p["records"] if r["id"]==q["target"])["payload"]["body"]["value"]=tensor
        r=validate(p);self.assertTrue(r.ok,r.to_json());self.assertEqual(result(r,q,"tensor_encoding"),"fail")

    def test_opaque_model_reference_does_not_claim_model_execution(self):
        b=Builder();d=finite_domain(b,["factor"])
        m=b.output("model_reference",{"model_role":"s1.encoder","artifacts":[],"input_domains":[],"output_domains":[d],
            "dependencies":[],"associated":[],"reader":unresolved("s1.unsupported_semantics"),
            "state_coverage":{"members":[],"extent":"not_examined","scope":scope(d),"gaps":[]}})
        r=validate(b.package([m]));self.assertEqual(result(r,m,"model_associations"),"pass")
        self.assertEqual(result(r,m,"model_internals"),"unknown")


if __name__=="__main__":unittest.main()
