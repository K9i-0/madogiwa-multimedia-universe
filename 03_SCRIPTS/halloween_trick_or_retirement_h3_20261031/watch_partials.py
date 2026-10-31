"""Read-only completion polling and local playable previews. No new GPU jobs."""
import json,subprocess,time
from pathlib import Path
EP=Path(__file__).resolve().parent
out=EP/'generated/partials';out.mkdir(parents=True,exist_ok=True)
started=time.time();shown=set()
while time.time()-started<7200:
 result=subprocess.run(['python3',str(EP/'collect_partial.py')],text=True,capture_output=True)
 if result.returncode:
  print('STATUS_RETRY',result.stderr[-300:],flush=True)
 else:
  for source in sorted(out.glob('ch*_480p.mp4')):
   if source.name in shown:continue
   preview=EP/('preview_'+source.stem.replace('_480p','')+'_720p_v1.mp4')
   if not preview.exists():
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-vf','scale=1280:720:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(preview)],check=True)
   shown.add(source.name);print('PLAYABLE',preview,flush=True)
  if len(shown)==4:break
 state_path=EP/'generated/h3-v1/job.json'
 if state_path.exists() and json.loads(state_path.read_text()).get('status')=='stopped':
  print('GPU STOPPED; remaining files are in results',flush=True);break
 time.sleep(35)
