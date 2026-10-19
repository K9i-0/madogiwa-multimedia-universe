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
 a=decode(P.parent/d['audio']);start=d['startFrame']*1600;voice[start:start+len(a)]+=a
save(P/'out/voice_unmixed.wav',voice);voice=decode(P/'out/voice_unmixed.wav','loudnorm=I=-18:TP=-2:LRA=11')[:n]
if len(voice)<n:voice=np.pad(voice,((0,n-len(voice)),(0,0)))
bgm=np.zeros((n,2),np.float32);cut=m['mainStartFrame']*1600
main=decode(P/'public/main.wav','loudnorm=I=-34:TP=-3:LRA=11');loop=main.copy();cross=sr
while len(loop)<n-cut:
 overlap=loop[-cross:]*np.linspace(1,0,cross)[:,None]+main[:cross]*np.linspace(0,1,cross)[:,None];loop=np.concatenate([loop[:-cross],overlap,main[cross:]])
bgm[cut:]=loop[:n-cut];bgm[cut:cut+sr]*=np.linspace(0,1,sr)[:,None];bgm[-4*sr:]*=np.linspace(1,0,4*sr)[:,None]
for c in m['clips']:
 if not c.get('audible'):continue
 start=c['startFrame']*1600;length=c['durationInFrames']*1600;source=c['sourceStartFrame']*1600
 a=decode(P/'public'/c['src'])[source:source+length];save(P/'out/clip_temp.wav',a)
 a=decode(P/'out/clip_temp.wav','loudnorm=I=-19:TP=-2:LRA=11')[:length];a[:240]*=np.linspace(0,1,240)[:,None];a[-480:]*=np.linspace(1,0,480)[:,None]
 voice[start:start+len(a)]+=a;bgm[start:start+length]=0
 bgm[max(0,start-9600):start]*=np.linspace(1,0,min(9600,start))[:,None];bgm[start+length:start+length+9600]*=np.linspace(0,1,min(9600,n-start-length))[:,None]
a=voice+bgm;peak=float(np.max(np.abs(a)))
if peak>.95:a*=.95/peak
save(P/'public/mixed.wav',a)
(P.parent/'mix_record.json').write_text(json.dumps(dict(sampleRate=sr,frames=m['composition']['durationInFrames'],voiceTargetLUFS=-18,bgmTargetLUFS=-34,clipTargetLUFS=-19,premasterPeak=peak,introOriginalAudio=False,introBgm=False,music='ほのぼのワルツ【リコーダー】／エクシエ',endingLiftAfterDialogue=False),ensure_ascii=False,indent=2))
print('Mixed',n/sr,'seconds; peak',peak)
