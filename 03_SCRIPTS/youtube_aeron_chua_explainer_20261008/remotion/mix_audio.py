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
def fade(a,head,tail):
 a[:head]*=np.linspace(0,1,head)[:,None];a[-tail:]*=np.linspace(1,0,tail)[:,None];return a
voice=np.zeros((n,2),np.float32)
for d in m['dialogue']:
 a=decode(P/'public'/d['audio']);start=d['startFrame']*1600;voice[start:start+len(a)]+=a
save(P/'out/voice_unmixed.wav',voice);voice=decode(P/'out/voice_unmixed.wav','loudnorm=I=-18:TP=-2:LRA=11')[:n]
if len(voice)<n:voice=np.pad(voice,((0,n-len(voice)),(0,0)))
bgm=np.zeros((n,2),np.float32);cut=m['mainStartFrame']*1600
intro=decode(P/'public/intro.mp3','loudnorm=I=-34:TP=-3:LRA=11');bgm[:cut]=fade(intro[:cut],sr//2,int(.8*sr))
main=decode(P/'public/main.wav','loudnorm=I=-34:TP=-3:LRA=11');loop=main.copy();cross=sr
while len(loop)<n-cut:
 overlap=loop[-cross:] * np.linspace(1,0,cross)[:,None]+main[:cross]*np.linspace(0,1,cross)[:,None]
 loop=np.concatenate([loop[:-cross],overlap,main[cross:]])
bgm[cut:]=fade(loop[:n-cut],int(.6*sr),sr)
for c in m['clips']:
 start=c['startFrame']*1600;length=c['durationInFrames']*1600;source=c['sourceStartFrame']*1600
 a=decode(P/'public'/c['src'])[source:source+length];save(P/'out/clip_temp.wav',a)
 a=decode(P/'out/clip_temp.wav','loudnorm=I=-19:TP=-2:LRA=11')[:length];a=fade(a,240,480)
 voice[start:start+len(a)]+=a;bgm[start:start+length]*=.08
 fadeN=sr//5
 bgm[max(0,start-fadeN):start]*=np.linspace(1,.08,min(fadeN,start))[:,None]
 bgm[start+length:start+length+fadeN]*=np.linspace(.08,1,min(fadeN,n-start-length))[:,None]
# End on Unity: crossfade from the main BGM, then lift after dialogue.
end=m['endingStartFrame']*1600;cross=sr
bgm[end:end+cross]*=np.linspace(1,0,cross)[:,None];bgm[end+cross:]=0
unity=decode(P/'public/unity.mp3','loudnorm=I=-30:TP=-3:LRA=11')[:n-end]
unity=fade(unity,sr,int(1.5*sr));lift=m['creditsStartFrame']*1600-end
if lift<len(unity):
 ramp=min(sr,len(unity)-lift);unity[lift:lift+ramp]*=np.linspace(1,2.5,ramp)[:,None];unity[lift+ramp:]*=2.5
bgm[end:]+=unity
a=voice+bgm;peak=float(np.max(np.abs(a)))
if peak>.95:a*=.95/peak
save(P/'public/mixed.wav',a)
(P.parent/'mix_record.json').write_text(json.dumps({'sampleRate':sr,'frames':m['composition']['durationInFrames'],'voiceTargetLUFS':-18,'bgmTargetLUFS':-34,'clipTargetLUFS':-19,'premasterPeak':peak,'clips':m['clips'],'endingStartFrame':m['endingStartFrame'],'endingTrack':'TheFatRat - Unity','endingTargetLUFS':-30},ensure_ascii=False,indent=2))
print('Mixed',n/sr,'seconds; peak',peak)
