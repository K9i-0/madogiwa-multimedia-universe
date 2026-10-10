from pathlib import Path
import json,subprocess,hashlib,math
import numpy as np
import soundfile as sf
p=Path(__file__).resolve().parent;ep=p.parent
rows=json.loads((ep/'dialogue.json').read_text());clips=json.loads((ep/'assets.json').read_text())['clips'];frame=24;placed=[]
overrides=json.loads((ep/'caption_overrides.json').read_text())
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

 if str(i) in overrides:caption=overrides[str(i)]
 moods={2:'normal',18:'smug',21:'sad',34:'surprise',36:'bored',38:'angry',40:'sad'}
 if i in moods:r['mood']=moods[i]
 r.update(caption=caption,startFrame=frame,durationInFrames=n,envelope=env,sha256=hashlib.sha256(src.read_bytes()).hexdigest())
 frame+=n+r['gapFrames']
 for c in clips:
  if c['afterLine']==i:
   c['startFrame']=frame;placed.append(c);frame+=c['durationInFrames']+c['postGapFrames']
m={'composition':{'width':1280,'height':720,'fps':30,'durationInFrames':frame+150},'dialogue':rows,'clips':placed,'mainStartFrame':next(r['startFrame'] for r in rows if r['scene']=='excel'),'endingStartFrame':next(r['startFrame'] for r in rows if r['scene']=='ending')}
(p/'src/edit-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));print('Duration',m['composition']['durationInFrames']/30)
