from pathlib import Path
import json,subprocess,hashlib
EP=Path(__file__).resolve().parent
m=json.loads((EP/'remotion/src/edit-manifest.json').read_text())
assert m['voiceComplete'], 'Voice generation is incomplete'
assert m['composition']['width']==1280 and m['composition']['height']==720
assert m['composition']['fps']==30
cursor=0
for s in m['scenes']:
 assert s['start']==cursor and isinstance(s['duration'],int) and s['duration']>0,s['id']
 if s.get('audio'):
  p=EP/'remotion/public'/s['audio'];assert p.exists(),p
  seconds=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)]))
  assert seconds*30<=s['duration']+.01,s['id']
 cursor+=s['duration']
assert cursor==m['composition']['durationInFrames']
previous=0
for c in m['captions']:
 assert isinstance(c['start'],int) and isinstance(c['end'],int)
 assert 0<=c['start']<c['end']<=cursor,c
 assert c['start']>=previous,c
 assert len(c['text'].splitlines())<=2,c
 assert max(map(len,c['text'].splitlines()))<=32,c
 previous=c['end']
for r in json.loads((EP/'voice_generation_record.json').read_text()):
 assert hashlib.sha256((EP/r['path']).read_bytes()).hexdigest()==r['sha256'],r['id']
 assert r['monsterize']==(r['speaker']=='sobaya')
print('PASS:',len(m['scenes']),'scenes;',len(m['captions']),'captions;',cursor,'frames;',round(cursor/30,2),'seconds')
