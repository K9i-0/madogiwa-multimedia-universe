from pathlib import Path
import json,subprocess,hashlib
import numpy as np
import soundfile as sf
p=Path(__file__).resolve().parent; ep=p.parent
rows=json.loads((ep/'dialogue.json').read_text());frame=30
for r in rows:
 src=ep/r['audio'];dst=p/'public'/r['audio']
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),'-af','loudnorm=I=-18:TP=-2:LRA=7','-ar','48000',str(dst)],check=True)
 x,sr=sf.read(dst);x=x.mean(axis=1) if x.ndim>1 else x
 n=int(np.ceil(len(x)/sr*30));env=[]
 for f in range(n):
  a=x[round(f*sr/30):round((f+1)*sr/30)];env.append(round(float(np.sqrt(np.mean(a*a))) if len(a) else 0,5))
 r.update(startFrame=frame,durationInFrames=n,envelope=env,sha256=hashlib.sha256(src.read_bytes()).hexdigest(),seconds=len(x)/sr)
 frame+=n+15
manifest={'composition':{'width':1280,'height':720,'fps':30,'durationInFrames':frame+45},'dialogue':rows}
(p/'src/edit-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('duration', (frame+45)/30)
