from pathlib import Path
import subprocess,time,sys
P=Path(__file__).resolve().parent
while not (P.parent/'mix_record.json').exists():time.sleep(3)
subprocess.run([sys.executable,str(P/'validate_timeline.py')],check=True)
subprocess.run(['node','render.cjs','full'],cwd=P,check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'out/visuals.mp4'),'-i',str(P/'public/mixed.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(P.parent/'final_remotion_tripo_workflow_v1.mp4')],check=True)
print('FINAL_WRITTEN',flush=True)
