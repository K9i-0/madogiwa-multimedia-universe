"""Remove two generated shirt point-shadows with tightly bounded video interpolation.
The original H3 clip remains immutable. H.264 lossless; original audio copied.
"""
from pathlib import Path
import hashlib,json,subprocess
EP=Path(__file__).resolve().parent
source=EP/'generated/h3-job/results/q1_480p.mp4'
out=EP/'generated/retouched/q1_480p_clean.mp4';out.parent.mkdir(parents=True,exist_ok=True)
filters='delogo=x=590:y=251:w=25:h=25,delogo=x=529:y=248:w=16:h=23'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-vf',filters,'-c:v','libx264','-preset','medium','-crf','0','-pix_fmt','yuv420p','-c:a','copy',str(out)],check=True)
record={'source':str(source.relative_to(EP)),'output':str(out.relative_to(EP)),'filters':filters,'purpose':'Remove small nipple-like point shadows; preserve mask, face, chest shape, broad shading and cloth folds.','scale_change':False,'audio':'stream copy','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
(EP/'retouch-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
