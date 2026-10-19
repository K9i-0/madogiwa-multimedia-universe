from pathlib import Path
import json,wave,re
P=Path(__file__).resolve().parent;m=json.loads((P/'src/edit-manifest.json').read_text());errors=[];end=0
for d in m['dialogue']:
 if d['startFrame']<end:errors.append('dialogue overlap '+d['id'])
 end=d['startFrame']+d['durationInFrames']
 if ''.join(c['text'].replace('\n','') for c in d['captions'])!=d['text']:errors.append('caption mismatch '+d['id'])
 previous=0
 for c in d['captions']:
  if c['fromFrame']!=previous or c['toFrame']<=previous:errors.append('caption gap '+d['id'])
  if len(c['text'].splitlines())>2 or any(len(line)>28 for line in c['text'].splitlines()):errors.append('caption overflow '+d['id'])
  previous=c['toFrame']
 if previous!=d['durationInFrames']:errors.append('caption duration '+d['id'])
 with wave.open(str(P.parent/d['audio'])) as w:
  if abs(w.getnframes()/w.getframerate()-d['durationInFrames']/30)>.034:errors.append('audio duration '+d['id'])
 for c in m['clips']:
  if d['startFrame']<c['startFrame']+c['durationInFrames'] and end>c['startFrame']:errors.append('clip/dialogue overlap '+d['id'])
 if not (P/d['queryFile']).exists():errors.append('missing query '+d['id'])
for c in m['clips']:
 if not (P/'public'/c['src']).exists():errors.append('missing clip '+c['src'])
r=dict(errors=errors,dialogueCount=len(m['dialogue']),viewCount=len(set(d['view'] for d in m['dialogue'])),frames=m['composition']['durationInFrames'],durationSeconds=m['composition']['durationInFrames']/30,subtitleMaxLines=2,introVoiceStartFrame=m['dialogue'][0]['startFrame'],clips=m['clips'])
(P.parent/'qa_structure.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False));assert not errors
