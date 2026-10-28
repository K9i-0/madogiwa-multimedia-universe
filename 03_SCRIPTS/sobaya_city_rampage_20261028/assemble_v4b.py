#!/usr/bin/env python3
"""Replace only frames [0,146) and [350,538); preserve v3 timeline at 30fps."""
from pathlib import Path
import subprocess,json
P=Path(__file__).resolve().parent
segments=[('generated/refined_v4b_opening.mkv',0,146),('wan3_sobaya_brewery_v3_480p.mp4',146,350),('generated/refined_v4b_flyby.mkv',0,188),('wan3_sobaya_brewery_v3_480p.mp4',538,900)]
cmd=['ffmpeg','-hide_banner','-loglevel','error']
for name,_,_ in segments:cmd+=['-i',str(P/name)]
filters=[]
for i,(_,start,end) in enumerate(segments):
 filters += [f'[{i}:v]fps=30,trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS,setsar=1[v{i}]',f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start_sample={start*1600}:end_sample={end*1600},asetpts=PTS-STARTPTS[a{i}]']
filters+=[''.join(f'[v{i}][a{i}]' for i in range(4))+'concat=n=4:v=1:a=1[v][a]']
out=P/'generated/assembled_v4b_lossless.mkv'
cmd+=['-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-c:v','ffv1','-level','3','-c:a','pcm_s24le','-y',str(out)]
subprocess.run(cmd,check=True)
(P/'patch_manifest_v4b.json').write_text(json.dumps({'fps':30,'total_frames':900,'base':'wan3_sobaya_brewery_v3_480p.mp4','segments':[{'source':n,'start_frame':s,'end_frame_exclusive':e} for n,s,e in segments],'output':str(out.relative_to(P)),'retiming':'only replacement scenes; see timing_refinement_v4b.json','music_source_in':26,'music_source_out':56},indent=2)+'\n')
print(out)
