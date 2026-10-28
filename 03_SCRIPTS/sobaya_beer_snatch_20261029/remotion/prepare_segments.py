"""Build frame-exact retimed clips. Keep audio at its original pitch and speed."""
from pathlib import Path
import json,subprocess
root=Path(__file__).resolve().parent
m=json.loads((root/'src/edit-manifest.json').read_text())
fps=m['fps']; source=root.parent/m['source']
for i,s in enumerate(m['segments']):
    start,end=s['sourceStart'],s['sourceEnd']; count=s['outputFrames']; duration=count/fps
    speed=(end-start)/count
    audio_start=s.get('audioStart',start)/fps
    filters=f'[0:v]trim=start_frame={start}:end_frame={end},setpts=(PTS-STARTPTS)/{speed},fps={fps},scale=1280:720:flags=lanczos,setsar=1,tpad=stop_mode=clone:stop_duration=1,trim=end_frame={count}[v];[0:a]atrim=start={audio_start}:duration={duration},asetpts=PTS-STARTPTS,aresample=48000,apad,atrim=duration={duration},afade=t=in:d=0.005,afade=t=out:st={max(0,duration-0.005)}:d=0.005[a]'
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-filter_complex',filters,'-map','[v]','-map','[a]','-c:v','libx264','-crf','16','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k',str(root/f'public/segment_{i}.mp4')],check=True)
