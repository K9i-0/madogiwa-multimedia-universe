"""Saturn concert: 25-second original chorus, crowd-only bed, single 720p resize."""
from pathlib import Path
import subprocess, json
P=Path(__file__).resolve().parent
video=P/'local/wan3_saturn_480p.mp4'
song=P/'local/song_077_102.wav'
# Use the image-reference-only crowd generated in the prior live test. This avoids
# carrying any regenerated singing from the reference-video task into the mix.
crowd=P.parent/'gyunrevo_live_20261022/local/wan3_movement_480p.mp4'
out=P/'final_gyunrevo_saturn_live_25s_720p.mp4'
filters=';'.join([
'[0:v]trim=duration=25,setpts=PTS-STARTPTS,fps=30,scale=1280:720:flags=lanczos,setsar=1,format=yuv420p,fade=t=out:st=24.6:d=0.4[v]',
'[2:a]atrim=duration=15,asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,asplit=2[c0][c1]',
'[c0][c1]acrossfade=d=0.7:c1=tri:c2=tri,atrim=duration=25,volume=0.18[c]',
'[1:a]atrim=duration=25,asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume=0.82[s]',
'[s][c]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.97:level=0:latency=1,afade=t=out:st=24.6:d=0.4[a]'])
subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-i',str(song),'-i',str(crowd),'-filter_complex',filters,'-map','[v]','-map','[a]','-t','25','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-movflags','+faststart',str(out)],check=True)
print(out)
