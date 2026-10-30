"""Link original H3 footage, build a sample-accurate audio master from edit-manifest."""
import json,os,subprocess
from pathlib import Path
EP=Path(__file__).resolve().parent
PUBLIC=EP/'remotion/public'
def main():
 m=json.loads((EP/'remotion/src/edit-manifest.json').read_text()); fps=m['composition']['fps']; total=m['composition']['durationInFrames']
 for seg in m['segments']:
  target=PUBLIC/seg['file'];source=EP/seg['source'] if 'source' in seg else EP/'generated/h3-bbq-v1/results'/Path(seg['file']).name
  if not source.exists():source=EP/'generated/partials'/Path(seg['file']).name
  if not source.exists():raise FileNotFoundError(source)
  target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():os.link(source,target)
 args=['ffmpeg','-y','-v','error']
 for s in m['segments']:args+=['-i',str(PUBLIC/s['file'])]
 args+=['-i',str(PUBLIC/m['music']['file'])]
 filters=[]
 for i,s in enumerate(m['segments']):
  first=round(s['trimStartFrame']/fps*48000); count=round(s['durationInFrames']/fps*48000)
  filters.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start_sample={first}:end_sample={first+count},asetpts=PTS-STARTPTS,apad=whole_len={count},atrim=end_sample={count}[a{i}]')
 filters.append(''.join(f'[a{i}]' for i in range(len(m['segments'])))+f'concat=n={len(m["segments"])}:v=0:a=1[dialogue]')
 stop=m['music']['stopFrame']/fps
 filters.append(f'[{len(m["segments"])}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=end={stop},asetpts=PTS-STARTPTS,volume={m["music"]["gainDb"]}dB,afade=t=in:d=0.35,afade=t=out:st={stop-0.012}:d=0.012,apad=whole_dur={total/fps}[bgm]')
 filters.append(f'[dialogue][bgm]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95:level=false,afade=t=out:st={total/fps-.15}:d=0.15[master]')
 subprocess.run(args+['-filter_complex',';'.join(filters),'-map','[master]','-c:a','pcm_s24le',str(PUBLIC/'master.wav')],check=True)
 print('MASTER',PUBLIC/'master.wav')
if __name__=='__main__':main()
