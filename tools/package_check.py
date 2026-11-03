"""Offline package integrity and namespace checks; no research data required."""
import ast
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
for path in (ROOT/'crucis_causal').rglob('*.py'):
    ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
from crucis_causal.connections.codec import loads
from crucis_causal.connections.schema import schema
from crucis_causal.experiments.schema import schema as s2schema
from crucis_causal.core.graph import Graph
assert schema() and s2schema()
assert Graph.from_edges(2,[(0,1)]).n==2
for module in ('crucis_causal','crucis_causal.connections','crucis_causal.experiments'):
    subprocess.run([sys.executable,'-B','-m',module,'--help'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
for forbidden in ('score','cc_graph','probe_io','lineage','partial_stages','harness','analysis'):
    assert forbidden not in sys.modules, 'external research module loaded: '+forbidden
print(json.dumps({'package':'crucis_causal','syntax':'pass','schemas':'pass','cli':'pass','external_source_imports':False}))
