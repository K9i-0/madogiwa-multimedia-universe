"""Render the adopted opening into the Wan explainer's portrait teaser style."""
from pathlib import Path
import argparse,json,subprocess
P=Path(__file__).resolve().parent
m=json.loads((P/'src/shorts-manifest.json').read_text())
a=argparse.ArgumentParser();a.add_argument('--skip-render',action='store_true');args=a.parse_args()
def run(cmd):subprocess.run(cmd,cwd=P,check=True)
source=P.parent/m['source'];cut=m['cutFrame']/30;duration=m['durationInFrames']/30
link=P/'public/shorts_source_v6.mp4'
if not link.exists():link.hardlink_to(source)
if not args.skip_render:run(['node','render_shorts.cjs'])
# Continue the same music at the matching source time. Crossfade falls after speech.
run(['ffmpeg','-v','error','-y','-i',str(P/'out/shorts_visuals.mp4'),'-i',str(source),'-i',str(P/'public/intro.mp3'),'-filter_complex',
 f'[1:a]atrim=end={cut},asetpts=PTS-STARTPTS[a];'
 f'[2:a]loudnorm=I=-34:TP=-3:LRA=11,atrim=start={cut-.15}:end={duration},asetpts=PTS-STARTPTS[b];'
 f'[a][b]acrossfade=d=0.15:c1=tri:c2=tri,atrim=end={duration},afade=t=out:st={duration-1}:d=1[aout]',
 '-map','0:v','-map','[aout]','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t',str(duration),'-movflags','+faststart',str(P.parent/'final_remotion_shorts_9x16.mp4')])
