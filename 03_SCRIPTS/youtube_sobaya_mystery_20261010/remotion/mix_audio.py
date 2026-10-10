from pathlib import Path
import json,subprocess,wave
import numpy as np
P=Path(__file__).resolve().parent;m=json.loads((P/'src/edit-manifest.json').read_text());sr=48000;n=m['composition']['durationInFrames']*1600

def decode(path,filters=None):
 cmd=['ffmpeg','-v','error','-i',str(path)]
 if filters:cmd+=['-af',filters]
 return np.frombuffer(subprocess.check_output(cmd+['-f','f32le','-ar',str(sr),'-ac','2','pipe:1']),dtype='<f4').reshape(-1,2).copy()
def save(path,a):
 with wave.open(str(path),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(a,-1,1)*32767).astype('<i2').tobytes())
voice=np.zeros((n,2),np.float32)
for d in m['dialogue']:
 a=decode(P/'public'/d['audio']);start=d['startFrame']*1600;voice[start:start+len(a)]+=a
save(P/'out/voice_unmixed.wav',voice);del voice
voice=decode(P/'out/voice_unmixed.wav','loudnorm=I=-18:TP=-2:LRA=11')[:n]
if len(voice)<n:voice=np.pad(voice,((0,n-len(voice)),(0,0)))
# Original deterministic, quiet minor-mode ambient composition; no samples or voices.
bgm=np.zeros((n,2),np.float32)
for start in range(0,n,sr*20):
 stop=min(n,start+sr*20);t=np.arange(start,stop,dtype=np.float64)/sr
 low=.15*np.sin(2*np.pi*73.416*t+.17*np.sin(t*.09))+.07*np.sin(2*np.pi*110*t)
 mid=.065*np.sin(2*np.pi*146.832*t)*(0.65+.35*np.sin(t*.13))
 high=np.zeros_like(t)
 notes=[293.665,349.228,440,329.628,293.665,220,261.626,220]
 for j in range(max(0,int(t[0]//12)-2),int(t[-1]//12)+1):
  dt=t-j*12;env=np.where(dt>=0,(1-np.exp(-np.maximum(dt,0)*1.6))*np.exp(-np.maximum(dt,0)/4),0)
  high+=.11*env*np.sin(2*np.pi*notes[j%len(notes)]*dt)
 a=low+mid+high;bgm[start:stop,0]=a;bgm[start:stop,1]=low+mid+high*.93
save(P/'out/ambient_raw.wav',bgm);del bgm
bgm=decode(P/'out/ambient_raw.wav','loudnorm=I=-35:TP=-6:LRA=8')[:n]
bgm[:sr*3]*=np.linspace(0,1,sr*3)[:,None]
ending=next(d['startFrame'] for d in m['dialogue'] if d['scene']=='ending')*1600
bgm[ending:]*=.7
bgm[-sr*5:]*=np.linspace(1,0,sr*5)[:,None]
a=voice+bgm;peak=float(np.max(np.abs(a)))
if peak>.95:a*=.95/peak
save(P/'public/mixed.wav',a)
(P.parent/'mix_record.json').write_text(json.dumps({'sampleRate':sr,'durationFrames':m['composition']['durationInFrames'],'voiceLUFS':-18,'musicLUFS':-35,'endingLift':False,'originalScore':True,'peak':peak,'clipAudio':'No original audio; archive video excerpts under narration','listeningAudit':'Not yet performed'},ensure_ascii=False,indent=2)+'\n')
print('Mixed',n/sr,'seconds; peak',peak)
