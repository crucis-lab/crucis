"""Additive legacy evidence bridge, no change to existing scoring (DLV-08/09)."""
import base64
import dataclasses
import json
import hashlib
from pathlib import Path

from .codec import WireError, dumps
from .domains import directed_link, finite_domain, graph_body, member
from .evidence import capture_bytes, capture_file, evidence_record
from .model import Builder, contract, known, number, source, scope, unknown_ref, unresolved


def encode(value):
    """Explicit legacy codec; no pickle, dynamic class loading, default=str or key coercion."""
    from crucis_causal.core.graph import Graph
    from crucis_causal.core.runs import RunRecord
    if isinstance(value,(Graph,RunRecord)):
        return {"legacy_type":type(value).__name__,"fields":{f.name:encode(getattr(value,f.name)) for f in dataclasses.fields(value)}}
    if isinstance(value,dict):return {"legacy_type":"dict","entries":[[encode(k),encode(v)] for k,v in value.items()]}
    if isinstance(value,(tuple,set,frozenset)):
        items=list(value)
        if isinstance(value,(set,frozenset)):items=sorted(items,key=lambda x:json.dumps(encode(x),sort_keys=True))
        return {"legacy_type":type(value).__name__,"items":[encode(x) for x in items]}
    if isinstance(value,list):return [encode(x) for x in value]
    if value is None or isinstance(value,(str,bool,int)):return value
    if isinstance(value,float):
        import struct
        return {"legacy_type":"float64","bits":struct.pack(">d",value).hex()}
    try:
        import numpy as np
        if isinstance(value,(np.ndarray,np.generic)):
            array=np.asarray(value)
            if array.dtype.hasobject:raise WireError("object arrays cannot be treated as a safe lossless numeric codec")
            return {"legacy_type":"numpy_scalar" if isinstance(value,np.generic) else "numpy_array",
                    "dtype":array.dtype.str,"shape":list(array.shape),"data":base64.b64encode(array.tobytes(order="C")).decode("ascii")}
    except ImportError:pass
    raise WireError("unsupported legacy object requires an explicit codec: "+type(value).__name__)


def decode(value):
    if isinstance(value,list):return [decode(x) for x in value]
    if not isinstance(value,dict):return value
    kind=value.get("legacy_type")
    if kind=="dict":return {decode(k):decode(v) for k,v in value["entries"]}
    if kind in ("tuple","set","frozenset"):
        cls={"tuple":tuple,"set":set,"frozenset":frozenset}[kind]
        return cls(decode(x) for x in value["items"])
    if kind in ("Graph","RunRecord"):
        from crucis_causal.core.graph import Graph
        from crucis_causal.core.runs import RunRecord
        cls={"Graph":Graph,"RunRecord":RunRecord}[kind]
        fields={k:decode(v) for k,v in value["fields"].items()}
        if set(fields)!={f.name for f in dataclasses.fields(cls)}:raise WireError("legacy field set is incompatible")
        return cls(**fields)
    if kind=="float64":
        import struct
        return struct.unpack(">d",bytes.fromhex(value["bits"]))[0]
    if kind in ("numpy_array","numpy_scalar"):
        import numpy as np
        dtype=np.dtype(value["dtype"])
        if dtype.hasobject:raise WireError("object array decoding is forbidden")
        raw=base64.b64decode(value["data"],validate=True)
        array=np.frombuffer(raw,dtype=dtype).copy().reshape(value["shape"])
        return array[()] if kind=="numpy_scalar" else array
    raise WireError("unknown legacy codec tag")


def _graph(builder,g,domain,evidence,role):
    links=[]
    for a,b in sorted(g.directed):links.append(directed_link(domain,a,b,"d:"+str(a)+":"+str(b)))
    for kind,pairs,marks,relation in (("u",g.undirected,["s1.tail","s1.tail"],"unresolved_adjacency"),
                                     ("b",g.bidirected,["s1.arrowhead","s1.arrowhead"],"bidirected_relation")):
        for a,b in sorted(pairs):links.append({"key":kind+":"+str(a)+":"+str(b),"left":member(domain,a),"right":member(domain,b),
            "relation":contract(relation),"endpoint_marks":marks,"properties":[],"quantities":[]})
    mark_map={"a o-> b":["s1.circle","s1.arrowhead"],"b o-> a":["s1.arrowhead","s1.circle"],
              "a o- b":["s1.circle","s1.tail"],"b o- a":["s1.tail","s1.circle"],"o-o":["s1.circle","s1.circle"]}
    for i,(a,b,mark) in enumerate(sorted(g.partial)):
        marks=mark_map.get(mark,[])
        relation="endpoint_relation" if marks else "association" if mark=="associated" else "legacy_partial"
        prop=builder.add("proposition",{"predicate":contract("native_property"),"arguments":[
            {"role":"s1.subject","value":evidence[0]},{"role":"s1.property","value":"legacy.partial_mark"},
            {"role":"s1.value","value":mark}],"conditioning":[],"scope":scope(domain)})
        links.append({"key":"p:"+str(i),"left":member(domain,a),"right":member(domain,b),"relation":contract(relation),
                      "endpoint_marks":marks,"properties":[prop],"quantities":[]})
    return builder.output("graph",graph_body(domain,links,"legacy_graph"),role=role,evidence=evidence)


def import_record(record, *, builder=None, domain=None, n=None, coordinate_basis="original", roots=()):
    """Read an already produced legacy value; no native attempt/request is fabricated."""
    builder=builder or Builder("legacy recorded importer")
    blob=capture_bytes(builder,dumps(encode(record)),format_contract=contract("legacy_runrecord_codec"),basis="reconstructed")
    artifacts=[blob];gaps=[]
    from crucis_causal.core.paths import ROOT as repository
    for info in record.files.values():
        if not isinstance(info,dict) or not isinstance(info.get('path'),str):
            gaps.append(builder.add('gap',{'subjects':[blob],'reasons':['s1.unsupported_file_declaration'],
                'scope':scope(blob),'source':source('reported',[blob],builder.producer)}));continue
        path=repository/info["path"]
        if path.is_file():
            try:captured=capture_file(builder,path,allowed_roots=roots or [repository],native_extent="s1.full_for_interface")
            except (OSError,WireError):
                gaps.append(builder.add('gap',{'subjects':[blob],'reasons':['s1.not_retrieved'],
                    'scope':scope(blob),'source':source('observed',[blob],builder.producer)}));continue
            artifacts.append(captured)
            # A fresh read is a new snapshot. It never refreshes the historical pin.
            from .evidence import Resolver
            actual=hashlib.sha256(Resolver(builder.package([captured])).bytes(captured)).hexdigest()
            if not info.get('sha256') or actual!=info['sha256']:
                gaps.append(builder.add('gap',{'subjects':[blob,captured],'reasons':['s1.historical_digest_not_established'],
                    'scope':scope(blob,captured),'source':source('observed',[blob,captured],builder.producer)}))
        else:
            gaps.append(builder.add("gap",{"subjects":[blob],"reasons":["s1.not_found_at_location"],
                "scope":scope(blob),"source":source("observed",[blob],builder.producer)}))
    outputs=[]
    graphs=[record.graph] if record.graph is not None else list(record.variants.values())
    if domain is None and (n is not None or graphs):
        size=n if n is not None else graphs[0].n
        domain=finite_domain(builder,["legacy position "+str(i) for i in range(size)],[blob])
    associations=[]
    if domain and coordinate_basis in ("original","shown"):
        def related(g,role,name,position=None):
            obj=_graph(builder,g,domain,[blob],role);outputs.append(obj)
            label=builder.add('proposition',{'predicate':contract('native_property'),'arguments':[
                {'role':'s1.subject','value':obj},{'role':'s1.property','value':'legacy.output_name'},
                {'role':'s1.value','value':name}], 'conditioning':[],'scope':scope(obj)})
            associations.append(builder.add('relation',{'relation_contract':contract('legacy_output_role'),
                'endpoints':[{'role':'s1.source','target':blob},{'role':role,'target':obj}],
                'parameters':[label],'scope':scope(obj),'source':source('reconstructed',[blob],builder.producer)}))
            if position is not None:
                associations.append(builder.add('proposition',{'predicate':contract('native_property'),'arguments':[
                    {'role':'s1.subject','value':obj},{'role':'s1.property','value':'legacy.stage_position'},
                    {'role':'s1.value','value':number(position)}],'conditioning':[],'scope':scope(obj)}))
            return obj
        if record.graph is not None:related(record.graph,'s1.native_answer','final')
        for key,g in record.variants.items():related(g,'s1.variant',key)
        for position,(name,g) in enumerate(record.stages or []):related(g,'s1.stage',name,position)
    elif graphs:
        gaps.append(builder.add("gap",{"subjects":[blob],"reasons":["s1.unresolved_identity"],
            "scope":scope(blob),"source":source("reported",[blob],builder.producer)}))
    prop=builder.add("proposition",{"predicate":contract("native_property"),"arguments":[
        {"role":"s1.subject","value":blob},{"role":"s1.property","value":"legacy.status"},
        {"role":"s1.value","value":record.status}],"conditioning":[],"scope":scope(blob)})
    obs=builder.add("observation",{"subject":blob,"proposition":prop,"value":record.status,"scope":scope(blob),
        "source_time":unresolved(),"capture_time":unresolved(),"source":source("reported",[blob],builder.producer),"event":unresolved()})
    for field in ('edge_source','confidence','failure','notes','cost'):
        if getattr(record,field):
            outputs.append(builder.output('native_report',{'type_claim':known(contract('legacy_'+field)),
                'payload':{'artifact':blob,'selector':known({'selector_type':'json_pointer','pointer':'/fields/'+field})},
                'interpretation_gap':[]},evidence=[blob]))
    if record.confidence:
        gaps.append(builder.add('gap',{'subjects':[blob],'reasons':['s1.legacy_confidence_coordinates_or_semantics_unestablished'],
            'scope':scope(blob),'source':source('reported',[blob],builder.producer)}))
    for key,value in record.cost.items():
        if key not in ('usd','calls','seconds') or value is None:continue
        try:numeric=number(value)
        except (ValueError,TypeError):
            gaps.append(builder.add('gap',{'subjects':[blob],'reasons':['s1.unsupported_quantity_value'],
                'scope':scope(blob),'source':source('reported',[blob],builder.producer)}));continue
        kind,unit,rule={'usd':('reported_cost','USD','legacy_reported_cost'),
            'calls':('count','call','legacy_reported_calls'),'seconds':('duration','second','legacy_reported_seconds')}[key]
        outputs.append(builder.output('quantity',{'quantity_kind':'s1.'+kind,'subject':blob,'value':known(numeric,[blob]),
            'units':known({'name':unit,'convention':contract('legacy_'+unit.lower())}),'conditioning':[],
            'basis':known(blob),'procedure':builder.producer,'associated_rule':known(contract(rule))},evidence=[blob]))
    root=evidence_record(builder,artifacts,outputs,subjects=[blob],gaps=gaps,observations=[obs],context=([domain] if domain else [])+associations)
    return {"builder":builder,"package":builder.package([root]),"root":root,"legacy_snapshot":blob,
            "domain":domain,"outputs":outputs,"gaps":gaps,"coordinate_basis":coordinate_basis}


def recorded(adapter_name,battery_id,item_id=None,arm=None):
    from crucis_causal.core import adapter,battery
    ad=adapter.get(adapter_name);bt=battery.get(battery_id)
    item=bt.item(item_id) if item_id else bt.items[0]
    chosen=arm or item.arms[0]
    result=import_record(ad.recorded(item,chosen),n=item.n,coordinate_basis="original")
    result.update({"adapter":ad,"battery":bt,"item":item,"arm":chosen})
    return result


def echo(package,snapshot,resolver=None):
    from .codec import loads
    from .evidence import Resolver
    return decode(loads((resolver or Resolver(package)).bytes(snapshot)))


def project(package,selection,resolver=None):
    """Explicit partial prospective projection. Echo is the historical lossless path."""
    from .api import LegacyProjection
    from .domains import member_map
    from .evidence import Resolver
    from .semantics import validate
    from crucis_causal.core.graph import Graph
    from crucis_causal.core.runs import RunRecord,STATUSES
    resolver=resolver or Resolver(package)
    if selection.projection_rule!=contract('legacy_projection_explicit'):raise WireError('unsupported projection rule')
    report=validate(package,resolver=resolver);report.require()
    assessment=resolver.record(selection.outcome_basis)
    if assessment['record_type']!='s1.assessment' or assessment['payload']['rule']!=contract('legacy_status_explicit'):
        raise WireError('explicit legacy status assessment required')
    outcomes=[c for c in assessment['payload']['conclusions'] if c['facet']=='s1.legacy_status']
    if (len(outcomes)!=1 or outcomes[0]['value']['state']!='known' or outcomes[0]['disputed'] or not outcomes[0]['supporting']):
        raise WireError('unknown or conflicting outcome is not representable by a legacy status')
    status=outcomes[0]['value']['value']
    if status not in STATUSES:raise WireError('legacy status is not established')
    if selection.graph not in assessment['payload']['subjects']:raise WireError('outcome assessment does not cover selected graph')
    if any(c['facet']=='s1.outcome.termination' and c['value'].get('value') in ('failed','interrupted') for c in assessment['payload']['conclusions']) and status=='ok':
        raise WireError('delivered graph followed by failed termination cannot silently become legacy ok')
    pairs,mapping=member_map(package,selection.coordinate_mapping)
    report.require(['s1.mapping_identity'],subjects=[selection.coordinate_mapping['target']])
    if mapping['mapping_kind']!='permutation':raise WireError('legacy graph requires a total coordinate bijection')
    labels=selection.legacy_labels;target=resolver.record(mapping['to'])
    if labels.domain!=mapping['to'] or labels.coordinate_basis not in ('original','shown'):raise WireError('legacy coordinate binding mismatch')
    positions={m['key']:i for i,m in enumerate(target['payload']['members'])}
    def graph(ref):
        record=resolver.record(ref)
        if record['record_type']!='s1.output' or record['payload']['output_type']!='graph':raise WireError('explicit graph output required')
        report.require(['s1.graph_encoding'],subjects=[ref['target']]);body=record['payload']['body']
        if (body['domain']!=mapping['from'] or body['coverage']['extent']!='all_in_domain'
            or body['omission']['within_coverage']!='asserted_absence' or body['coverage']['include_same_node']):
            raise WireError('partial/unknown/same-node coverage cannot become a complete legacy graph')
        D=set();U=set();B=set();P=set()
        marks_to_name={('s1.circle','s1.arrowhead'):'a o-> b',('s1.arrowhead','s1.circle'):'b o-> a',
            ('s1.circle','s1.tail'):'a o- b',('s1.tail','s1.circle'):'b o- a',('s1.circle','s1.circle'):'o-o'}
        for link in body['links']:
            coords=[pairs[(x['domain']['target'],x['key'])] for x in (link['left'],link['right'])]
            a,b=[positions[x['key']] for x in coords];relation=link['relation'];marks=tuple(link['endpoint_marks'])
            if relation==contract('direct_relation') and not marks:D.add((a,b));continue
            pair=tuple(sorted((a,b)))
            if a>b:marks=tuple(reversed(marks))
            if relation==contract('unresolved_adjacency') and marks==('s1.tail','s1.tail'):U.add(pair)
            elif relation==contract('bidirected_relation') and marks==('s1.arrowhead','s1.arrowhead'):B.add(pair)
            elif relation==contract('endpoint_relation') and marks in marks_to_name:P.add((*pair,marks_to_name[marks]))
            elif relation==contract('association') and not marks:P.add((*pair,'associated'))
            else:raise WireError('native endpoint/relation meaning cannot be faithfully projected')
        return Graph(len(positions),frozenset(D),frozenset(U),frozenset(B),frozenset(P))
    g=graph(selection.graph)
    variants={x['role']:graph(x['target']) for x in selection.variants}
    def stage_name(ref):
        names=[]
        for relation in package['records']:
            if relation['record_type']!='s1.relation' or relation['payload']['relation_contract']!=contract('legacy_output_role'):continue
            if {'role':'s1.stage','target':ref} not in relation['payload']['endpoints']:continue
            for parameter in relation['payload']['parameters']:
                label=resolver.record(parameter)
                if label['record_type']!='s1.proposition':continue
                args={a['role']:a['value'] for a in label['payload']['arguments']}
                if args.get('s1.subject')==ref and args.get('s1.property')=='legacy.output_name' and isinstance(args.get('s1.value'),str):
                    names.append(args['s1.value'])
        if len(set(names))!=1:raise WireError('stage name requires an explicit unambiguous legacy naming relation')
        return names[0]
    stages=[(stage_name(ref),graph(ref)) for ref in selection.stages] or None
    component=resolver.record(labels.system)['payload']
    record=RunRecord(component['name'],labels.item,labels.arm,status,graph=g,variants=variants,stages=stages)
    return LegacyProjection(record,tuple(selection.source_records)+(selection.graph,selection.outcome_basis,selection.coordinate_mapping),
        ('richer_provenance_and_unselected_outputs_not_expressible',),(),selection.projection_rule)
