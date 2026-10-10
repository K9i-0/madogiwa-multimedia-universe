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
# Licensed music, normalized before mixing; all positions derive from dialogue frames.
def fade(a,ins=0,outs=0):
 a=a.copy()
 if ins:a[:ins]*=np.linspace(0,1,ins)[:,None]
 if outs:a[-outs:]*=np.linspace(1,0,outs)[:,None]
 return a
body_frame=next(d['startFrame'] for d in m['dialogue'] if d['scene']!='intro')
end_frame=next(d['startFrame'] for d in m['dialogue'] if d['scene']=='ending')
reveal_frame=next(d['startFrame'] for d in m['dialogue'] if 'うちの社員です' in d['text'])
body=body_frame*1600;end=end_frame*1600;cross=2*sr
bgm=np.zeros((n,2),np.float32)
op=decode(P/'public/urban_legend.mp3','loudnorm=I=-34:TP=-6:LRA=8')[:body+cross]
bgm[:len(op)]+=fade(op,sr,cross)
track=decode(P/'public/truth_seeker.mp3','loudnorm=I=-34:TP=-6:LRA=8')
length=end+cross-body;bed=np.zeros((length,2),np.float32);step=len(track)-cross
for start in range(0,length,step):
 part=fade(track,cross if start else 0,cross)[:length-start]
 bed[start:start+len(part)]+=part
bgm[body:end+cross]+=fade(bed,cross,cross)
# A brief musical silence before and under the HR punchline, without changing dialogue.
cut=reveal_frame*1600;down=sr//2;hold=sr*2
bgm[cut-sr:cut-sr+down]*=np.linspace(1,0,down)[:,None]
bgm[cut-sr+down:cut+hold]=0
bgm[cut+hold:cut+hold+sr]*=np.linspace(0,1,sr)[:,None]
unity=decode(P/'public/unity.mp3','loudnorm=I=-38:TP=-3:LRA=11')[:n-end]
bgm[end:]+=fade(unity,cross,4*sr)
save(P/'out/music_v10.wav',bgm)
a=voice+bgm;peak=float(np.max(np.abs(a)))
if peak>.95:a*=.95/peak
save(P/'public/mixed.wav',a)
(P.parent/'mix_record.json').write_text(json.dumps({'revision':10,'sampleRate':sr,'durationFrames':m['composition']['durationInFrames'],'voiceLUFS':-18,'musicLUFS':-34,'endingLUFS':-38,'endingLift':False,'originalScore':False,'peak':peak,'bodyStartFrame':body_frame,'endingStartFrame':end_frame,'revealFrame':reveal_frame,'crossfadeSeconds':2,'endingFadeSeconds':4,'tracks':['都市伝説 / shimtone','Truth Seeker / 松浦洋介','Unity / TheFatRat'],'clipAudio':'No original audio; archive video excerpts under narration','listeningAudit':'Not performed'},ensure_ascii=False,indent=2)+'\n')
print('Mixed',n/sr,'seconds; peak',peak)
