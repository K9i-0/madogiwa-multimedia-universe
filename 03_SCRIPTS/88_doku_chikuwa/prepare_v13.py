"""v13: remove added marker, localized Irodori repairs, trim unwanted reaction words."""
from pathlib import Path
import json,subprocess,wave,shutil,hashlib
import numpy as np
P=Path(__file__).resolve().parent;W=P.parents[1]/'.local/doku-chikuwa-v13';PUB=P/'remotion/public';S=P/'remotion/src';SR=48000;SPF=1600

def pcm(p):
 return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar',str(SR),'-ac','2','-f','s16le','-']),dtype='<i2').reshape(-1,2).astype(np.int32)
def save(p,x):
 assert np.max(np.abs(x))<32768
 with wave.open(str(p),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(np.rint(x).astype('<i2').tobytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=pcm(PUB/'master_v12.wav');edited=base.copy();changed=np.zeros(len(base),bool)
# Repair only 可能性. Original: source frames87:105, full-output frames684:702.
# Sentence synthesized with the current Wan Yotan reference; no speed change.
full=pcm(W/'deduction_sentence.wav');part=full[round(2.70*SR):round(3.25*SR)].copy()
ref=pcm(P/'wan3_investigation_v12_480p.mp4');original=ref[87*SPF:105*SPF]
gain=float(np.sqrt(np.mean(original.astype(float)**2))/np.sqrt(np.mean(part.astype(float)**2)))
part=np.rint(part*gain).astype(np.int32)
patch=np.zeros((18*SPF,2),np.int32);patch[:len(part)]=part
# Low-energy edges only: 2ms fade to avoid discontinuity, no phoneme overlap/crossfade.
fade=96;patch[:fade]=np.rint(patch[:fade]*np.linspace(0,1,fade)[:,None]);patch[len(part)-fade:len(part)]=np.rint(patch[len(part)-fade:len(part)]*np.linspace(1,0,fade)[:,None])
lo=684*SPF;hi=702*SPF
# Keep the pre-existing score under the repair.
bed=base[lo:hi]-original
edited[lo:hi]=patch+bed;changed[lo:hi]=True
save(P/'possibility_patch_v13.wav',patch)
# Replace offscreen warning, retaining the existing accompaniment.
old=pcm(P/'warning_v5.wav');new=pcm(W/'warning.wav');at=1056*SPF
assert at+len(new)<(987*SPF+round((24.08-526/30)*SR)), 'Warning overlaps Sobaya line'
edited[at:at+len(old)]-=old;edited[at:at+len(new)]+=new;changed[at:at+max(len(old),len(new))]=True
assert np.array_equal(edited[~changed],base[~changed])
shutil.copy2(W/'warning.wav',P/'warning_v13.wav')
# Keep reaction picture and sound together; remove name and trailing extra words.
# Source 1.5–4.4s lies within surrounding silence, retaining 誰この人。こわ… .
start=1361;end=1541;keep0=45;keep1=132
out=np.concatenate([edited[:start*SPF],edited[(start+keep0)*SPF:(start+keep1)*SPF],edited[end*SPF:]])
save(PUB/'master_v13.wav',out)
# Standalone review clips.
save(P/'deduction_repaired_v13.wav',edited[597*SPF:721*SPF])
save(P/'reaction_trimmed_v13.wav',edited[(start+keep0)*SPF:(start+keep1)*SPF])
m=json.loads((S/'edit-manifest-v12.json').read_text());m['audio']='master_v13.wav';cursor=0
for shot in m['shots']:
 if shot['file']=='wan3_result_v2_marker_v12_480p.mp4':shot['file']='wan3_result_v2_480p.mp4'
 if shot['file']=='wan3_aftermath_v12c_potfix_480p.mp4':shot['sourceStart']=keep0;shot['duration']=keep1-keep0
 shot['from']=cursor;cursor+=shot['duration']
m['durationInFrames']=cursor;assert len(out)==cursor*SPF
(S/'edit-manifest-v13.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
f=S/'Root.tsx';s=f.read_text()
if 'edit-manifest-v13' not in s:
 s=s.replace('export const Root',"import repaired from './edit-manifest-v13.json';\nexport const Root")
 s=s.replace('</>;', '<Composition id="DokuChikuwaRepaired" component={DokuChikuwa} defaultProps={{manifest:repaired,drama:true,records:true,enhanced:true}} width={1280} height={720} fps={30} durationInFrames={repaired.durationInFrames}/>\n</>;');f.write_text(s)
r={'version':13,'fps':30,'duration_frames':cursor,'marker_overlay_removed':True,'video_regenerated':False,'model':'Aratako/Irodori-TTS-v4-Large','seed':100,'caption':'','cfg_text':3,'duration_scale':1,'uncut':True,'asr_usage':'boundary location only; not pronunciation approval or retry trigger','tts_attempts_per_line':1,'time_stretch':False,'outside_audio_patches_pcm_equal':True,'deduction':{'text':'被害者は、大のちくわ好きだった可能性が高い。','reference':'yotan_reference_v13.wav','reference_source':'wan3_investigation_v12_480p.mp4','reference_seconds':[0,124/30],'reference_sha256':sha(P/'yotan_reference_v13.wav'),'target_frames':[684,702],'source_seconds':[2.70,3.25],'gain':gain,'padding_seconds':.05,'edge_fade_samples':fade,'replacement':'possibility_patch_v13.wav'},'warning':{'text':'おい！それは証拠品ギュン！','reference':'warning_v5.wav','reference_sha256':sha(P/'warning_v5.wav'),'start_frame':1056,'duration_seconds':len(new)/SR,'replacement':'warning_v13.wav'},'reaction':{'source':'wan3_aftermath_v12c_potfix_480p.mp4','keep_frames':[keep0,keep1],'audio_preserved':True},'listening_approval':'user','precise_lip_sync_verified':False}
(P/'edit_v13_record.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False,indent=2))
