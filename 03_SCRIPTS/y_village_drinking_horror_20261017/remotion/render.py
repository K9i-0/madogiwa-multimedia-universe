import subprocess,json,os
from pathlib import Path
P=Path(__file__).resolve().parent
subprocess.run(['npx','remotion','render','src/index.ts','YVillage','out/visual_v5.mp4','--muted','--codec=h264','--crf=20','--concurrency=6','--log=info'],cwd=P,check=True)
m=json.loads((P/'src/edit-manifest.json').read_text())
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','json',str(P/'out/visual_v5.mp4')]))
assert int(probe['streams'][0]['nb_frames'])==m['composition']['durationInFrames'], 'Interrupted or stale visual render; refusing to mux'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'out/visual_v5.mp4'),'-i',str(P/'public/mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(P.parent/'review_remotion_horror_aoyama_v5.mp4')],check=True)

canonical=P.parent/"review_remotion_horror.mp4"
canonical.unlink(missing_ok=True)
os.link(P.parent/"review_remotion_horror_aoyama_v5.mp4",canonical)
