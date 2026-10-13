from pathlib import Path
import subprocess,sys
P=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(P/'mix_audio.py')],check=True)
subprocess.run(['npx','remotion','render','src/index.ts','Explainer','out/visuals.mp4','--muted','--concurrency=4','--crf=18','--log=error'],cwd=P,check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'out/visuals.mp4'),'-i',str(P/'public/mixed.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(P/'out/final_mux.mp4')],check=True)

(P/'out/final_mux.mp4').replace(P.parent/'final_remotion_ai_video_workflow.mp4')
