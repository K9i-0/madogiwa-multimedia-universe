"""Local shirt repair in the native H3 frame; preserve originals and copy audio."""
from pathlib import Path
import hashlib,json,subprocess

EP=Path(__file__).resolve().parent
repairs={
    'q2_r2':'delogo=x=274:y=362:w=64:h=53',
    'q3_r2':'delogo=x=518:y=277:w=23:h=32,delogo=x=638:y=273:w=42:h=36',
    'q4_r2':"delogo=x=549:y=292:w=29:h=37:enable='lt(t,4.95)+gte(t,5.125)',delogo=x=703:y=286:w=29:h=42",
    'q5_r2':'delogo=x=542:y=273:w=29:h=39,delogo=x=645:y=262:w=34:h=39',
}
records=[]
for key,filters in repairs.items():
    source=EP/f'generated/h3-r2/results/{key}_480p.mp4'
    output=EP/f'generated/retouched/{key}_480p_clean.mp4'
    output.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-vf',filters,
                    '-c:v','libx264','-preset','medium','-crf','0','-pix_fmt','yuv420p',
                    '-c:a','copy',str(output)],check=True)
    records.append({'source':str(source.relative_to(EP)),'output':str(output.relative_to(EP)),
                    'filters':filters,'purpose':'Remove generated nipple-like point shadow. Preserve face, mask, chest silhouette, broad shading and surrounding fabric folds.',
                    'scale_change':False,'audio':'stream copy',
                    'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                    'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest()})
(EP/'retouch-r2-record.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
