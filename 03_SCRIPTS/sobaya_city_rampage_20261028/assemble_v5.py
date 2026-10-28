#!/usr/bin/env python3
"""Replace only landing frames [538,691); preserve v4b timeline at 30fps."""
from pathlib import Path
import subprocess,json
P=Path(__file__).resolve().parent
segments=[('generated/assembled_v4b_lossless.mkv',0,538),('wan3_v5_landing_480p.mp4',0,153),('generated/assembled_v4b_lossless.mkv',691,900)]
cmd=['ffmpeg','-hide_banner','-loglevel','error']
for name,_,_ in segments:cmd+=['-i',str(P/name)]
filters=[]
for i,(_,start,end) in enumerate(segments):
 filters += [f'[{i}:v]fps=30,trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS,setsar=1[v{i}]',f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start_sample={start*1600}:end_sample={end*1600},asetpts=PTS-STARTPTS[a{i}]']
filters+=[''.join(f'[v{i}][a{i}]' for i in range(3))+'concat=n=3:v=1:a=1[v][a]']
out=P/'generated/assembled_v5_lossless.mkv'
cmd+=['-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-c:v','ffv1','-level','3','-c:a','pcm_s24le','-y',str(out)]
subprocess.run(cmd,check=True)
(P/'patch_manifest_v5.json').write_text(json.dumps({'fps':30,'total_frames':900,'base':'generated/assembled_v4b_lossless.mkv','segments':[{'source':n,'start_frame':s,'end_frame_exclusive':e} for n,s,e in segments],'output':str(out.relative_to(P)),'retiming':False,'music_source_in':26,'music_source_out':56},indent=2)+'\n')
print(out)
