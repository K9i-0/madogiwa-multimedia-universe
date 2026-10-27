"""Reproducible 45s concert test: original opening, move to main stage, chorus.
Original audio remains at source speed; no vocal synthesis or time stretching.
"""
from pathlib import Path
import subprocess, json
P=Path(__file__).resolve().parent
SOURCE=P.parent.parent/'【ｷﾞｭﾝﾚﾎﾞ】テイク3★（変換済み）.mov'
OUTPUT=P/'final_gyunrevo_live_test_45s_720p.mp4'
videos=[P/'local/wan3_part01_480p.mp4',P/'local/wan3_movement_480p.mp4',P/'local/wan3_chorus_480p.mp4']
cmd=['ffmpeg','-y','-v','error']
for v in videos:cmd+=['-i',str(v)]
cmd+=['-i',str(SOURCE)]
f=[]
for i in range(3):
    f.append(f'[{i}:v]trim=start=0:end=15,setpts=PTS-STARTPTS,fps=30,scale=960:720:flags=lanczos,setsar=1,format=yuv420p[v{i}]')

f.append('[v0][v1][v2]concat=n=3:v=1:a=0[vjoined]')
f.append('[vjoined]fade=t=out:st=44.6:d=0.4[v]')
f.append('[1:a]atrim=start=0:end=15,asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,apad,atrim=duration=15,asplit=4[c0][c1][c2][c3]')
f.append('[c0][c1]acrossfade=d=0.7:c1=tri:c2=tri[c01]')
f.append('[c01][c2]acrossfade=d=0.7:c1=tri:c2=tri[c012]')
f.append('[c012][c3]acrossfade=d=0.7:c1=tri:c2=tri,atrim=duration=45,volume=0.20[crowd]')
f.append('[3:a]asplit=2[srca][srcb]')
f.append('[srca]atrim=start=7:end=37,asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,afade=t=out:st=29.97:d=0.03[songa]')
f.append('[srcb]atrim=start=72:end=87,asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.03[songb]')
f.append('[songa][songb]concat=n=2:v=0:a=1,volume=0.8[song]')
f.append('[song][crowd]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.97:level=0:latency=1,afade=t=out:st=44.6:d=0.4[a]')
cmd+=['-filter_complex',';'.join(f),'-map','[v]','-map','[a]','-t','45','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-movflags','+faststart',str(OUTPUT)]
subprocess.run(cmd,check=True)
print(OUTPUT)
