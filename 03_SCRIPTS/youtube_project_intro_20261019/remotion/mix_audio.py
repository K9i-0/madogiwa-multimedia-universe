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
def loop_to(a,length,cross=0):
 loop=a.copy()
 while len(loop)<length:
  if cross:
   overlap=loop[-cross:]*np.linspace(1,0,cross)[:,None]+a[:cross]*np.linspace(0,1,cross)[:,None]
   loop=np.concatenate([loop[:-cross],overlap,a[cross:]])
  else:loop=np.concatenate([loop,a])
 return loop[:length]
cut=m['mainStartFrame']*1600;ending=m['endingStartFrame']*1600;cross=2*sr
bgm=np.zeros((n,2),np.float32)
intro=decode(P/'public/intro.mp3','loudnorm=I=-34:TP=-3:LRA=11')
bgm[:cut+cross]=loop_to(intro,cut+cross,sr);bgm[cut:cut+cross]*=np.linspace(1,0,cross)[:,None]
main=loop_to(decode(P/'public/main.wav','loudnorm=I=-34:TP=-3:LRA=11'),ending+cross-cut,sr)
main[:cross]*=np.linspace(0,1,cross)[:,None];main[-cross:]*=np.linspace(1,0,cross)[:,None]
bgm[cut:ending+cross]+=main
ending_music=loop_to(decode(P/'public/unity.mp3','loudnorm=I=-38:TP=-3:LRA=11'),n-ending,sr)
ending_music[:cross]*=np.linspace(0,1,cross)[:,None];ending_music[-4*sr:]*=np.linspace(1,0,4*sr)[:,None];bgm[ending:]+=ending_music
source=decode(P/'public/commute.mp4')
montage=np.concatenate([source[a*sr:b*sr] for a,b in [(0,5),(12,16),(21,26)]])
save(P/'out/intro_source.wav',montage)
source=loop_to(decode(P/'out/intro_source.wav','loudnorm=I=-38:TP=-6:LRA=11'),cut)
source[-sr:]*=np.linspace(1,0,sr)[:,None];bgm[:cut]+=source
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
(P.parent/'mix_record.json').write_text(json.dumps(dict(sampleRate=sr,frames=m['composition']['durationInFrames'],voiceTargetLUFS=-18,bgmTargetLUFS=-34,clipTargetLUFS=-19,premasterPeak=peak,introOriginalAudio=True,introBgm=True,introSourceTargetLUFS=-38,introSourceCutsSeconds=[[0,5],[12,16],[21,26]],introMusic='昼下がり気分／KK',endingMusic='TheFatRat - Unity',endingTargetLUFS=-38,endingStartFrame=m['endingStartFrame'],crossfadeSeconds=2,music='ほのぼのワルツ【リコーダー】／エクシエ',endingLiftAfterDialogue=False),ensure_ascii=False,indent=2))
print('Mixed',n/sr,'seconds; peak',peak)
