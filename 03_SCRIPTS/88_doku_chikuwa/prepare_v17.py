"""Adopt comparison A; subtract the existing post-added music, retain speech/foley."""
from pathlib import Path
import subprocess,json,wave,shutil,hashlib
import numpy as np
P=Path(__file__).resolve().parent;PUB=P/'remotion/public';S=P/'remotion/src';W=P.parents[1]/'.local/doku-chikuwa-voice-v16';SR=48000

def pcm(f):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-ar',str(SR),'-ac','2','-f','s16le','-']),dtype='<i2').reshape(-1,2).astype(np.int32)
base=pcm(PUB/'master_v15.wav');out=base.copy();old=pcm(P/'warning_v14.wav');new=pcm(W/'A_raw.wav');at=1056*1600
out[at:at+len(old)]-=old;out[at:at+len(new)]+=new
assert at+len(new)<987*1600+round((24.08-526/30)*SR)
# Reconstruct ONLY the score already added by prepare_v6.py, for subtraction.
# v12 copied this same continuous music through frame888. No new music is mixed in.
n=888*1600;t=np.arange(n)/SR;stop=888/30;music=np.zeros(n)
env=np.minimum(t/1.3,1)*np.clip((stop-t)/.09,0,1)
music+=(.009*np.sin(2*np.pi*55*t)+.004*np.sin(2*np.pi*82.4069*t)+.002*np.sin(2*np.pi*110.2*t))*env
for point,freq in [(0.5,220),(4.7,233.08),(9,164.81),(14,220),(19.8,164.81),(24.5,233.08),(27.5,220)]:
 u=t-point;v=np.maximum(u,0);e=(u>=0)*np.minimum(v/.008,1)*np.exp(-v/1.4)*np.clip((stop-t)/.09,0,1)
 music+=.012*e*(np.sin(2*np.pi*freq*v)+.3*np.sin(2*np.pi*freq*2.004*v)+.13*np.sin(2*np.pi*freq*3.01*v))
music_pcm=np.rint(music*32768).astype(np.int32);out[:n]-=music_pcm[:,None]
# The untouched initial narration now equals the pre-score source exactly.
pre=pcm(PUB/'master_v5.wav');assert np.array_equal(out[:13*SR],pre[:13*SR])
mask=np.zeros(len(out),bool);mask[:n]=True;mask[at:at+max(len(old),len(new))]=True
assert np.array_equal(out[~mask],base[~mask]);assert out.min()>=-32768 and out.max()<=32767
with wave.open(str(PUB/'master_v17.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(out.astype('<i2').tobytes())
shutil.copy2(W/'A_raw.wav',P/'warning_adopted_A_v17.wav')
m=json.loads((S/'edit-manifest-v15.json').read_text());m['audio']='master_v17.wav';(S/'edit-manifest-v17.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
f=S/'Root.tsx';s=f.read_text()
if 'edit-manifest-v17' not in s:
 s=s.replace('export const Root',"import noMusic from './edit-manifest-v17.json';\nexport const Root")
 s=s.replace('</>;', '<Composition id="DokuChikuwaNoMusic" component={DokuChikuwa} defaultProps={{manifest:noMusic,drama:true,records:true,enhanced:true}} width={1280} height={720} fps={30} durationInFrames={noMusic.durationInFrames}/>\n</>;');f.write_text(s)
r={'adopted':'A','text':'おい！それは証拠品だギュン！','source':'warning_adopted_A_v17.wav','source_sha256':hashlib.sha256((P/'warning_adopted_A_v17.wav').read_bytes()).hexdigest(),'model':'Aratako/Irodori-TTS-v4-Large','reference':'02_CHARACTERS/Fukuchan_voice.wav','seed':100,'caption':'','cfg_text':3,'duration_scale':1,'uncut':True,'voice_gain_db':0,'start_frame':1056,'duration_seconds':len(new)/SR,'music_removed_frames':[0,888],'foley_preserved':True,'narration_before_radio_pcm_equals_pre_bgm':True,'unchanged_outside_edits_pcm':True,'video_stream_copy':True,'time_stretch':False,'tts_regenerated':False,'output':'final_remotion_doku_chikuwa_v17.mp4'}
(P/'edit_v17_record.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
comparison=P/'voice_comparison_v16.json';record=json.loads(comparison.read_text());record.update(status='A_adopted',adopted='A',adopted_output=r['output']);comparison.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
subprocess.run(['ffmpeg','-y','-v','error','-i',str(P/'final_remotion_doku_chikuwa_v15.mp4'),'-i',str(PUB/'master_v17.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(P/r['output'])],check=True)
print(json.dumps(r,ensure_ascii=False,indent=2))
