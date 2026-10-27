"""Render static poster with feathered animated face; preserve H3 speech."""
from pathlib import Path
import os,json,subprocess,shutil
P=Path(__file__).resolve().parent;os.chdir(P)
m=json.loads(Path('src/edit-manifest.json').read_text());fps=m['composition']['fps']
Path('public').mkdir(exist_ok=True);Path('out').mkdir(exist_ok=True)
shutil.copy2('../poster.png','public/poster.png')
inputs=[];filters=[];labels=[]
for i,ch in enumerate(m['chapters']):
 source=P.parent/'generated/h3-job/results'/ch['file'];dest=P/'public'/ch['file']
 if not dest.exists():os.link(source,dest)
 inputs+=['-i',str(source)]
 start=ch['sourceStart']/fps;end=(ch['sourceStart']+ch['frames'])/fps
 filters.append(f'[{i}:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,apad=whole_dur={ch["frames"]/fps},atrim=duration={ch["frames"]/fps}[a{i}]');labels.append(f'[a{i}]')
assert sum(c['frames'] for c in m['chapters'])==m['composition']['durationInFrames']
filters.append(''.join(labels)+f'concat=n={len(labels)}:v=0:a=1[a]')
subprocess.run(['ffmpeg','-y','-v','error',*inputs,'-filter_complex',';'.join(filters),'-map','[a]','-ar','32000','-c:a','pcm_s16le','out/speech.wav'],check=True)
subprocess.run(['npx','remotion','render','src/index.ts',m['composition']['id'],'out/picture.mp4','--codec=h264','--crf=18','--overwrite'],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i','out/picture.mp4','-i','out/speech.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','../final_remotion_talking_poster.mp4'],check=True)
