from pathlib import Path
import subprocess
P=Path(__file__).resolve().parent
# Final visual polish: copy the approved v15 audio without re-encoding.
audio=P.parent/'final_remotion_flutterkaigi_v15.mp4'
assert audio.exists(), 'Approved v15 audio source is required'
subprocess.run(['npx','remotion','render','src/index.ts','FlutterKaigi','out/visuals_v16.mp4','--muted','--concurrency=8','--crf=18','--log=info'],cwd=P,check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'out/visuals_v16.mp4'),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(P.parent/'final_remotion_flutterkaigi_final.mp4')],check=True)
