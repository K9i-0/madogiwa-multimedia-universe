"""Render retained source frame ranges and mux matching 32kHz H3 audio."""
from pathlib import Path
import json,subprocess,os
os.chdir(Path(__file__).resolve().parent)
m=json.loads(Path('src/edit-manifest.json').read_text());fps=m['composition']['fps'];ranges=m['sourceRanges']
assert sum(r['endFrame']-r['startFrame'] for r in ranges)==m['composition']['durationInFrames']
Path('out').mkdir(exist_ok=True)
subprocess.run(['npx','remotion','render','src/index.ts',m['composition']['id'],'out/news_picture.mp4','--codec=h264','--overwrite'],check=True)
filters=[]
for i,r in enumerate(ranges):
 filters.append(f"[1:a]atrim=start={r['startFrame']/fps}:end={r['endFrame']/fps},asetpts=PTS-STARTPTS[a{i}]")
filters.append(''.join(f'[a{i}]' for i in range(len(ranges)))+f'concat=n={len(ranges)}:v=0:a=1[a]')
subprocess.run(['ffmpeg','-y','-v','error','-i','out/news_picture.mp4','-i','public/'+m['inputVideo'],'-filter_complex',';'.join(filters),'-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-ar','32000','-movflags','+faststart','../final_remotion_news.mp4'],check=True)
