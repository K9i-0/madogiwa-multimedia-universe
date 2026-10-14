from pathlib import Path
import json,wave,subprocess
import numpy as np
P=Path(__file__).resolve().parent;pub=P/'remotion/public'
def pcm(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar','48000','-ac','2','-f','s16le','-']),dtype='<i2').reshape(-1,2).copy()
m=json.loads((P/'remotion/src/edit-manifest-v9.json').read_text())
insert_frame=794;pause_frames=15
base=pcm(pub/'master_v7.wav');voice=pcm(P/'abbreviation_v5.wav');at=insert_frame*1600;n=pause_frames*1600;v=42*1600
# The phrase boundary is the low-energy valley at 1.40 seconds of the adopted line.
# Keep the quiet music under the pause by isolating the existing accompaniment.
bed=base[at:at+n].astype(np.int32)-voice[v:v+n].astype(np.int32)
ramp=np.ones(n);fade=240;ramp[:fade]=np.linspace(0,1,fade);ramp[-fade:]=np.linspace(1,0,fade)
bed=np.round(bed*ramp[:,None]).astype('<i2')
out=np.concatenate([base[:at],bed,base[at:]])
assert np.array_equal(out[:at],base[:at]) and np.array_equal(out[at+n:],base[at:])
for s in m['shots']:
 if s['from']<=insert_frame<s['from']+s['duration']:s['duration']+=pause_frames
 elif s['from']>insert_frame:s['from']+=pause_frames
m['durationInFrames']+=pause_frames;m['audio']='master_v10.wav'
with wave.open(str(pub/m['audio']),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(out.tobytes())
(P/'remotion/src/edit-manifest-v10.json').write_text(json.dumps(m,indent=2)+'\n')
(P/'edit_v10_record.json').write_text(json.dumps(dict(insertFrame=insert_frame,pauseFrames=pause_frames,fps=30,lineBoundarySeconds=1.4,sourceAudio='master_v7.wav',preservedOutsideInsertion=True,tts=False,asr=False,timeStretch=False),indent=2)+'\n')
