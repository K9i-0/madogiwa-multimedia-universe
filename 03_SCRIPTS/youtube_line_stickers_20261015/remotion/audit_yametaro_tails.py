"""Read-only VAD/RMS screening of the generated body dialogue.

This report locates tails for review; it never automatically deletes samples.
A whole-utterance ASR endpoint is not a safe phoneme cut boundary.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time
import numpy as np
import torch

P = Path(__file__).resolve().parent
R = P.parents[2]
sys.path.insert(0, str(R / '.local/silero-vad-analysis/src'))
from silero_vad.utils_vad import get_speech_timestamps, init_jit_model
torch.set_num_threads(1)
vad = init_jit_model(str(R / '.local/silero-vad-analysis/src/silero_vad/data/silero_vad.jit'))
report_file = P / 'out/yametaro_tail_audit_v3.json'
report = json.loads(report_file.read_text()) if report_file.exists() else {'subjectiveListening':False, 'audioChanged':False,
 'sileroRevision':'1e261b036686cd0017d500ee96acd1c4ba572a9d','note':'Review candidates only. VAD and RMS do not determine safe cut points.', 'utterances':[]}
seen={r['audioSha256'] for r in report['utterances']}
targets={r['id'] for r in json.loads((P/'dialogue.json').read_text()) if r['who']=='yametaro' and not r['id'].startswith(('intro-','main-'))}

def islands(mask):
 active=np.flatnonzero(mask)
 for a,b in zip(active[:-1],active[1:]):
  if b-a<=8: mask[a:b+1]=True
 padded=np.pad(mask.astype(np.int8),(1,1))
 return [(int(a),int(b)) for a,b in zip(np.flatnonzero(np.diff(padded)==1),np.flatnonzero(np.diff(padded)==-1)) if b-a>=2]

while True:
 try: rows=json.loads((P/'out/voice_progress.json').read_text())
 except (FileNotFoundError,json.JSONDecodeError):
  time.sleep(3); continue
 selected=[r for r in rows if r['id'] in targets]
 for row in selected:
  if row['audioSha256'] in seen: continue
  source=P/'public'/row['audio']
  assert hashlib.sha256(source.read_bytes()).hexdigest()==row['audioSha256']
  raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(source),'-f','f32le','-ar','16000','-ac','1','-'])
  x=np.frombuffer(raw,dtype='<f4').copy()
  rms=np.array([np.sqrt(np.mean(x[i:i+160]**2)) for i in range(0,len(x),160)])
  db=20*np.log10(np.maximum(rms,1e-9)); threshold=max(-48.,float(np.percentile(db,95))-34)
  active=[{'start':a*.01,'end':min(len(x)/16000,b*.01),'peakRmsDb':round(float(np.max(db[a:b])),2)} for a,b in islands(db>threshold)]
  speech={str(level):get_speech_timestamps(torch.from_numpy(x),vad,sampling_rate=16000,threshold=level,min_speech_duration_ms=80,min_silence_duration_ms=100,speech_pad_ms=0,return_seconds=True) for level in [.25,.5]}
  last=speech['0.5'][-1]['end'] if speech['0.5'] else 0
  tail_peak=round(float(np.max(db[int(last*100):])),2) if int(last*100)<len(db) else None
  row_result={'id':row['id'],'audio':row['audio'],'audioSha256':row['audioSha256'],'text':row['text'],'durationSeconds':len(x)/16000,'sileroVAD':speech,'rmsWindowSeconds':.01,'rmsThresholdDb':threshold,'rmsIslands':active,'rmsDb':[round(float(v),2) for v in db], 'tailAfterVadSeconds':round(len(x)/16000-last,3),'tailAfterVadPeakRmsDb':tail_peak}
  report['utterances'].append(row_result);seen.add(row['audioSha256'])
  tmp=report_file.with_suffix('.tmp');tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');tmp.replace(report_file)
  print(row['id'],round(len(x)/16000,2),speech,'tail',row_result['tailAfterVadSeconds'],tail_peak,flush=True)
 if len(selected)==len(targets) and all(r['audioSha256'] in seen for r in selected): break
 time.sleep(3)
print('COMPLETE',len(targets),flush=True)
