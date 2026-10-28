#!/usr/bin/env python3
"""Local timing correction only; no additional generation. All timing is integer 30fps frames."""
from pathlib import Path
import subprocess,json
P=Path(__file__).resolve().parent
plans=[('flyby',[(0,18,18),(18,54,11),(54,210,160)])]
for name,parts in plans:
 filters=[]
 for i,(start,end,count) in enumerate(parts):
  ratio=count/(end-start);speed=1/ratio
  tempos=[]
  while speed>2:tempos.append('atempo=2');speed/=2
  tempos.append(f'atempo={speed:.10f}')
  filters += [f'[0:v]trim=start_frame={start}:end_frame={end},setpts=(PTS-STARTPTS)*{ratio:.10f},fps=30,tpad=stop_mode=clone:stop_duration=1,trim=end_frame={count},setsar=1[v{i}]',f'[0:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start_sample={start*1600}:end_sample={end*1600},asetpts=PTS-STARTPTS,'+','.join(tempos)+f',apad,atrim=end_sample={count*1600}[a{i}]']
 filters+=[''.join(f'[v{i}][a{i}]' for i in range(len(parts)))+f'concat=n={len(parts)}:v=1:a=1[v][a]']
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(P/f'wan3_v8_{name}_native720p.mp4'),'-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-c:v','ffv1','-level','3','-c:a','pcm_s24le','-y',str(P/f'generated/refined_v8b_{name}.mkv')],check=True)
(P/'timing_refinement_v8b.json').write_text(json.dumps({'fps':30,'plans':plans,'scope':'only newly generated scenes','flyby_transit_frames':11,'additional_paid_generation':False},indent=2)+'\n')
