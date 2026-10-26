"""Run with the repository audio venv; execute from this remotion directory."""
from pathlib import Path
import json,subprocess,hashlib
import numpy as np
import soundfile as sf
r=Path(__file__).resolve().parent
m=json.loads((r/'src/aura-manifest.json').read_text());o=r/'out/aura-prep';sr=48000;fps=30;n=m['composition']['durationInFrames']*sr//fps
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r.parent/m['audioSource']),'-ar',str(sr),'-ac','2',str(o/'original.wav')],check=True)
x,_=sf.read(o/'original.wav');music,_=sf.read(o/'revenge.wav');start=m['music']['startFrame']*sr//fps;music=music[start:start+n]
original=np.zeros((n,2))
for s in m['segments']:
 if 'sourceStart' not in s: continue
 seg=x[s['sourceStart']*sr//fps:s['sourceEnd']*sr//fps]
 if s['rate']!=1:
  sf.write(o/'segment-in.wav',seg,sr,subtype='FLOAT')
  subprocess.run(['ffmpeg','-v','error','-y','-i',str(o/'segment-in.wav'),'-af',f"atempo={s['rate']}",str(o/'segment-out.wav')],check=True)
  seg,_=sf.read(o/'segment-out.wav')
 size=s['duration']*sr//fps;seg=seg[:size]; fade=min(240,len(seg)//2);seg[:fade]*=np.linspace(0,1,fade)[:,None];seg[-fade:]*=np.linspace(1,0,fade)[:,None]
 at=s['from']*sr//fps;original[at:at+len(seg)]=seg
# Same music source timing in both versions; lower music around authored speech.
t=np.arange(n)/sr;duck=np.full(n,.52)
for c in m['captions']:
 a=c['startFrame']/fps-.13;b=c['endFrame']/fps+.15
 env=np.minimum(np.clip((t-a)/.12,0,1),np.clip((b-t)/.2,0,1))
 duck=np.minimum(duck,.52-env*.39)
fades=np.minimum(np.clip(t/.08,0,1),np.clip((n/sr-t)/.25,0,1))
for name,y in [('original_audio',original*.95+music*duck[:,None]),('bgm_only',music*.65)]:
 y*=fades[:,None];sf.write(o/f'{name}-pre.wav',y,sr,subtype='FLOAT')
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(o/f'{name}-pre.wav'),'-af','alimiter=limit=0.84:level=false:latency=true','-c:a','pcm_s24le',str(o/f'{name}.wav')],check=True)
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(o/'picture.mp4'),'-i',str(o/f'{name}.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(n/sr),'-movflags','+faststart',str(r.parent/f'final_remotion_aura_{name}_9x16.mp4')],check=True)
 print(name)
