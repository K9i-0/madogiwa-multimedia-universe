from pathlib import Path
import json,subprocess,wave,math,shutil,hashlib
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[1];W=ROOT/'.local/doku-chikuwa-v5';PUB=P/'remotion/public'
def pcm(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar','48000','-ac','2','-f','s16le','-']),dtype='<i2').reshape(-1,2).copy()
lines=['report','message','deduction','abbreviation','question','warning','reaction'];clips={}
for n in lines:
 dst=P/(n+'_v5.wav')
 if not dst.exists():shutil.copy2(W/(n+'.wav'),dst)
 clips[n]=pcm(dst)
original=pcm(PUB/'master_v4.wav');intro_frames=max(342,237+math.ceil(len(clips['message'])/1600)+6);delta=intro_frames-342
m=json.loads((P/'remotion/src/edit-manifest.json').read_text())
for s in m['shots']:
 if s['from']==228:s['duration']+=delta
 elif s['from']>=342:s['from']+=delta
m['durationInFrames']+=delta;m['audio']='master_v5.wav'
master=np.zeros((m['durationInFrames']*1600,2),dtype='<i2');master[intro_frames*1600:]=original[342*1600:m['durationInFrames']*1600-delta*1600]
entries=[('report',3,0,intro_frames),('message',237,None,None),('deduction',583+delta,578+delta,709+delta),('abbreviation',715+delta,709+delta,848+delta),('question',851+delta,848+delta,921+delta),('warning',1132+delta,1130+delta,1238+delta),('reaction',1410+delta,1410+delta,1455+delta)]
records=[];changed=np.zeros(len(master),dtype=bool)
for n,start,lo,hi in entries:
 if lo is not None:master[lo*1600:hi*1600]=0
 x=clips[n];s=start*1600;e=s+len(x)
 assert e<=len(master)
 if hi is not None:assert e<=hi*1600,(n,e/48000,hi/30)
 master[s:e]=x;changed[s:e]=True
 assert np.array_equal(master[s:e],x)
 records.append(dict(id=n,file=n+'_v5.wav',startFrame=start,durationSeconds=len(x)/48000,sha256=hashlib.sha256((P/(n+'_v5.wav')).read_bytes()).hexdigest(),pcm_exact=True))
# Verify the adopted Sobaya section is unchanged by the new mix and timeline shift.
old_s=1063*1600+round((24.08-526/30)*48000);old_e=1063*1600+round((26.5-526/30)*48000)
assert np.array_equal(original[old_s:old_e],master[old_s+delta*1600:old_e+delta*1600])
with wave.open(str(PUB/'master_v5.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(master.tobytes())
(P/'remotion/src/edit-manifest-v5.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
r=json.loads((W/'generation.json').read_text());r.update(output='final_remotion_doku_chikuwa_v5.mp4',patches=records,extra_intro_frames=delta,durationInFrames=m['durationInFrames'],fps=30,audio_time_stretch=False,silence_trimming=False,sobaya_pcm_unchanged=True,asr_used=False,pronunciation_review='user')
(P/'audio_edit_v5.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('Duration',m['durationInFrames']/30,'All new WAV samples preserved')
