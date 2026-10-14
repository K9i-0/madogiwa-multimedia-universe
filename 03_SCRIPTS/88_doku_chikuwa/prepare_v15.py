from pathlib import Path
import json,subprocess,wave,os
import numpy as np
P=Path(__file__).resolve().parent;PUB=P/'remotion/public';S=P/'remotion/src'
def pcm(f):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-ar','48000','-ac','2','-f','s16le','-']),dtype='<i2').reshape(-1,2).copy()
m=json.loads((S/'edit-manifest-v14.json').read_text());base=pcm(PUB/'master_v14.wav');name='wan3_aftermath_v15_480p.mp4';new=pcm(P/name)[:108*1600];start=1361;old_duration=87
out=np.concatenate([base[:start*1600],new,base[(start+old_duration)*1600:]])
assert np.array_equal(out[:start*1600],base[:start*1600])
assert np.array_equal(out[(start+108)*1600:],base[(start+old_duration)*1600:])
with wave.open(str(PUB/'master_v15.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(out.tobytes())
at=0
for shot in m['shots']:
 if shot['file']=='wan3_aftermath_v12c_potfix_480p.mp4':shot.update(file=name,sourceStart=0,duration=108)
 shot['from']=at;at+=shot['duration']
assert len(out)==at*1600;m.update(audio='master_v15.wav',durationInFrames=at)
(S/'edit-manifest-v15.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
if not (PUB/name).exists():os.link(P/name,PUB/name)
f=S/'Root.tsx';s=f.read_text()
if 'edit-manifest-v15' not in s:
 s=s.replace('export const Root',"import proneEnding from './edit-manifest-v15.json';\nexport const Root")
 s=s.replace('</>;', '<Composition id="DokuChikuwaProneEnding" component={DokuChikuwa} defaultProps={{manifest:proneEnding,drama:true,records:true,enhanced:true}} width={1280} height={720} fps={30} durationInFrames={proneEnding.durationInFrames}/>\n</>;');f.write_text(s)
r=dict(duration_frames=at,fps=30,warning='warning_v14.wav',aftermath_source=name,aftermath_source_frames=[0,108],aftermath_audio='generated synchronously with new action; reference reaction_trimmed_v13.wav',outside_aftermath_pcm_equal=True,time_stretch=False,asr='boundary locating only; not pronunciation grading',visual_audit='All three visible; rear-left Yotan, rear-right Fukugyun, foreground Sobaya prone, weak arm support then collapse; no extra captions, no purple food reappearing',cost_estimate_usd=.175)
(P/'edit_v15_record.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(r)
