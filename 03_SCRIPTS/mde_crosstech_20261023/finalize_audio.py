"""Master the complete mix while stream-copying video; keep raw render reproducible."""
import json,re,subprocess,os
from pathlib import Path
EP=Path(__file__).resolve().parent
src=EP/'remotion/out/raw-v2.mp4'
out=EP/'final_remotion_mde_v2_16x9.mp4'
tmp=EP/'remotion/out/mastered-v2.mp4'
measure=subprocess.run(['ffmpeg','-hide_banner','-i',str(src),'-af','loudnorm=I=-18:TP=-2:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
v=json.loads(re.search(r'\{\s*"input_i".*?\}',measure.stderr,re.S)[0])
af=f"loudnorm=I=-18:TP=-2:LRA=7:measured_I={v['input_i']}:measured_TP={v['input_tp']}:measured_LRA={v['input_lra']}:measured_thresh={v['input_thresh']}:offset={v['target_offset']}:linear=true"
subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),'-map','0:v:0','-map','0:a:0','-c:v','copy','-af',af,'-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(tmp)],check=True)
os.replace(tmp,out)
(EP/'audio_mastering_record.json').write_text(json.dumps({'input':str(src.relative_to(EP)),'output':out.name,'before':v,'filter':af,'video':'stream copied, no re-encoding'},ensure_ascii=False,indent=2)+'\n')
print('Audio master complete:',out.name)
