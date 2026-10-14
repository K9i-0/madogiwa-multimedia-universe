from pathlib import Path
import json,hashlib,wave,unicodedata
P=Path(__file__).resolve().parent;m=json.loads((P/'src/edit-manifest-v3.json').read_text());last=0;warnings=[]
for d in m['dialogue']:
 assert d['startFrame']>=last,d['id'];last=d['startFrame']+d['durationInFrames'];assert last<=m['composition']['durationInFrames']
 p=P/'public'/d['audio'];assert p.exists(),str(p);assert hashlib.sha256(p.read_bytes()).hexdigest()==d['audioSha256'],d['id']
 segs=d['captionSegments'];assert segs[0]['startFrame']==0 and segs[-1]['endFrame']==d['durationInFrames'];cursor=0
 for s in segs:
  assert s['startFrame']==cursor and s['endFrame']>cursor;cursor=s['endFrame'];assert len(s['text'].splitlines())<=2
  if max(sum(1 if unicodedata.east_asian_width(c) in ('F','W','A') else .5 for c in line) for line in s['text'].splitlines())>28:warnings.append((d['id'],s['text']))
with wave.open(str(P/'public/mixed-v3.wav')) as w:assert w.getframerate()==48000 and w.getnchannels()==2 and abs(w.getnframes()/48000-m['composition']['durationInFrames']/30)<.001
print('PASS',len(m['dialogue']),'utterances',m['composition']['durationInFrames'],'frames','caption warnings',warnings)
