"""Retain actual fixture observations; never manufacture past-run receipts."""
import base64
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
from crucis_causal.execution.model import canonical


def snapshot(view):
    return {'package_id':view.package_id,'digest':view.digest,
            'source_base64':base64.b64encode(view.source_bytes).decode()}


def owner_oracle(owner):
    with closing(sqlite3.connect(owner.path)) as db:
        return {'request_rows':db.execute('SELECT COUNT(*) FROM requests').fetchone()[0],
                'subject_rows':db.execute('SELECT COUNT(*) FROM subjects').fetchone()[0],
                'charges':[r[0] for r in db.execute('SELECT quantity FROM charges')],
                'scope':'Independent local owner SQLite read; not provider invoice or native scientific execution'}


def triplet(case,variant,oracle,prefix,recovered):
    destination=os.environ.get('CRUCIS_S3_CASE_RECEIPTS')
    if not destination:return
    root=Path(__file__).resolve().parents[3]
    folder=Path(destination).resolve()/'faults'/case/variant
    if folder.is_relative_to(root):raise AssertionError('external fault receipts required')
    folder.mkdir(parents=True,exist_ok=True)
    for name,value in [('receiver-oracle',oracle),('history-prefix',prefix),('recovered-view',recovered)]:
        target=folder/(name+'.json')
        with target.open('xb') as stream:stream.write(canonical(value))
