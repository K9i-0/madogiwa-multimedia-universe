import subprocess,json,os
from pathlib import Path
P=Path(__file__).resolve().parent
subprocess.run(['npx','remotion','render','src/index.ts','YVillage','out/visual.mp4','--muted','--codec=h264','--crf=20','--concurrency=6','--log=error'],cwd=P,check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'out/visual.mp4'),'-i',str(P/'public/mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(P.parent/'review_remotion_horror_aoyama_v3.mp4')],check=True)

canonical=P.parent/"review_remotion_horror.mp4"
canonical.unlink(missing_ok=True)
os.link(P.parent/"review_remotion_horror_aoyama_v3.mp4",canonical)
