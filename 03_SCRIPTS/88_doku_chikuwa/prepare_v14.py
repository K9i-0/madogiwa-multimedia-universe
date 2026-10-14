from pathlib import Path
import subprocess,json,wave,shutil,hashlib
import numpy as np
P=Path(__file__).resolve().parent;PUB=P/'remotion/public';S=P/'remotion/src';W=P.parents[1]/'.local/doku-chikuwa-v14'
def pcm(f):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-ar','48000','-ac','2','-f','s16le','-']),dtype='<i2').reshape(-1,2).astype(np.int32)
base=pcm(PUB/'master_v13.wav');old=pcm(P/'warning_v13.wav');new=pcm(W/'warning.wav');out=base.copy();at=1056*1600
assert at+len(new)<987*1600+round((24.08-526/30)*48000),'Overlap with Sobaya'
out[at:at+len(old)]-=old;out[at:at+len(new)]+=new
end=at+max(len(old),len(new));assert np.array_equal(base[:at],out[:at]) and np.array_equal(base[end:],out[end:]);assert abs(out).max()<32768
with wave.open(str(PUB/'master_v14.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(out.astype('<i2').tobytes())
shutil.copy2(W/'warning.wav',P/'warning_v14.wav')
m=json.loads((S/'edit-manifest-v13.json').read_text());m['audio']='master_v14.wav';(S/'edit-manifest-v14.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
f=S/'Root.tsx';s=f.read_text()
if 'edit-manifest-v14' not in s:
 s=s.replace('export const Root',"import warningUpdated from './edit-manifest-v14.json';\nexport const Root")
 s=s.replace('</>;', '<Composition id="DokuChikuwaWarningUpdated" component={DokuChikuwa} defaultProps={{manifest:warningUpdated,drama:true,records:true,enhanced:true}} width={1280} height={720} fps={30} durationInFrames={warningUpdated.durationInFrames}/>\n</>;');f.write_text(s)
r=dict(text='おい！それは証拠品だギュン！',model='Aratako/Irodori-TTS-v4-Large',reference='warning_v5.wav',reference_sha256=hashlib.sha256((P/'warning_v5.wav').read_bytes()).hexdigest(),seed=100,caption='',cfg_text=3,duration_scale=1,uncut=True,tts_attempts=1,asr=False,time_stretch=False,start_frame=1056,duration_seconds=len(new)/48000,outside_patch_pcm_equal=True,video='stream-copy v13',output='final_remotion_doku_chikuwa_v14.mp4')
(P/'edit_v14_record.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
subprocess.run(['ffmpeg','-y','-v','error','-i',str(P/'final_remotion_doku_chikuwa_v13.mp4'),'-i',str(PUB/'master_v14.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(P/r['output'])],check=True)
print(json.dumps(r,ensure_ascii=False))
