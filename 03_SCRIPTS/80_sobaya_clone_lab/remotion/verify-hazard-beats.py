"""Verify actual decoded final audio against the picture's musical event frames."""
from pathlib import Path
import json,subprocess
import numpy as np
from scipy.signal import butter,sosfilt
r=Path(__file__).resolve().parent;m=json.loads((r/'src/aura-hazard-synced.json').read_text());f=r.parent/m['output']
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-map','0:a:0','-ac','1','-ar','48000','-f','f32le','-'])
x=np.frombuffer(raw,dtype='<f4');x=sosfilt(butter(3,180,fs=48000,output='sos'),x);hop=240;e=np.sqrt(np.mean(x[:len(x)//hop*hop].reshape(-1,hop)**2,axis=1))
events=[]
for label,frame in [('glass_first_impact',725),('title_entrance',961)]:
 expected=frame/30;lo=round((expected-.045)*200);hi=round((expected+.045)*200)
 at=(lo+int(np.argmax(e[lo:hi+1])))/200;delta=at-expected
 assert abs(delta)<1/30,(label,delta)
 events.append({'event':label,'pictureFrame':frame,'decodedAudioLowBandPeakSeconds':at,'errorMs':round(delta*1000,3)})
q={'decodedFinalAudioCheck':'passed','events':events,'method':'180Hz low-pass; 5ms RMS; local peak within 45ms of scheduled event; max allowed difference one 30fps frame','subjectiveAudition':False}
(r.parent/'aura_phonk_prep_20261026/hazard-synced-audio-check.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print(json.dumps(q,ensure_ascii=False,indent=2))
