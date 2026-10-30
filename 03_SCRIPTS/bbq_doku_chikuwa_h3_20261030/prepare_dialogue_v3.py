"""Apply the three user-requested v2 edits, preserving original H3 video frames."""
from pathlib import Path
import json,hashlib,subprocess,shutil,sys
EP=Path(__file__).resolve().parent;ROOT=EP.parents[1];OUT=EP/'generated/dialogue-v3';OUT.mkdir(exist_ok=True)
def run(*a):subprocess.run(list(map(str,a)),check=True)
def ff(*a):run('ffmpeg','-y','-v','error',*a)
source=EP/'generated/partials/ch03_480p.mp4';voice=EP/'ch3_yotan_smell_v3.wav'
ff('-i',source,'-vn','-ar','48000','-ac','2','-c:a','pcm_s16le',OUT/'original.wav')
# 72..144 frames (3..6 seconds) cover the old reply and the new natural-length line.
ff('-i',voice,'-af','apad=whole_dur=3,atrim=end=3','-ar','48000','-ac','2','-c:a','pcm_s16le',OUT/'replacement.wav')
patched=OUT/'patched.wav'
if not patched.exists():run(sys.executable,ROOT/'.claude/skills/wan-video/scripts/patch_pcm_audio.py',OUT/'original.wav',OUT/'replacement.wav',patched,'--target-start','3','--source-start','0','--duration','3')
ff('-i',source,'-i',patched,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-map_metadata','-1',OUT/'ch03_dialogue_v3.mp4')
f=EP/'remotion/src/edit-manifest.json';old=f.with_name('edit-manifest-v2.json')
if not old.exists():shutil.copy2(f,old)
m=json.loads(old.read_text());m['segments']=[s for s in m['segments'] if s['id']!='discovery_a']
for s in m['segments']:
 if s['id']=='toast':s['trimStartFrame']=24;s['durationInFrames']=24
 if s['id']=='eat':s['source']='generated/dialogue-v3/ch03_dialogue_v3.mp4';s['file']='h3/ch03_dialogue_v3.mp4'
cursor=0
for s in m['segments']:s['startFrame']=cursor;cursor+=s['durationInFrames']
m['composition']['durationInFrames']=cursor;st={s['id']:s['startFrame'] for s in m['segments']}
for c in m['captions']:
 if c['text']=='乾杯！':c['endFrame']=224
 elif c['text']=='これ、いい感じに焼けました':c['startFrame']=st['eat'];c['endFrame']=st['eat']+72
 elif c['text']=='お、うまそう':c['text']='なんか臭い変じゃない？';c['startFrame']=st['eat']+72;c['endFrame']=st['eat']+134
 elif c['speaker']=='やめ太郎' and c['startFrame']>200:c['startFrame']=st['discovery_b'];c['endFrame']=st['discovery_b']+102
 elif c['text']=='なんで買ってるんだよ':c['startFrame']=st['discovery_b']+102;c['endFrame']=st['discovery_b']+158
 elif c['text']=='これ、毒ちくわです':c['startFrame']-=70;c['endFrame']-=70
m['music']['stopFrame']-=70
m['audit']='v3 user edits: remove first toast (24 frames), replace Yotan reply with Irodori Large natural 2.56s line inside original 3..6s window, remove entire first discovery closeup (46 frames). All retained video frames and playback speeds unchanged from v2. New line is dubbed; phoneme-level lip synchronization not certified.'
f.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
record={'source_master':'final_remotion_bbq_v2.mp4','output':'final_remotion_bbq_v3.mp4','removed_v2_frames':[[200,224],[542,588]],'new_line':{'text':'なんか臭い変じゃない？','generation_text':'なんか、におい変じゃない？','file':voice.name,'model':'Aratako/Irodori-TTS-v4-Large','seed':100,'caption':'','cfg_text':5,'uncut':True,'duration_scale':1,'duration_seconds':2.56,'reference':'voice_ref_yotan_h3_v3.wav','reference_source':'generated/h3-shirt-prompt-test-v1/results/ch01_480p.mp4','reference_interval_seconds':[0,3.2],'reference_sha256':hashlib.sha256((EP/'voice_ref_yotan_h3_v3.wav').read_bytes()).hexdigest(),'sha256':hashlib.sha256(voice.read_bytes()).hexdigest(),'patch_source_frames':[72,144],'speed_change':False,'gain_db':0},'pcm_patch':json.loads((OUT/'patched.patch.json').read_text()),'composition':m['composition']}
(EP/'dialogue-v3-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('READY',cursor,'frames',cursor/24,'seconds')
