"""Reproduce v2 voice replacements and one-pass 720p export; run with Irodori venv Python."""
from pathlib import Path
import subprocess,json,hashlib,wave
import numpy as np
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
WORK=ROOT/'.local/doku-chikuwa-v2'; WORK.mkdir(exist_ok=True)
video=P/'wan3_result_v2_480p.mp4'
def pcm(path):
 return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-f','s16le','-ac','2','-ar','48000','-']),dtype='<i2').reshape(-1,2).copy()
a=pcm(video); b=a.copy(); reports=[]; touched=np.zeros(len(a),dtype=bool)
for filename,start,end in [('fukugyun_warning_v2.wav',19.85,22.55),('sobaya_doku_chikuwa_v2.wav',24.08,26.5)]:
 s,e=round(start*48000),round(end*48000);v=pcm(P/filename)
 assert len(v)<=e-s
 # Match speech energy using samples above a quiet floor; constant gain only.
 old=a[s:e].astype(float);new=v.astype(float)
 old_active=old[np.abs(old)>1500];new_active=new[np.abs(new)>1500]
 gain=float(np.sqrt(np.mean(old_active**2))/np.sqrt(np.mean(new_active**2)))
 gain=min(gain,30000/max(1,np.abs(new).max()))
 replacement=np.zeros((e-s,2),dtype='<i2');replacement[:len(v)]=np.rint(new*gain).astype('<i2')
 # 5ms fades occur only at the silent window edges, not across phonemes.
 n=240;replacement[:n]=np.rint(replacement[:n]*np.linspace(0,1,n)[:,None]).astype('<i2')
 b[s:e]=replacement;touched[s:e]=True
 reports.append(dict(file=filename,start=start,end=end,duration=len(v)/48000,gain=gain,sha256=hashlib.sha256((P/filename).read_bytes()).hexdigest()))
assert np.array_equal(a[~touched],b[~touched])
master=WORK/'master_v2.wav'
with wave.open(str(master),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(b.tobytes())
output=P/'preview_v2_720p.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-i',str(master),'-map','0:v:0','-map','1:a:0','-vf','scale=1280:720:flags=lanczos,setsar=1','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(output)],check=True)
(P/'audio_edit_v2.json').write_text(json.dumps(dict(input=video.name,output=output.name,patches=reports,unmodified_pcm_outside_windows=True,speech_time_stretch=False,model='Aratako/Irodori-TTS-v4-Large',text_cfg=5,duration_scale=1,uncut=True,sobaya=dict(reference='02_CHARACTERS/Sobaya_voice.wav',seed=42,caption='落ち着いて、自信たっぷりに短く言い切る。',postprocess='sobaya_monsterize.sh'),fukugyun=dict(reference='02_CHARACTERS/Fukuchan_voice.wav',seed=100,caption='短く鋭く制止する。',text='おい！ それはしょうこひんだ！'),listening_verified=False),ensure_ascii=False,indent=2)+'\n')
print(output)
