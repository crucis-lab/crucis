"""Independent scoped model/optimizer receiver; no causal or replay oracle."""
import base64
import json
from pathlib import Path
import sys
import uuid
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'sc3'))
import native_service as native

STATE=b'{"model":[2,4],"optimizer":{"step":7}}'


class Provider(native.Provider):
    def __init__(self,root):
        super().__init__(root)
        with self.db() as db:
            db.executescript('''
CREATE TABLE IF NOT EXISTS checkpoints(id TEXT PRIMARY KEY,job TEXT NOT NULL,data BLOB NOT NULL,valid INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS recovery_commands(transmission TEXT PRIMARY KEY,fingerprint BLOB NOT NULL,reply BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS loaded(job TEXT PRIMARY KEY,data BLOB NOT NULL);
''')

    def dispatch(self,v):
        m=v['method']
        if m not in ('checkpoint','request_stop','finish_stop','inspect_stop','expire_checkpoint','restart','restore','inspect_loaded','recovery_oracle'):
            return super().dispatch(v)
        with self.db() as db:
            db.execute('INSERT INTO requests_log(method,body) VALUES(?,?)',(m,native.encoded(v)))
            db.execute('BEGIN IMMEDIATE')
            if m=='checkpoint':
                if db.execute('SELECT 1 FROM jobs WHERE id=?',(v['job'],)).fetchone() is None:raise ValueError('unknown predecessor')
                key=str(uuid.uuid4());db.execute('INSERT INTO checkpoints VALUES(?,?,?,1)',(key,v['job'],STATE))
                out={'id':key,'job':v['job'],'bytes':base64.b64encode(STATE).decode(),'available':True,'loaded':native.unknown()}
            elif m=='expire_checkpoint':
                db.execute('UPDATE checkpoints SET valid=0 WHERE id=?',(v['id'],));out={'expired':v['id']}
            elif m=='finish_stop':
                db.execute('UPDATE jobs SET status=?,charge=? WHERE id=?',('stopped','5',v['job']));out={'observed_stopped':True,'final_bill':'5'}
            elif m=='inspect_stop':
                row=db.execute('SELECT * FROM jobs WHERE id=?',(v['job'],)).fetchone()
                if row is None:raise ValueError('unknown predecessor')
                out={'job':row['id'],'observed_stopped':row['status']=='stopped','scope':'component','descendants':native.unknown()}
            elif m=='inspect_loaded':
                row=db.execute('SELECT data FROM loaded WHERE job=?',(v['job'],)).fetchone()
                out={'job':v['job'],'components':['model','optimizer'] if row else [],'bytes':base64.b64encode(bytes(row[0])).decode() if row else None,'rng':native.unknown(),'history':native.unknown()}
            elif m=='recovery_oracle':
                out={'jobs':[dict(r)|{'result':base64.b64encode(bytes(r['result'])).decode()} for r in db.execute('SELECT * FROM jobs ORDER BY rowid')],
                    'loads':[{**dict(r),'data':base64.b64encode(bytes(r['data'])).decode()} for r in db.execute('SELECT * FROM loaded')],
                    'commands':str(db.execute('SELECT COUNT(*) FROM recovery_commands').fetchone()[0])}
            else:
                fingerprint=native.encoded(v)
                old=db.execute('SELECT * FROM recovery_commands WHERE transmission=?',(v['transmission'],)).fetchone()
                if old:
                    if bytes(old['fingerprint'])!=fingerprint:raise ValueError('same D changed effect')
                    db.execute('COMMIT');return json.loads(old['reply'])
                if v['epoch']!=self.meta(db,'epoch'):raise ValueError('stale epoch')
                if m=='request_stop':
                    if v['scope']!='component' or db.execute('SELECT 1 FROM jobs WHERE id=?',(v['job'],)).fetchone() is None:raise ValueError('unsupported stop scope')
                    db.execute('UPDATE jobs SET status=? WHERE id=? AND status<>?',('stop_requested',v['job'],'stopped'))
                    out={'accepted':True,'job':v['job'],'observed_stopped':False,'scope':'component','descendants':native.unknown()}
                else:
                    checkpoint=db.execute('SELECT * FROM checkpoints WHERE id=?',(v['checkpoint'],)).fetchone() if v['source_type']=='native_reference' else None
                    data=bytes(checkpoint['data']) if checkpoint and checkpoint['valid'] else base64.b64decode(v['bytes'],validate=True) if v['source_type']=='captured_payload' else None
                    if data!=STATE:raise ValueError('missing/expired/substituted checkpoint')
                    if m=='restart':
                        previous=db.execute('SELECT * FROM jobs WHERE id=?',(v['predecessor'],)).fetchone()
                        if previous is None or previous['status']!='stopped':raise ValueError('strict nonoverlap')
                        if checkpoint and checkpoint['job']!=previous['id']:raise ValueError('checkpoint origin mismatch')
                        job=str(uuid.uuid4());incarnation=str(uuid.uuid4())
                        db.execute('INSERT INTO jobs VALUES(?,?,?,?,?,?,?,?,?,?)',(job,v['command'],v['transmission'],job,incarnation,v['epoch'],'checkpoint',previous['result'],'quiescent','4'))
                        # Native acceptance and loading are intentionally separate.
                        out={'accepted':True,'job':job,'descriptor':self.descriptor(db.execute('SELECT * FROM jobs WHERE id=?',(job,)).fetchone(),db),'loaded':native.unknown(),'charge':'4'}
                    else:
                        row=db.execute('SELECT * FROM jobs WHERE id=?',(v['job'],)).fetchone()
                        if row is None or row['status']!='quiescent':raise ValueError('in-place restore requires quiescence')
                        db.execute('INSERT OR REPLACE INTO loaded VALUES(?,?)',(v['job'],data))
                        out={'accepted':True,'job':v['job'],'components':['model','optimizer'],'bytes':base64.b64encode(data).decode(),'rng':native.unknown(),'history':native.unknown()}
                db.execute('INSERT INTO recovery_commands VALUES(?,?,?)',(v['transmission'],fingerprint,native.encoded(out)))
            db.execute('COMMIT')
        if v.get('drop_reply'):out['_drop_reply']=True
        return out


if __name__=='__main__':
    native.Provider=Provider
    native.main()
