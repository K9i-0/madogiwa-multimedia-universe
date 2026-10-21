from pathlib import Path
import subprocess,sys
P=Path(__file__).resolve().parent
if '--no-mix' not in sys.argv:subprocess.run([sys.executable,str(P/'mix_audio.py')],check=True)
subprocess.run(['npx','remotion','render','src/index.ts','FlutterKaigi','out/visuals_v2.mp4','--muted','--concurrency=4','--crf=18','--log=info'],cwd=P,check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'out/visuals_v2.mp4'),'-i',str(P/'public/mixed.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(P.parent/'final_remotion_flutterkaigi_v2.mp4')],check=True)
