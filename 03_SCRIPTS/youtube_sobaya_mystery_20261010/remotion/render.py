from pathlib import Path
import subprocess,sys
p=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(p/'mix_audio.py')],check=True)
subprocess.run(['npx','remotion','render','src/index.ts','Explainer','out/visuals_v2.mp4','--muted','--concurrency=4','--log=error','--crf=19'],cwd=p,check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(p/'out/visuals_v2.mp4'),'-i',str(p/'public/mixed.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(p.parent/'final_remotion_sobaya_mystery_v2.mp4')],check=True)
