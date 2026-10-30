"""Assemble retrieved H3 originals; preserve all first-version inputs and outputs."""
from pathlib import Path
import json, subprocess
EP=Path(__file__).resolve().parent
m=json.loads((EP/'remotion/src/edit-manifest.json').read_text())
r=EP/'generated/h3_v1/results'; public=EP/'remotion/public'
def run(args):subprocess.run(args,check=True)
for s in m['segments']:
 name=s['id'];src=r/(name+'_480p.mp4')
 run(['ffmpeg','-y','-v','error','-i',str(src),'-vf','scale=1280:712:flags=lanczos,pad=1280:720:0:4,setsar=1','-frames:v',str(s['durationInFrames']),'-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(public/(name+'_720p.mp4'))])
args=['ffmpeg','-y','-v','error']
for s in m['segments']:args+=['-i',str(r/(s['id']+'_480p.mp4'))]
filters=[]
for i,s in enumerate(m['segments']):filters.append(f'[{i}:a]aresample=48000,apad,atrim=duration={s["durationInFrames"]/24},asetpts=PTS-STARTPTS[a{i}]')
filters.append(''.join(f'[a{i}]' for i in range(3))+'concat=n=3:v=0:a=1[out]')
run(args+['-filter_complex',';'.join(filters),'-map','[out]','-c:a','pcm_s16le',str(public/'master.wav')])
run(['npm','run','typecheck','--prefix',str(EP/'remotion')])
subprocess.run(['node','render.mjs','video'],cwd=EP/'remotion',check=True)
print(EP/'final_remotion_newyear_v2.mp4')
