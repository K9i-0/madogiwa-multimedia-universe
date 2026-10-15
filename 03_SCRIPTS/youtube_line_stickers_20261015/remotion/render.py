"""Render visuals, then mux the measured final dialogue/music mix."""
from pathlib import Path
import argparse, json, subprocess
P=Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('output',nargs='?',default='out/review_line_stickers_v1.mp4')
p.add_argument('--concurrency',type=int,default=6)
args=p.parse_args()
out=Path(args.output)
if not out.is_absolute(): out=P/out
out.parent.mkdir(parents=True,exist_ok=True)
manifest=json.loads((P/'src/edit-manifest.json').read_text())
audio=P/'public'/manifest.get('audioSrc','mixed.wav')
if not audio.exists(): raise SystemExit(f'Audio missing: {audio}')
visual=P/'out'/f'{out.stem}_visuals.mp4'
subprocess.run(['npx','remotion','render','src/index.ts','Explainer',str(visual),'--muted',f'--concurrency={args.concurrency}','--crf=18','--log=error'],cwd=P,check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(visual),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out)],check=True)
print(out)
