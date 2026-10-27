"""Replace live recording with supplied master; retain existing video bitstream."""
from pathlib import Path
import subprocess,json
P=Path(__file__).resolve().parent
root=P.parents[1]
master=next(root.glob('*.mp3'))
video=P/'final_gyunrevo_saturn_live_25s_720p.mp4'
crowd=P.parent/'gyunrevo_live_20261022/local/wan3_movement_480p.mp4'
out=P/'final_gyunrevo_saturn_master_crowd_25s_720p.mp4'
filters=';'.join([
'[1:a]atrim=start=71.08:duration=25,asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume=0.78[s]',
'[2:a]atrim=duration=15,asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,asplit=2[c0][c1]',
'[c0][c1]acrossfade=d=0.7:c1=tri:c2=tri,atrim=duration=25,highpass=f=160,lowpass=f=6500,volume=0.19,volume=\'if(lt(t,8),0.65,if(lt(t,17),1,1.2))\':eval=frame,afade=t=in:d=0.25[c]',
'[s][c]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95:level=0:latency=1,afade=t=out:st=24.6:d=0.4[a]'])
subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-i',str(master),'-i',str(crowd),'-filter_complex',filters,'-map','0:v:0','-map','[a]','-t','25','-c:v','copy','-c:a','aac','-b:a','256k','-movflags','+faststart',str(out)],check=True)
print(out)
