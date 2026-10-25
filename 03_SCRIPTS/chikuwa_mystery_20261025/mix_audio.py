from pathlib import Path
import json,subprocess,wave,numpy as np
P=Path(__file__).resolve().parent;D=P/'remotion';m=json.loads((D/'src/edit-manifest.json').read_text());sr=48000;n=m['composition']['durationInFrames']*1600

def decode(path,filters=None,start=None,duration=None):
 cmd=['ffmpeg','-v','error']
 if start is not None:cmd+=['-ss',str(start)]
 cmd+=['-i',str(path)]
 if duration is not None:cmd+=['-t',str(duration)]
 if filters:cmd+=['-af',filters]
 return np.frombuffer(subprocess.check_output(cmd+['-f','f32le','-ar',str(sr),'-ac','2','pipe:1']),dtype='<f4').reshape(-1,2).copy()
def save(path,a):
 with wave.open(str(path),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(a,-1,1)*32767).astype('<i2').tobytes())
def fade(a,head,tail):
 a[:head]*=np.linspace(0,1,head)[:,None];a[-tail:]*=np.linspace(1,0,tail)[:,None];return a
voice=np.zeros((n,2),np.float32)
for d in m['dialogue']:
 a=decode(P/d['audio']);start=d['startFrame']*1600;voice[start:start+len(a)]+=a
save(D/'out/voice_unmixed.wav',voice);del voice
voice=decode(D/'out/voice_unmixed.wav','loudnorm=I=-18:TP=-2:LRA=11')[:n]
if len(voice)<n:voice=np.pad(voice,((0,n-len(voice)),(0,0)))
bgm=np.zeros((n,2),np.float32);cut=m['mainStartFrame']*1600;end=m['endingStartFrame']*1600
intro=decode(D/'public/intro.mp3','loudnorm=I=-35:TP=-3:LRA=11');bgm[:cut]=fade(intro[:cut].copy(),sr,int(.8*sr))
main=decode(D/'public/main.mp3','loudnorm=I=-35:TP=-3:LRA=11');loop=main.copy();cross=sr
while len(loop)<end-cut+sr*2:
 overlap=loop[-cross:]*np.linspace(1,0,cross)[:,None]+main[:cross]*np.linspace(0,1,cross)[:,None];loop=np.concatenate([loop[:-cross],overlap,main[cross:]])
bgm[cut:end+sr*2]=fade(loop[:end-cut+sr*2],int(.6*sr),2*sr);del loop
# Return to the quiet opening theme for the ending, never lift after dialogue.
a=decode(D/'public/ending.mp3','loudnorm=I=-38:TP=-3:LRA=11')[:(m['codaStartFrame']-18)*1600-end].copy();bgm[end:end+len(a)]+=fade(a,sr*2,sr*4)
# Gradually lower the bed after Kitahara; withdraw music at the key inference.
horror=m['cues']['horrorStart']*1600
ramp=min(sr*5,end-horror)
bgm[horror:horror+ramp]*=np.linspace(1,.55,ramp)[:,None]
bgm[horror+ramp:end]*=.55
quiet0=m['cues']['silenceStart']*1600;quiet1=m['cues']['silenceEnd']*1600
ramp=sr//2
bgm[quiet0-ramp:quiet0]*=np.linspace(1,0,ramp)[:,None]
bgm[quiet0:quiet1]=0
bgm[quiet1:quiet1+sr*2]*=np.linspace(0,1,sr*2)[:,None]
# Coda: restrained original factory room tone, no musical sting or reused dialogue.
coda=m['codaStartFrame']*1600
seconds=np.arange(n-coda)/sr
hum=.0014*np.sin(2*np.pi*60*seconds)+.0005*np.sin(2*np.pi*120*seconds)
bed=np.stack([hum,hum],axis=1).astype(np.float32)
bgm[coda:]+=fade(bed,sr,2*sr)
for c in m['clips']:
 if c.get('muteSource'):continue
 start=c['startFrame']*1600;length=c['durationInFrames']*1600
 a=decode(D/'public'/c['src'],'loudnorm=I=-19:TP=-2:LRA=11',c['sourceStartFrame']/30,c['durationInFrames']/30)[:length]
 a=fade(a,240,480);voice[start:start+len(a)]+=a;bgm[start:start+length]*=.08
 fadeN=sr//5;bgm[start-fadeN:start]*=np.linspace(1,.08,fadeN)[:,None];bgm[start+length:start+length+fadeN]*=np.linspace(.08,1,fadeN)[:,None]
voice+=bgm;del bgm
peak=float(np.max(np.abs(voice)))
if peak>.94:voice*=.94/peak
save(D/'public/mixed.wav',voice)
(P/'mix_record.json').write_text(json.dumps({'sampleRate':sr,'durationSeconds':n/sr,'voiceLUFS':-18,'bgmLUFS':-35,'clipLUFS':-19,'premasterPeak':peak,'endingMusic':'TheFatRat - Unity / -38 LUFS','endingLift':False,'mainBgmStartFrame':m['mainStartFrame'],'mainFadeInFrames':18,'editorialCues':m['cues'],'codaSound':'original synthesized quiet factory hum, no dialogue','clips':m['clips']},ensure_ascii=False,indent=2))
print('Mixed',n/sr,'seconds; peak',peak)
