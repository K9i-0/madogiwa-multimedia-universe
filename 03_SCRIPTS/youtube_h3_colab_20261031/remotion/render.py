from pathlib import Path
import subprocess,sys
P=Path(__file__).resolve().parent
if '--no-mix' not in sys.argv:subprocess.run([sys.executable,str(P/'mix_audio.py')],check=True)
subprocess.run(['npx','remotion','render','src/index.ts','H3Colab','out/visuals_v1.mp4','--muted','--concurrency=6','--crf=20','--log=info'],cwd=P,check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'out/visuals_v1.mp4'),'-i',str(P/'public/mixed.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(P.parent/'final_remotion_h3_colab_v1.mp4')],check=True)
