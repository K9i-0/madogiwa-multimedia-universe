import subprocess,json,hashlib,re
from pathlib import Path
EP=Path(__file__).resolve().parent
video=EP/'final_remotion_mde_v2_16x9.mp4'
m=json.loads((EP/'remotion/src/edit-manifest.json').read_text())
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_entries','format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,nb_read_frames','-of','json',str(video)]))
v=next(s for s in probe['streams'] if s['codec_type']=='video')
a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'])==(1280,720,'30/1')
assert int(v['nb_read_frames'])==m['composition']['durationInFrames']
assert a['codec_name']=='aac'
decoded=subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True,check=True)
assert not decoded.stderr.strip(),decoded.stderr
loudness=subprocess.run(['ffmpeg','-hide_banner','-i',str(video),'-af','loudnorm=I=-18:TP=-2:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
match=re.search(r'\{\s*"input_i".*?\}',loudness.stderr,re.S);assert match
levels=json.loads(match[0]);assert float(levels['input_tp'])<0
report={'file':video.name,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'probe':probe,'expectedFrames':m['composition']['durationInFrames'],'fullDecode':'passed','loudness':levels,'captionSource':'approved dialogue; ASR phrase timing + text alignment','visualReview':'see remotion/out/audit and final video caption sheets','audioListening':'not performed; ASR and objective loudness/decode checks only','lipSync':'not claimed; interview uses still with camera move, archive masked character footage with new voice','originalAudio':'chair.mp4 25.0–28.5 seconds only; other B-roll muted','music':'original procedural underscore'}
(EP/'qa_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'seconds':m['composition']['durationInFrames']/30,'frames':v['nb_read_frames'],'lufs':levels['input_i'],'truePeak':levels['input_tp'],'decode':'passed'},ensure_ascii=False))
