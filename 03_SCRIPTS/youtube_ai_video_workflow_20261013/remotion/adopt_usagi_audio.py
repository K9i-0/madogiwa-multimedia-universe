"""Archive only newly adopted v4 Takosan WAVs; Yametaro stays at v3 paths."""
from pathlib import Path
import json,hashlib,os
P=Path(__file__).resolve().parent;m=json.loads((P/'src/edit-manifest.json').read_text());rows=[]
for d in m['dialogue']:
 if d['who']!='takosan':continue
 src=P/'public'/d['audio'];sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha==d['audioSha256']
 name=f'usagi_v4_{d["id"]}_takosan.wav';dst=P.parent/name
 if dst.exists():assert hashlib.sha256(dst.read_bytes()).hexdigest()==sha
 else:os.link(src,dst)
 rows.append({'id':d['id'],'file':name,'publicAudio':d['audio'],'sha256':sha,'text':d['text'],'settings':d['voiceSettings']})
(P.parent/'usagi_adopted_audio_v4.json').write_text(json.dumps({'version':4,'credit':'VOICEVOX:中国うさぎ','count':len(rows),'audio':rows},ensure_ascii=False,indent=2));print('ARCHIVED',len(rows))
