from pathlib import Path
import json,subprocess,wave,shutil
import numpy as np
P=Path(__file__).resolve().parent;pub=P/'remotion/public';S=P/'remotion/src'
def pcm(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar','48000','-ac','2','-f','s16le','-']),dtype='<i2').reshape(-1,2).astype(np.float64)/32768
old=json.loads((S/'edit-manifest-v10.json').read_text());shots=old['shots'][:4];at=597
segments=[('wan3_investigation_v12_480p.mp4',0,124),('wan3_investigation_v12_480p.mp4',174,177),('wan3_investigation_v12_480p.mp4',351,69),('wan3_entrance_inserts_v4_480p.mp4',340,20),('wan3_result_v2_marker_v12_480p.mp4',526,374),('wan3_aftermath_v12c_potfix_480p.mp4',0,180),('oden_marker1_v9.png',0,36)]
for file,start,dur in segments:
 shots.append(dict(kind='image' if file.endswith('.png') else 'video',file=file,sourceStart=start,duration=dur,**{'from':at}));at+=dur
 f=pub/file
 if f.is_symlink():f.unlink()
 if not f.exists():shutil.copy2(P/file,f)
m=dict(fps=30,width=1280,height=720,durationInFrames=at,shots=shots,audio='master_v12.wav',endcardFrames=36)
base=pcm(pub/'master_v10.wav');out=np.zeros((at*1600,2));out[:597*1600]=base[:597*1600]
cursor=597
for i,(file,start,dur) in enumerate(segments):
 if i in [0,1,2,5]: chunk=pcm(P/file)[start*1600:(start+dur)*1600]
 elif i==3: chunk=base[973*1600:993*1600]
 elif i==4:
  chunk=base[993*1600:1367*1600].copy()
  # Remove the previous reaction; retain the original fall sound underneath.
  raw=pcm(P/'wan3_result_v2_480p.mp4');chunk[347*1600:]=raw[873*1600:900*1600]
 else: chunk=np.zeros((dur*1600,2))
 out[cursor*1600:(cursor+dur)*1600]=chunk;cursor+=dur
# Existing score only, no previous dialogue.
bed=(pcm(pub/'master_v6.wav')-pcm(pub/'master_v5.wav'))[597*1600:888*1600]
out[597*1600:597*1600+len(bed)]+=bed
assert np.max(np.abs(out))<1
with wave.open(str(pub/'master_v12.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(np.round(out*32768).astype('<i2').tobytes())
(S/'edit-manifest-v12.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
f=S/'Root.tsx';s=f.read_text()
if "edit-manifest-v12" not in s:
 s=s.replace("export const Root", "import revised from './edit-manifest-v12.json';\nexport const Root");s=s.replace('</>;', '<Composition id="DokuChikuwaRevised" component={DokuChikuwa} defaultProps={{manifest:revised,drama:true,records:true,enhanced:true}} width={1280} height={720} fps={30} durationInFrames={revised.durationInFrames}/>\n</>;');f.write_text(s)
for name in ['investigation_v12','aftermath_v12','aftermath_v12b','aftermath_v12c','aftermath_v12d','rear_v12']:
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(P/f'wan3_{name}_480p.mp4'),'-vn','-c:a','pcm_s16le',str(P/f'wan3_{name}_generated_audio.wav')],check=True)
(P/'edit_v12_record.json').write_text(json.dumps(dict(duration_frames=at,generated_dialogue_audio_preserved=True,asr=False,tts_regeneration=False,time_stretch=False,marker_only_original_video=True,aftermath_first_take_rejected='repeated fall and unwanted end cut',aftermath_retry='v12b first-frame take rejected for unwanted foreign subtitles; v12c single shared image and Yotan voice reference with Japanese prompt',cost_estimate_usd=1.54),ensure_ascii=False,indent=2))
print('frames',at,'seconds',at/30)
