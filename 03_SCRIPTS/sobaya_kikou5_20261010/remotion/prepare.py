from pathlib import Path
import json,subprocess,hashlib,math
import numpy as np
import soundfile as sf
p=Path(__file__).resolve().parent;ep=p.parent
rows=json.loads((ep/'dialogue.json').read_text());clips=json.loads((ep/'assets.json').read_text())['clips'];frame=24;placed=[]
for i,r in enumerate(rows,1):
 src=ep/r['audio'];dst=p/'public'/r['audio']
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),'-af','loudnorm=I=-18:TP=-2:LRA=7','-ar','48000',str(dst)],check=True)
 x,sr=sf.read(dst);x=x.mean(axis=1) if x.ndim>1 else x;n=math.ceil(len(x)/sr*30)
 env=[round(float(np.sqrt(np.mean(x[f*1600:(f+1)*1600]**2))),5) for f in range(n)]
 text=r['text'];caption=text
 if len(text)>29:
  splits=[j+1 for j,c in enumerate(text) if c in '、。！？' and 8<j<len(text)-7]
  k=min(splits,key=lambda j:abs(j-len(text)/2)) if splits else len(text)//2
  caption=text[:k]+'\n'+text[k:]
 if i==9:caption='お店では、やめさんを捕まえると\nビールが永久無料になるキャンペーンも実施。'
 r.update(caption=caption,startFrame=frame,durationInFrames=n,envelope=env,sha256=hashlib.sha256(src.read_bytes()).hexdigest())
 frame+=n+(18 if i in [4,8,14,18,22,30] else 10)
 for c in clips:
  if c['afterLine']==i:
   c['startFrame']=frame;placed.append(c);frame+=c['durationInFrames']+12
m={'composition':{'width':1280,'height':720,'fps':30,'durationInFrames':frame+150},'dialogue':rows,'clips':placed,'mainStartFrame':rows[4]['startFrame'],'endingStartFrame':rows[30]['startFrame']}
(p/'src/edit-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));print('Duration',m['composition']['durationInFrames']/30)
