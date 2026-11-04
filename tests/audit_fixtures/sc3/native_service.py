"""Independent synthetic protocol receiver, not a real provider (DLV-08/09).

Supervisor owns lifetime/auth, coordinator owns neither. Bootstrap token arrives
on stdin and is never persisted or returned. SQLite is the independent oracle.
"""
import argparse
import base64
from contextlib import contextmanager
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
import sys
import threading
import uuid
from native_program import discover


def encoded(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
def known(value): return {'state': 'known', 'value': value, 'basis': []}
def unknown(): return {'state': 'unresolved', 'reasons': ['s3.fixture.not_established'], 'evidence': []}
def contract(name): return {'name': name, 'version': '0.1.0-proposal.3'}
def unknown_ref(): return {'binding': 'unresolved', 'target_type': 's3.typed_payload', 'reason': 's3.fixture.validity_not_reported', 'evidence': [], 'source_labels': []}


class Provider:
    def __init__(self, root):
        self.root = Path(root).resolve(); self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root/'provider.sqlite3'; self.barriers = {}; self.lock = threading.RLock()
        config = {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in ('native_service.py', 'native_program.py')}
        with self.db() as db:
            db.executescript('''
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS requests(transmission TEXT PRIMARY KEY,command TEXT NOT NULL,fingerprint BLOB NOT NULL,state TEXT NOT NULL,reply BLOB);
CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,command TEXT NOT NULL,transmission TEXT NOT NULL,native_id TEXT NOT NULL,incarnation TEXT NOT NULL,epoch TEXT NOT NULL,mode TEXT NOT NULL,result BLOB NOT NULL,status TEXT NOT NULL,charge TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS attachments(id TEXT PRIMARY KEY,job TEXT NOT NULL,role TEXT NOT NULL,epoch TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS closed_commands(command TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS requests_log(id INTEGER PRIMARY KEY,method TEXT NOT NULL,body BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS stream_reads(transmission TEXT PRIMARY KEY,fingerprint BLOB NOT NULL,reply BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS stream_acks(source TEXT PRIMARY KEY,position INTEGER NOT NULL,updates INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS actions(id TEXT PRIMARY KEY,job TEXT NOT NULL,label TEXT NOT NULL,context TEXT NOT NULL,question TEXT NOT NULL,available INTEGER NOT NULL,state TEXT NOT NULL,answer BLOB,receipt TEXT,command TEXT);
CREATE TABLE IF NOT EXISTS messages(id TEXT PRIMARY KEY,command TEXT NOT NULL,transmission TEXT NOT NULL,fingerprint BLOB NOT NULL,reply BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS computations(transmission TEXT PRIMARY KEY,body BLOB NOT NULL);
''')
            prior = db.execute('SELECT value FROM meta WHERE key=?', ('config',)).fetchone()
            if prior and json.loads(prior[0]) != config: raise RuntimeError('fixture code drift requires explicit migration')
            for key, value in [('config', encoded(config)), ('namespace', str(uuid.uuid4()).encode()), ('epoch', b'0'), ('tick', b'0')]:
                db.execute('INSERT OR IGNORE INTO meta VALUES(?,?)', (key, value))

    @contextmanager
    def db(self):
        db = sqlite3.connect(self.path, isolation_level=None, timeout=5); db.row_factory = sqlite3.Row
        try:
            if db.execute('PRAGMA journal_mode=DELETE').fetchone()[0].lower() != 'delete': raise RuntimeError('fixture journal profile')
            db.execute('PRAGMA synchronous=FULL'); db.execute('PRAGMA foreign_keys=ON')
            if db.execute('PRAGMA synchronous').fetchone()[0] != 2: raise RuntimeError('fixture sync profile')
            yield db
        finally: db.close()

    @staticmethod
    def meta(db, key): return bytes(db.execute('SELECT value FROM meta WHERE key=?', (key,)).fetchone()[0]).decode()

    def descriptor(self, row, db):
        return {'authority': 'S3_owned_fixture_provider', 'namespace': self.meta(db, 'namespace'), 'native_id': row['native_id'],
            'incarnation': known(row['incarnation']), 'identity_rule': contract('s3.fixture.native_incarnation'), 'validity': unknown_ref(), 'basis': []}

    def dispatch(self, value):
        if not isinstance(value, dict) or not isinstance(value.get('method'), str): raise ValueError('closed fixture request required')
        method = value['method']
        with self.db() as db: db.execute('INSERT INTO requests_log(method,body) VALUES(?,?)', (method, encoded(value)))
        if method == 'launch': return self.launch(value)
        if method in ('observe', 'ack_source', 'query_ack'): return self.stream(value)
        if method in ('setup_actions','information','compute','answer_bundle','lookup_answer','expire_action','change_action_context','interaction_oracle'):
            return self.interact(value)
        if method == 'arm_ack_loss':
            with self.db() as db: db.execute('INSERT OR REPLACE INTO meta VALUES(?,?)',('lose_ack',b'1'))
            return {'armed': True}
        if method == 'arm_delivery_loss':
            with self.db() as db:db.execute('INSERT OR REPLACE INTO meta VALUES(?,?)',('lose_delivery',b'1'))
            return {'armed':True}
        if method == 'advance_tick':
            with self.db() as db:
                db.execute('BEGIN IMMEDIATE'); tick = int(self.meta(db,'tick')) + int(value['amount'])
                if int(value['amount']) < 0: raise ValueError('fixture time cannot regress')
                db.execute('UPDATE meta SET value=? WHERE key=?',(str(tick).encode(),'tick'));db.execute('COMMIT')
            return {'tick': str(tick)}
        if method == 'query':
            with self.db() as db:
                db.execute('BEGIN')
                matches = db.execute('SELECT * FROM jobs WHERE command=? ORDER BY rowid', (value['command'],)).fetchall()
                closed = db.execute('SELECT 1 FROM closed_commands WHERE command=?', (value['command'],)).fetchone() is not None
                namespace, epoch = self.meta(db, 'namespace'), self.meta(db, 'epoch')
                result = {'classification': 'unknown' if value.get('unavailable', False) else 'positive' if matches else 'negative',
                    'matches': [] if value.get('unavailable', False) else [self.descriptor(row, db) for row in matches],
                    'complete': not value.get('unavailable', False), 'no_late_acceptance': closed,
                    'namespace': namespace, 'epoch': epoch, 'pending': db.execute('SELECT COUNT(*) FROM requests WHERE command=? AND state=?', (value['command'], 'pending')).fetchone()[0],
                    'paths': ['authenticated_fixture_http'], 'retention': 'all_fixture_history',
                    'charges': [row['charge'] for row in matches], 'command': value['command']}
                db.execute('COMMIT'); return result
        if method == 'attach':
            with self.db() as db:
                db.execute('BEGIN IMMEDIATE'); epoch = self.meta(db, 'epoch')
                descriptor = value['descriptor']
                if value['epoch'] != epoch: raise ValueError('stale receiver epoch')
                if descriptor['authority'] != 'S3_owned_fixture_provider' or descriptor['namespace'] != self.meta(db, 'namespace') or descriptor['incarnation'].get('state') != 'known':
                    raise ValueError('native scope unestablished')
                row = db.execute('SELECT * FROM jobs WHERE native_id=? ORDER BY rowid DESC LIMIT 1', (descriptor['native_id'],)).fetchone()
                if row is None or row['incarnation'] != descriptor['incarnation']['value']: raise ValueError('native incarnation mismatch')
                if value['role'] not in ('observer', 'controller', 'consumer'): raise ValueError('unsupported role')
                connection = str(uuid.uuid4())
                db.execute('INSERT INTO attachments VALUES(?,?,?,?)', (connection, row['id'], value['role'], epoch)); db.execute('COMMIT')
                return {'connection': connection, 'descriptor': self.descriptor(row, db), 'role': value['role'], 'epoch': epoch}
        if method == 'rotate_epoch':
            with self.db() as db:
                db.execute('BEGIN IMMEDIATE'); epoch = str(int(self.meta(db, 'epoch')) + 1)
                db.execute('UPDATE meta SET value=? WHERE key=?', (epoch.encode(), 'epoch')); db.execute('COMMIT'); return {'epoch': epoch}
        if method == 'close_command':
            with self.db() as db: db.execute('INSERT OR IGNORE INTO closed_commands VALUES(?)', (value['command'],))
            return {'closed': value['command']}
        if method in ('await_pending', 'release'):
            with self.lock: pair = self.barriers.setdefault(value['transmission'], (threading.Event(), threading.Event()))
            if method == 'await_pending':
                if not pair[0].wait(timeout=15): raise ValueError('pending barrier absent')
                return {'pending': value['transmission']}
            pair[1].set(); return {'released': value['transmission']}
        if method == 'oracle':
            with self.db() as db:
                return {'namespace': self.meta(db, 'namespace'), 'epoch': self.meta(db, 'epoch'),
                    'jobs': [dict(row) | {'result': base64.b64encode(bytes(row['result'])).decode()} for row in db.execute('SELECT * FROM jobs ORDER BY rowid')],
                    'requests': [dict(row) | {'fingerprint': bytes(row['fingerprint']).decode(), 'reply': json.loads(row['reply']) if row['reply'] else None} for row in db.execute('SELECT * FROM requests ORDER BY rowid')],
                    'attachments': [dict(row) for row in db.execute('SELECT * FROM attachments ORDER BY rowid')],
                    'stream_reads': [{'transmission': r['transmission'], 'reply': json.loads(r['reply'])} for r in db.execute('SELECT * FROM stream_reads ORDER BY rowid')],
                    'stream_acks': [dict(r) for r in db.execute('SELECT * FROM stream_acks ORDER BY rowid')]}
        raise ValueError('unsupported fixture method')

    def interact(self,value):
        method=value['method']
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            if method=='setup_actions':
                job=db.execute('SELECT * FROM jobs WHERE id=?',(value['job'],)).fetchone()
                if job is None or db.execute('SELECT 1 FROM actions WHERE job=?',(job['id'],)).fetchone():raise ValueError('new explicit interaction fixture required')
                for i in range(2):
                    db.execute('INSERT INTO actions VALUES(?,?,?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),job['id'],'Q'+str(i+1),str(uuid.uuid4()),'Continue?',int(i==0 or value['all_sources']), 'open',None,None,None))
                rows=[dict(r) for r in db.execute('SELECT * FROM actions WHERE job=? ORDER BY label',(job['id'],))];db.execute('COMMIT')
                return {'session':job['id'],'actions':rows,'capacity':'2','native_termination':unknown()}
            if method=='interaction_oracle':
                rows=[dict(r) for r in db.execute('SELECT * FROM actions ORDER BY label')]
                for r in rows:r['answer']=base64.b64encode(bytes(r['answer'])).decode() if r['answer'] is not None else None
                return {'actions':rows,'physical_messages':str(db.execute('SELECT COUNT(*) FROM messages').fetchone()[0]),
                    'deliveries':str(sum(r['state']=='answered' for r in rows)),'consumed':str(sum(r['state']=='answered' for r in rows)),
                    'remaining':str(2-sum(r['state']=='answered' for r in rows)),'computations':str(db.execute('SELECT COUNT(*) FROM computations').fetchone()[0]),'native_termination':unknown()}
            if method in ('expire_action','change_action_context'):
                if method=='expire_action':db.execute('UPDATE actions SET state=? WHERE id=?',('expired',value['action']))
                else:db.execute('UPDATE actions SET context=? WHERE id=?',(str(uuid.uuid4()),value['action']))
                db.execute('COMMIT');return {'changed':value['action']}
            if method in ('information','compute'):
                row=db.execute('SELECT * FROM actions WHERE id=?',(value['action'],)).fetchone()
                if row is None or row['context']!=value['context']:raise ValueError('action context mismatch')
                if not row['available']:return {'state':'unavailable','action':row['id'],'context':row['context']}
                source=encoded({'action':row['id'],'context':row['context'],'answer':True,'scope':'synthetic_configured_source_not_scientific_truth'})
                if method=='compute':
                    if base64.b64decode(value['source'],validate=True)!=source:raise ValueError('computation source mismatch')
                    db.execute('INSERT INTO computations VALUES(?,?)',(value['transmission'],encoded(value)));db.execute('COMMIT')
                return {'state':'available','action':row['id'],'context':row['context'],'bytes':base64.b64encode(source).decode()}
            if method=='lookup_answer':
                rows=db.execute('SELECT reply FROM messages WHERE command=? ORDER BY rowid',(value['command'],)).fetchall()
                return {'classification':'positive' if rows else 'negative','matches':[json.loads(r['reply']) for r in rows], 'complete':True,'no_late_acceptance':False}
            if method!='answer_bundle':raise ValueError('unsupported interaction')
            if value['epoch']!=self.meta(db,'epoch') or value['atomicity']!='all_or_none' or not 1<=len(value['entries'])<=2:raise ValueError('native bundle contract')
            rows=[];ids=set()
            for entry in value['entries']:
                row=db.execute('SELECT * FROM actions WHERE id=?',(entry['action'],)).fetchone()
                if row is None or row['context']!=entry['context'] or row['state']!='open' or row['job']!=value['session'] or row['id'] in ids:
                    return {'accepted':False,'reason':'closed_or_changed_action','consumed':'0'}
                ids.add(row['id']);rows.append(row)
            if sum(1 for r in db.execute('SELECT state FROM actions WHERE job=?',(value['session'],)) if r['state']=='answered')+len(rows)>2:
                return {'accepted':False,'reason':'policy_exhausted','consumed':'0'}
            message=str(uuid.uuid4());receipt=str(uuid.uuid4())
            reply={'accepted':True,'message':message,'receipt':receipt,'command':value['command'],'transmission':value['transmission'],
                'atomicity':'all_or_none','entries':value['entries'],'consumed':str(len(rows)),'native_use':unknown(),'native_termination':unknown()}
            for row,entry in zip(rows,value['entries']):
                answer=base64.b64decode(entry['bytes'],validate=True)
                db.execute('UPDATE actions SET state=?,answer=?,receipt=?,command=? WHERE id=?',('answered',answer,receipt,value['command'],row['id']))
            db.execute('INSERT INTO messages VALUES(?,?,?,?,?)',(message,value['command'],value['transmission'],encoded(value),encoded(reply)))
            lose=db.execute('SELECT value FROM meta WHERE key=?',('lose_delivery',)).fetchone();drop=bool(lose and bytes(lose[0])==b'1')
            if drop:db.execute('UPDATE meta SET value=? WHERE key=?',(b'0','lose_delivery'))
            db.execute('COMMIT')
            reply['_drop_reply']=drop
            return reply

    def stream(self, value):
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            descriptor = value['descriptor']; epoch = self.meta(db, 'epoch')
            if value['epoch'] != epoch or descriptor['authority'] != 'S3_owned_fixture_provider' or descriptor['namespace'] != self.meta(db, 'namespace'):
                raise ValueError('source receiver scope mismatch')
            row = db.execute('SELECT * FROM jobs WHERE native_id=? ORDER BY rowid DESC LIMIT 1', (descriptor['native_id'],)).fetchone()
            if row is None or descriptor['incarnation'] != known(row['incarnation']): raise ValueError('source incarnation mismatch')
            if value['partition'] not in ('p0','p1') or not isinstance(value['consumer'], str) or not value['consumer']:
                raise ValueError('explicit source/filter/consumer required')
            expected_filter = hashlib.sha256(encoded({'kind': 'all_fixture_events', 'partition': value['partition'], 'consumer': value['consumer']})).hexdigest()
            if value['filter_digest'] != expected_filter: raise ValueError('filter semantics mismatch')
            source = encoded([row['id'], row['incarnation'], value['partition'], value['consumer'], expected_filter]).decode()
            ack = db.execute('SELECT * FROM stream_acks WHERE source=?', (source,)).fetchone()
            if value['method'] == 'query_ack':
                return {'position': str(ack['position']) if ack else None, 'updates': str(ack['updates']) if ack else '0', 'epoch': epoch}
            if value['method'] == 'ack_source':
                position = int(value['position'])
                if not 0 <= position <= 3 or ack and position < ack['position']: raise ValueError('ACK position invalid')
                if ack is None: db.execute('INSERT INTO stream_acks VALUES(?,?,?)', (source, position, 1))
                elif position > ack['position']: db.execute('UPDATE stream_acks SET position=?,updates=updates+1 WHERE source=?', (position, source))
                after = db.execute('SELECT * FROM stream_acks WHERE source=?', (source,)).fetchone()
                lose = db.execute('SELECT value FROM meta WHERE key=?',('lose_ack',)).fetchone()
                drop = bool(lose and bytes(lose[0]) == b'1')
                if drop: db.execute('UPDATE meta SET value=? WHERE key=?',(b'0','lose_ack'))
                db.execute('COMMIT')
                return {'position': str(after['position']), 'updates': str(after['updates']), 'generation': row['incarnation'], 'filter_digest': expected_filter, 'consumer': value['consumer'], '_drop_reply': drop}
            prior = db.execute('SELECT * FROM stream_reads WHERE transmission=?', (value['transmission'],)).fetchone()
            fingerprint = encoded(value)
            if prior:
                if bytes(prior['fingerprint']) != fingerprint: raise ValueError('read transmission conflict')
                return json.loads(prior['reply'])
            start = int(value['position']); max_events = int(value['max_events']); max_bytes = int(value['max_bytes'])
            if not 0 <= start <= 3 or not 1 <= max_events <= 100 or not 1 <= max_bytes <= 1048576 or value['deadline'] != 'fixture_tick:10':
                raise ValueError('bounded fixture stream required')
            if int(self.meta(db,'tick')) >= 10: raise ValueError('fixture receiver deadline expired')
            events = [('E2', '2', b'{"graph":'), ('E1','1', bytes(row['result'])), ('E1','1', bytes(row['result']))]
            returned, size = [], 0
            for offset, (event, sequence, raw) in enumerate(events[start:], start):
                if len(returned) == max_events or size + len(raw) > max_bytes: break
                returned.append({'capture': str(uuid.uuid4()), 'event': event, 'sequence': sequence, 'offset': str(offset), 'bytes': base64.b64encode(raw).decode()}); size += len(raw)
            reply = {'batch': str(uuid.uuid4()), 'entries': returned, 'next_position': str(start + len(returned)),
                'generation': row['incarnation'], 'filter_digest': expected_filter, 'consumer': value['consumer'], 'partition': value['partition'],
                'complete_source_history': start + len(returned) == 3, 'native_termination': unknown()}
            db.execute('INSERT INTO stream_reads VALUES(?,?,?)', (value['transmission'], fingerprint, encoded(reply))); db.execute('COMMIT')
            return reply

    def launch(self, value):
        required = {'method', 'command', 'transmission', 'binding_digest', 'epoch', 'mode', 'data', 'pause', 'drop_reply', 'native_id'}
        if set(value) != required: raise ValueError('closed launch grammar')
        fingerprint = encoded(value)
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            prior = db.execute('SELECT * FROM requests WHERE transmission=?', (value['transmission'],)).fetchone()
            if prior:
                if bytes(prior['fingerprint']) != fingerprint: raise ValueError('transmission identity conflict')
                reply = json.loads(prior['reply']) if prior['reply'] else {'acceptance': unknown(), 'pending': True}
                db.execute('COMMIT'); return reply
            db.execute('INSERT INTO requests VALUES(?,?,?,?,?)', (value['transmission'], value['command'], fingerprint, 'pending', None)); db.execute('COMMIT')
        if value['pause']:
            with self.lock: pair = self.barriers.setdefault(value['transmission'], (threading.Event(), threading.Event()))
            pair[0].set()
            if not pair[1].wait(timeout=30): return {'acceptance': unknown(), 'pending': True}
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE'); epoch = self.meta(db, 'epoch')
            closed = db.execute('SELECT 1 FROM closed_commands WHERE command=?', (value['command'],)).fetchone()
            if value['epoch'] != epoch or closed:
                reply = {'acceptance': known(False), 'reason': 'stale_epoch' if value['epoch'] != epoch else 'command_closed', 'epoch': epoch}
                db.execute('UPDATE requests SET state=?,reply=? WHERE transmission=?', ('rejected', encoded(reply), value['transmission'])); db.execute('COMMIT'); return reply
            data = base64.b64decode(value['data'], validate=True); result = discover(data)
            if value['mode'] not in ('local', 'remote', 'interactive', 'checkpoint'): raise ValueError('unsupported fixture mode')
            job = str(uuid.uuid4()); native_id = value['native_id'] or str(uuid.uuid4()); incarnation = str(uuid.uuid4())
            charge = '0.7' if value['mode'] == 'local' else '4' if value['mode'] == 'remote' else '0' if value['mode'] == 'interactive' else '3'
            db.execute('INSERT INTO jobs VALUES(?,?,?,?,?,?,?,?,?,?)', (job, value['command'], value['transmission'], native_id, incarnation, epoch, value['mode'], result, 'accepted', charge))
            row = db.execute('SELECT * FROM jobs WHERE id=?', (job,)).fetchone()
            reply = {'acceptance': known(True), 'descriptor': self.descriptor(row, db), 'charge': charge, 'epoch': epoch, 'job': job}
            db.execute('UPDATE requests SET state=?,reply=? WHERE transmission=?', ('accepted', encoded(reply), value['transmission'])); db.execute('COMMIT')
        return reply


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass
    def do_POST(self):
        if self.path != '/v1' or self.headers.get('Authorization') != 'Bearer ' + self.server.bootstrap_token:
            self.send_error(403); return
        try:
            length = int(self.headers.get('Content-Length', '-1'))
            if not 0 <= length <= 1048576: raise ValueError('bounded request required')
            raw = self.rfile.read(length)
            value = json.loads(raw)
            result = self.server.provider.dispatch(value)
            # Actual receiver commit above precedes this deterministic ACK loss.
            if result.pop('_drop_reply', False) or value.get('drop_reply', False): self.close_connection = True; return
            body = encoded({'ok': True, 'value': result})
        except Exception:
            # No token, raw exception/header/body values in diagnostic reply.
            body = encoded({'ok': False, 'reason': 'fixture_request_rejected'})
        try:
            self.send_response(200); self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError): pass


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--root', required=True); args = parser.parse_args()
    line = sys.stdin.readline(4097)
    bootstrap = json.loads(line)
    if set(bootstrap) != {'token'} or not isinstance(bootstrap['token'], str) or len(bootstrap['token']) < 32: raise ValueError('actual supervisor bootstrap required')
    provider = Provider(args.root); server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.daemon_threads = True; server.provider = provider; server.bootstrap_token = bootstrap['token']
    with provider.db() as db: namespace, epoch = provider.meta(db, 'namespace'), provider.meta(db, 'epoch')
    print(json.dumps({'address': list(server.server_address), 'namespace': namespace, 'epoch': epoch}), flush=True)
    server.serve_forever(poll_interval=0.1)


if __name__ == '__main__': main()
