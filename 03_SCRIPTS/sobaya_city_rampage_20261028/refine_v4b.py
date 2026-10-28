#!/usr/bin/env python3
"""Local timing correction only; no additional generation. All timing is integer 30fps frames."""
from pathlib import Path
import subprocess,json
P=Path(__file__).resolve().parent
plans=[('opening',[(30,150,146)]),('flyby',[(0,18,18),(18,57,11),(57,210,159)])]
for name,parts in plans:
 filters=[]
 for i,(start,end,count) in enumerate(parts):
  ratio=count/(end-start);speed=1/ratio
  tempos=[]
  while speed>2:tempos.append('atempo=2');speed/=2
  tempos.append(f'atempo={speed:.10f}')
  filters += [f'[0:v]trim=start_frame={start}:end_frame={end},setpts=(PTS-STARTPTS)*{ratio:.10f},fps=30,tpad=stop_mode=clone:stop_duration=1,trim=end_frame={count},setsar=1[v{i}]',f'[0:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start_sample={start*1600}:end_sample={end*1600},asetpts=PTS-STARTPTS,'+','.join(tempos)+f',apad,atrim=end_sample={count*1600}[a{i}]']
 filters+=[''.join(f'[v{i}][a{i}]' for i in range(len(parts)))+f'concat=n={len(parts)}:v=1:a=1[v][a]']
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(P/f'wan3_v4_{name}_480p.mp4'),'-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-c:v','ffv1','-level','3','-c:a','pcm_s24le','-y',str(P/f'generated/refined_v4b_{name}.mkv')],check=True)
(P/'timing_refinement_v4b.json').write_text(json.dumps({'fps':30,'plans':plans,'scope':'only newly generated scenes','flyby_transit_frames':11,'additional_paid_generation':False},indent=2)+'\n')
s=(P/'assemble_v4.py').read_text().replace("'wan3_v4_opening_480p.mp4'","'generated/refined_v4b_opening.mkv'").replace("'wan3_v4_flyby_480p.mp4'","'generated/refined_v4b_flyby.mkv'").replace('assembled_v4_lossless','assembled_v4b_lossless').replace('patch_manifest_v4.json','patch_manifest_v4b.json').replace("'retiming':False","'retiming':'only replacement scenes; see timing_refinement_v4b.json'")
(P/'assemble_v4b.py').write_text(s)
s=(P/'render_bgm_v4.py').read_text().replace('_v4','_v4b').replace("'video_retiming':False","'video_retiming':'replacement scenes only; retained v3 scenes unchanged'")
(P/'render_bgm_v4b.py').write_text(s)
