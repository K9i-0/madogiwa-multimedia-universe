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
 a=decode(P.parent/d['audio']);rate=d.get('audioSourceRate',24000);a=a[round(d.get('audioTrimStartSample',0)/rate*sr):round(d.get('audioTrimEndSample',len(a)*rate/sr)/rate*sr)];start=d['startFrame']*1600;voice[start:start+len(a)]+=a
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
# BGM stays local (prepare_assets.py). Without it, mix voice only and keep mix_record.json as the adopted record.
missing=[f for f in ['intro.mp3','main.wav','unity.mp3'] if not (P/'public'/f).exists()]
if missing:print('BGM missing, voice-only draft:',', '.join(missing))
if not missing:
 intro=decode(P/'public/intro.mp3','loudnorm=I=-34:TP=-3:LRA=11')
 intro_end=cut-int(.18*sr)
 bgm[:intro_end]=loop_to(intro,intro_end,sr);bgm[intro_end-sr:intro_end]*=np.linspace(1,0,sr)[:,None]
 main=loop_to(decode(P/'public/main.wav','loudnorm=I=-34:TP=-3:LRA=11'),ending+cross-cut,sr)
 main[:int(.35*sr)]*=np.linspace(0,1,int(.35*sr))[:,None];main[-cross:]*=np.linspace(1,0,cross)[:,None]
 bgm[cut:ending+cross]+=main
 ending_music=loop_to(decode(P/'public/unity.mp3','loudnorm=I=-38:TP=-3:LRA=11'),n-ending,sr)
 ending_music[:cross]*=np.linspace(0,1,cross)[:,None];ending_music[-4*sr:]*=np.linspace(1,0,4*sr)[:,None];bgm[ending:]+=ending_music
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
if not missing:(P.parent/'mix_record.json').write_text(json.dumps(dict(sampleRate=sr,frames=m['composition']['durationInFrames'],voiceTargetLUFS=-18,bgmTargetLUFS=-34,clipTargetLUFS=-19,premasterPeak=peak,introOriginalAudio=False,introBgm=True,introMusic='昼下がり気分／KK',endingMusic='TheFatRat - Unity',endingTargetLUFS=-38,endingStartFrame=m['endingStartFrame'],crossfadeSeconds=2,mainTransition="intro fade out 1s, gap 180ms, main fade in 350ms at greeting",music='ほのぼのワルツ【リコーダー】／エクシエ',endingLiftAfterDialogue=False),ensure_ascii=False,indent=2))
print('Mixed',n/sr,'seconds; peak',peak)
