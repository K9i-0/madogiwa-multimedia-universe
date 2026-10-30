from pathlib import Path
import subprocess,sys
P=Path(__file__).resolve().parent
if '--no-mix' not in sys.argv:subprocess.run([sys.executable,str(P/'mix_audio.py')],check=True)
subprocess.run(['npx','remotion','render','src/index.ts','FlutterKaigi','out/visuals_v12.mp4','--muted','--concurrency=8','--crf=18','--log=info'],cwd=P,check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'out/visuals_v12.mp4'),'-i',str(P/'public/mixed.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(P.parent/('final_remotion_flutterkaigi_v12.mp4' if all((P/'public'/f).exists() for f in ['intro.mp3','main.wav','unity.mp3']) else 'final_remotion_flutterkaigi_v12_nobgm.mp4'))],check=True)
