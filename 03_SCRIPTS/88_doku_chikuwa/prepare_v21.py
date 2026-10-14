from pathlib import Path
import json,subprocess,wave,shutil,hashlib
import numpy as np
P=Path(__file__).resolve().parent;PUB=P/'remotion/public';S=P/'remotion/src';SR=48000;SPF=1600

def pcm(f):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-ar',str(SR),'-ac','2','-f','s16le','-']),dtype='<i2').reshape(-1,2).astype(np.int32)
r=json.loads((P/'voice_report_v20.json').read_text());source=Path(r['file']);assert hashlib.sha256(source.read_bytes()).hexdigest()==r['sha256']
shutil.copy2(source,P/'report_adopted43_v21.wav');new=pcm(source);old=pcm(P/'report_v5.wav');base=pcm(PUB/'master_v17.wav');clean=base.copy();start=3*SPF
clean[start:start+len(old)]-=old
# Extend the oden evidence hold by15frames. Shift later shots/sounds together, preserve speech speeds.
insert=228*SPF;extra=15*SPF;out=np.concatenate([clean[:insert],np.zeros((extra,2),np.int32),clean[insert:]])
out[start:start+len(new)]+=new
assert np.array_equal(out[start:start+len(new)],new)
next_start=(237+15)*SPF;gap=(next_start-start-len(new))/SR;assert gap>=.2
assert np.array_equal(out[next_start:],base[237*SPF:]);assert out.min()>=-32768 and out.max()<=32767
with wave.open(str(PUB/'master_v21.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(out.astype('<i2').tobytes())
m=json.loads((S/'edit-manifest-v18.json').read_text());m['shots'][1]['duration']+=15
for shot in m['shots'][2:]:shot['from']+=15
m['durationInFrames']+=15;m['audio']='master_v21.wav';assert len(out)==m['durationInFrames']*SPF
(S/'edit-manifest-v21.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
f=S/'Root.tsx';s=f.read_text()
if 'edit-manifest-v21' not in s:
 s=s.replace('export const Root',"import finished from './edit-manifest-v21.json';\nexport const Root")
 s=s.replace('</>;', '<Composition id="DokuChikuwaFinished" component={DokuChikuwa} defaultProps={{manifest:finished,drama:true,records:true,enhanced:true}} width={1280} height={720} fps={30} durationInFrames={finished.durationInFrames}/>\n</>;');f.write_text(s)
r.update(status='adopted',adopted_file='report_adopted43_v21.wav',video_modified=True,adopted_output='final_remotion_doku_chikuwa_v21.mp4');(P/'voice_report_v20.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
record=dict(output=r['adopted_output'],duration_frames=m['durationInFrames'],fps=30,resolution=[1280,720],adopted_report='report_adopted43_v21.wav',adopted_sha256=r['sha256'],report_start_frame=3,report_duration_seconds=len(new)/SR,next_line_frame=252,gap_seconds=gap,hold_extended_frames=15,shift_start_frame=228,report_pcm_exact=True,subsequent_pcm_equal_after_shift=True,time_stretch=False,tts_regenerated=False,music=False,warning='warning_adopted_A_v17.wav',mosaic=True)
(P/'edit_v21_record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(record)
