from pathlib import Path
import json,subprocess,wave,math,hashlib
import numpy as np
P=Path(__file__).resolve().parent;pub=P/'remotion/public'
def pcm(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar','48000','-ac','2','-f','s16le','-']),dtype='<i2').reshape(-1,2).copy()
m=json.loads((P/'remotion/src/edit-manifest-v6.json').read_text())
cut_start=958;cut_end=1080;removed=cut_end-cut_start
reaction=pcm(P/'reaction_v7.wav');start=1447-removed
endcard=1492-removed
extra=max(0,start+math.ceil(len(reaction)/1600)+9-endcard)
for s in m['shots']:
 if s['from']==cut_start:
  s['sourceStart']+=removed;s['duration']-=removed
 elif s['from']>=cut_end:s['from']-=removed
 if s['file']=='ending_hold.png':s['duration']+=extra
 elif s['from']==endcard:s['from']+=extra
m['durationInFrames']+=extra-removed;m['audio']='master_v7.wav'
a=pcm(pub/'master_v6.wav');a[1447*1600:1492*1600]=0
a=np.concatenate([a[:cut_start*1600],a[cut_end*1600:]])
a=np.concatenate([a[:endcard*1600],np.zeros((extra*1600,2),dtype='<i2'),a[endcard*1600:]])
a[start*1600:start*1600+len(reaction)]=reaction
assert len(a)==m['durationInFrames']*1600
with wave.open(str(pub/m['audio']),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(a.tobytes())
(P/'remotion/src/edit-manifest-v7.json').write_text(json.dumps(m,indent=2)+'\n')
r=dict(text='誰この人。こわ…',reference='yotan_reference_v3.wav',model='Aratako/Irodori-TTS-v4-Large',seed=100,caption='',cfg=3,uncut=True,asr=False,time_stretch=False,cut_v6_frames=[958,1080],extra_hold_frames=extra,reaction_start_frame=start,reaction_seconds=len(reaction)/48000,durationInFrames=m['durationInFrames'],sha256=hashlib.sha256((P/'reaction_v7.wav').read_bytes()).hexdigest())
(P/'edit_v7_record.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(r)
