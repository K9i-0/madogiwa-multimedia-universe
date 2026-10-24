from pathlib import Path
import json, os, subprocess
P=Path(__file__).resolve().parent
m=json.loads((P/'src/edit-manifest.json').read_text())
subprocess.run(['npx','remotion','render','src/index.ts','YVillageMask','out/visual.mp4','--muted','--codec=h264','--crf=19','--concurrency=6','--log=info'],cwd=P,check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','json',str(P/'out/visual.mp4')]))
assert int(probe['streams'][0]['nb_frames'])==m['composition']['durationInFrames']
temporary=P/'out/mux.mp4';target=P.parent/'review_remotion_horror_mask_v1.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'out/visual.mp4'),'-i',str(P/'public/mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(temporary)],check=True)
os.replace(temporary,target)
canonical=P.parent/'final_remotion_horror.mp4';canonical.unlink(missing_ok=True);os.link(target,canonical)
print(target)
