from pathlib import Path
import subprocess,sys
p=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(p/'mix_audio.py')],check=True)
subprocess.run(['npx','remotion','render','src/index.ts','Explainer','out/visuals.mp4','--muted','--concurrency=2','--log=error'],cwd=p,check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(p/'out/visuals.mp4'),'-i',str(p/'public/mixed.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(p.parent/'final_remotion_aeron_chua.mp4')],check=True)
