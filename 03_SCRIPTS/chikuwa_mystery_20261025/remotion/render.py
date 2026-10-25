from pathlib import Path
import subprocess,sys
D=Path(__file__).resolve().parent;P=D.parent;R=P.parents[1];py=R/'.local/voicevox-explainer/venv/bin/python'
for script in ['prepare_assets.py','prepare_edit.py','mix_audio.py']:subprocess.run([str(py),str(P/script)],check=True,cwd=R)
subprocess.run(['npm','run','typecheck'],cwd=D,check=True)
subprocess.run(['npm','run','render'],cwd=D,check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(D/'out/visuals.mp4'),'-i',str(D/'public/mixed.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(P/'final_remotion_chikuwa_mystery_v8.mp4')],check=True)
