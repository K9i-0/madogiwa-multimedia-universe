#!/usr/bin/env python3
"""Restore adopted trailer picture, moving only removable dialogue into lower captions."""
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[3]
B=ROOT/'03_SCRIPTS/shorts_sobaya_20261016'
E=B/'episodes/madogiwa-super-try-sobaya-invasion-trailer'
ORIGINAL=ROOT/'03_SCRIPTS/66_madogiwa_super_try_invasion'
segments=json.loads((ORIGINAL/'remotion/src/trailer-voice-v3-manifest.json').read_text())['segments']
clean=ORIGINAL/'remotion/out/shorts-clean.mp4'
filters=[]
for i,s in enumerate(segments):
    idx=0 if s['kind']=='card' else 1
    start=s['from'] if idx==0 else s['sourceStart']
    filters.append(f'[{idx}:v]trim=start_frame={start}:end_frame={start+s["duration"]},setpts=PTS-STARTPTS[v{i}]')
filters.append(''.join(f'[v{i}]' for i in range(len(segments)))+f'concat=n={len(segments)}:v=1:a=0[v]')
subprocess.run(['ffmpeg','-v','error','-threads','2','-reinit_filter','0','-i',str(E/'source.mp4'),'-threads','2','-reinit_filter','0','-i',str(clean),'-filter_complex_threads','2','-filter_complex',';'.join(filters),'-map','[v]','-an','-r','30','-c:v','libx264','-threads','2','-preset','veryfast','-crf','16','-y',str(E/'source-clean.mp4')],check=True)
