from pathlib import Path
import json,subprocess,wave,argparse
import numpy as np
P=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--manifest',default='src/edit-manifest-v2.json');parser.add_argument('--output',default='public/mixed-v2.wav');parser.add_argument('--record',default='../mix_record_v2.json');args=parser.parse_args()
m=json.loads((P/args.manifest).read_text());sr=48000
assert m['composition']['fps']==30
n=m['composition']['durationInFrames']*1600
(P/'out').mkdir(exist_ok=True)

def decode(path,filters=None):
 cmd=['ffmpeg','-v','error','-i',str(path)]
 if filters:cmd+=['-af',filters]
 return np.frombuffer(subprocess.check_output(cmd+['-f','f32le','-ar',str(sr),'-ac','2','pipe:1']),dtype='<f4').reshape(-1,2).copy()
def save(path,a):
 with wave.open(str(path),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(a,-1,1)*32767).astype('<i2').tobytes())
def fade(a,head,tail):
 head=min(head,len(a));tail=min(tail,len(a))
 if head:a[:head]*=np.linspace(0,1,head)[:,None]
 if tail:a[-tail:]*=np.linspace(1,0,tail)[:,None]
 return a
voice=np.zeros((n,2),np.float32)
for d in m['dialogue']:
 a=decode(P/'public'/d['audio'],'loudnorm=I=-18:TP=-2:LRA=11' if m.get('voiceModel') else None);start=d['startFrame']*1600;voice[start:start+len(a)]+=fade(a,144,144)
save(P/'out/voice_unmixed_v2.wav',voice);voice=decode(P/'out/voice_unmixed_v2.wav','loudnorm=I=-18:TP=-2:LRA=11')[:n]
if len(voice)<n:voice=np.pad(voice,((0,n-len(voice)),(0,0)))
bgm=np.zeros((n,2),np.float32);cut=m['mainStartFrame']*1600
intro=decode(P/'public/intro.mp3','loudnorm=I=-34:TP=-3:LRA=11');bgm[:cut]=fade(intro[:cut],sr//2,int(.8*sr))
main=decode(P/'public/main.wav','loudnorm=I=-34:TP=-3:LRA=11');loop=main.copy();cross=sr
while len(loop)<n-cut:
 overlap=loop[-cross:] * np.linspace(1,0,cross)[:,None]+main[:cross]*np.linspace(0,1,cross)[:,None]
 loop=np.concatenate([loop[:-cross],overlap,main[cross:]])
bgm[cut:]=fade(loop[:n-cut],int(.6*sr),sr)
clip_duck_records=[]
for clip_index,c in enumerate(m['clips']):
 start=c['startFrame']*1600;length=c['durationInFrames']*1600;source=c['sourceStartFrame']*1600
 for d in m['dialogue']:
  assert c['startFrame']+c['durationInFrames']<=d['startFrame'] or c['startFrame']>=d['startFrame']+d['durationInFrames'], ('clip/host overlap',c.get('id'),d.get('id'))
 a=decode(P/'public'/c['src'])[source:source+length]
 assert len(a)>=length-sr//30,('clip audio shorter than excerpt',c.get('id'),len(a),length)
 if len(a)<length:a=np.pad(a,((0,length-len(a)),(0,0)))
 save(P/'out/clip_temp.wav',a)
 a=decode(P/'out/clip_temp.wav','loudnorm=I=-19:TP=-2:LRA=11')[:length];a=fade(a,240,480)
 duck=0 if c.get('muteBgm') or c.get('layout')=='comparison' else .08
 voice[start:start+len(a)]+=fade(a,144,144);bgm[start:start+length]*=duck
 fadeN=sr//5
 bgm[max(0,start-fadeN):start]*=np.linspace(1,duck,min(fadeN,start))[:,None]
 bgm[start+length:start+length+fadeN]*=np.linspace(duck,1,min(fadeN,n-start-length))[:,None]
 clip_duck_records.append({'id':c.get('id',clip_index),'startFrame':c['startFrame'],'durationInFrames':c['durationInFrames'],'bgmGain':duck})
# Unity is a quiet ending cue; keep its level low even after dialogue.
end=m['endingStartFrame']*1600;cross=2*sr
if end<n:
 bgm[end:end+cross]*=np.linspace(1,0,cross)[:,None];bgm[end+cross:]=0
 unity=decode(P/'public/unity.mp3','loudnorm=I=-38:TP=-3:LRA=11')[:n-end]
 unity=fade(unity,2*sr,4*sr)
 bgm[end:]+=unity
a=voice+bgm;peak=float(np.max(np.abs(a)))
if peak>.95:a*=.95/peak
save(P/args.output,a)
(P/args.record).write_text(json.dumps({'sampleRate':sr,'frames':m['composition']['durationInFrames'],'voiceTargetLUFS':-18,'perUtteranceNormalization':bool(m.get('voiceModel')),'bgmTargetLUFS':-34,'clipTargetLUFS':-19,'premasterPeak':peak,'clips':m['clips'],'clipDucking':clip_duck_records,'endingStartFrame':m['endingStartFrame'],'endingTrack':'TheFatRat - Unity','endingTargetLUFS':-38,'endingLiftAfterDialogue':False,'endingCrossfadeSeconds':2,'endingFadeOutSeconds':4},ensure_ascii=False,indent=2))
print('Mixed',n/sr,'seconds; peak',peak)
