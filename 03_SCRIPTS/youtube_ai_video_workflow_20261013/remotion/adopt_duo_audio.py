"""Archive only the narration selected by the reviewed final manifest."""
from pathlib import Path
import argparse,hashlib,json,os
P=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--version',default='v3');args=parser.parse_args()
m=json.loads((P/'src/edit-manifest.json').read_text());rows=[]
for d in m['dialogue']:
 src=P/'public'/d['audio'];sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha==d['audioSha256']
 name=f"duo_{args.version}_{d['id']}_{d['who']}.wav";dst=P.parent/name
 if dst.exists():assert hashlib.sha256(dst.read_bytes()).hexdigest()==sha, dst
 else:os.link(src,dst)
 rows.append({'id':d['id'],'speaker':d['who'],'file':name,'publicAudio':d['audio'],'sha256':sha,'text':d['text'],'settings':d['voiceSettings']})
(P.parent/'duo_adopted_audio.json').write_text(json.dumps({'version':args.version,'count':len(rows),'audio':rows},ensure_ascii=False,indent=2))
print('ARCHIVED',len(rows))
