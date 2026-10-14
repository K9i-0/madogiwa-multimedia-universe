from pathlib import Path
import subprocess,json,wave,hashlib
import numpy as np
P=Path(__file__).resolve().parent;W=P.parents[1]/'.local/doku-chikuwa-v3';W.mkdir(exist_ok=True)
def pcm(path):
 return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-f','s16le','-ac','2','-ar','48000','-']),dtype='<i2').reshape(-1,2).copy()
a=pcm(P/'wan3_result_v2_480p.mp4');b=a.copy();mask=np.zeros(len(a),bool);rows=[]
# Fixed voice gain per speaker, not per scene. Pauses alone may be shortened.
items=[('fuku_intro_v3.wav',0.45,3.85,1.05,[]),('yotan_deduction_v3.wav',6.27,10.4,1.0,[]),('fuku_abbreviation_kana_v3.wav',10.67,15.1,1.05,[(1.6,1.9),(3.1,3.25)]),('yotan_question_v3.wav',15.2,17.45,1.0,[]),('fuku_warning_kana_v3.wav',19.85,22.55,1.05,[]),('sobaya_doku_chikuwa_v2.wav',24.08,26.5,1.2613616324107835,[])]
for filename,start,end,gain,cuts in items:
 v=pcm(P/filename)
 for lo,hi in reversed(cuts):v=np.concatenate([v[:round(lo*48000)],v[round(hi*48000):]])
 s,e=round(start*48000),round(end*48000);assert len(v)<=e-s,(filename,len(v)/48000,end-start)
 q=np.rint(v.astype(float)*gain);assert np.abs(q).max()<32767
 replacement=np.zeros((e-s,2),dtype='<i2');replacement[:len(v)]=q.astype('<i2');b[s:e]=replacement;mask[s:e]=True
 rows.append(dict(file=filename,start=start,end=end,gain=gain,silence_cuts=cuts,speech_speed_changed=False,sha256=hashlib.sha256((P/filename).read_bytes()).hexdigest()))
assert np.array_equal(a[~mask],b[~mask])
# Preserve the prior adopted Sobaya PCM exactly.
old=pcm(P.parents[1]/'.local/doku-chikuwa-v2/master_v2.wav');b[round(24.08*48000):round(26.5*48000)]=old[round(24.08*48000):round(26.5*48000)];assert np.array_equal(b[round(24.08*48000):round(26.5*48000)],old[round(24.08*48000):round(26.5*48000)])
master=W/'master_v3.wav'
with wave.open(str(master),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(48000);f.writeframes(b.tobytes())
output=P/'preview_v3_720p.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(P/'preview_v2_720p.mp4'),'-i',str(master),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(output)],check=True)
(P/'audio_edit_v3.json').write_text(json.dumps(dict(output=output.name,patches=rows,video_stream_copy=True,outside_patches_pcm_identical=True,sobaya_pcm_identical=True,reference_source='generated_video',listening_verified=False,phoneme_sync_verified=False),ensure_ascii=False,indent=2)+'\n')
print(output)
