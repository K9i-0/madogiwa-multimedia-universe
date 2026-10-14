"""Reproduce the approved opening as a portrait teaser; no uploads."""
from pathlib import Path
import json
import subprocess
import argparse

parser=argparse.ArgumentParser()
parser.add_argument("--skip-render",action="store_true")
args=parser.parse_args()

ROOT=Path(__file__).resolve().parent
EP=ROOT.parent
M=json.loads((ROOT/'src/shorts-manifest.json').read_text())
CUT=M['cutFrame']/M['fps']
DURATION=M['durationInFrames']/M['fps']
SOURCE=EP/'final_remotion_ai_video_workflow_v12.mp4'
OUT=EP/'final_remotion_workflow_shorts_9x16.mp4'
VISUAL=ROOT/'out/workflow_shorts_visuals.mp4'
def run(args):subprocess.run(args,cwd=ROOT,check=True)
link=ROOT/'public/shorts_source_v12.mp4'
if not link.exists():link.hardlink_to(SOURCE)
if not args.skip_render:run(['npx','remotion','render','src/shorts-entry.tsx','WorkflowShorts',str(VISUAL),'--muted','--concurrency=4','--crf=18','--log=error'])
# Preserve all source dialogue. The silent lead-in supplies the final card's BGM;
# its first 0.3s crossfades within the last speech-free gap (1698..1707).
run(['ffmpeg','-v','error','-y','-i',str(VISUAL),'-i',str(SOURCE),'-filter_complex',
 f'[1:a]atrim=end={CUT},asetpts=PTS-STARTPTS[a];'
 '[1:a]atrim=start=0:end=2.4,asetpts=PTS-STARTPTS,afade=t=out:st=1.4:d=1,apad=pad_dur=0.9[b];'
 '[a][b]acrossfade=d=0.3:c1=tri:c2=tri,'
 f'atrim=end={DURATION},afade=t=out:st={DURATION-1.3}:d=1.3[aout]',
 '-map','0:v:0','-map','[aout]','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t',str(DURATION),'-movflags','+faststart',str(OUT)])
print(OUT)
