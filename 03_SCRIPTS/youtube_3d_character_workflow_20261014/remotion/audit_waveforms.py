from pathlib import Path
import json
import numpy as np,soundfile as sf
P=Path(__file__).resolve().parent
rows=json.loads((P/'out/voice_progress.json').read_text());out=[]
for d in rows:
 x,sr=sf.read(P/'public'/d['audio']);block=max(1,round(sr*.02));rms=np.array([np.sqrt(np.mean(x[i:i+block]**2)) for i in range(0,len(x),block)]);active=np.where(rms>max(.003,float(rms.max())*.035))[0]
 r={'id':d['id'],'seconds':len(x)/sr,'headQuietSeconds':float(active[0]*.02) if len(active) else len(x)/sr,'tailQuietSeconds':float((len(rms)-1-active[-1])*.02) if len(active) else len(x)/sr,'peak':float(np.abs(x).max()),'finite':bool(np.isfinite(x).all())};out.append(r)
(P/'out/waveform_audit.json').write_text(json.dumps(out,indent=2));print('checked',len(out));print(json.dumps([r for r in out if r['headQuietSeconds']>1 or r['tailQuietSeconds']>1.2 or not r['finite']],indent=2))
