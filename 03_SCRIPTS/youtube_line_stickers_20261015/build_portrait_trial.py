"""Render a local-only reflow experiment; never changes scheduled media or upload records."""
from pathlib import Path
import subprocess
p=Path(__file__).resolve().parent
r=p/'remotion'
subprocess.run(['npx','remotion','render','src/index.ts','PortraitTrial','out/portrait_trial_silent.mp4','--muted','--concurrency=6','--crf=18','--log=error'],cwd=r,check=True)
subprocess.run(['ffmpeg','-v','error','-i',str(r/'out/portrait_trial_silent.mp4'),'-i',str(p/'final_remotion_shorts_9x16.mp4'),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart','-y',str(r/'out/shorts_portrait_trial.mp4')],check=True)
