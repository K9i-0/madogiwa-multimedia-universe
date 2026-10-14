"""Re-render website ranges after the final QA fix, retaining the full timeline.

A fresh `node render_v2.cjs full` also includes this correction. This helper
reuses an existing full visual render and performs a frame-accurate replacement.
"""
from pathlib import Path
import hashlib
import json
import subprocess

P = Path(__file__).resolve().parent
m = json.loads((P / 'src/edit-manifest-v2.json').read_text())
rows = m['dialogue']
ranges = []
for i, row in enumerate(rows):
    if row['view'] == 'website' and (i == 0 or rows[i-1]['view'] != 'website'):
        end = next((d['startFrame'] for d in rows[i+1:] if d['view'] != 'website'), m['composition']['durationInFrames'])
        ranges.append((row['startFrame'], end))
assert ranges == [(15536, 16370), (18587, 18681)]
base = P / 'out/visuals-v2.mp4'
assert base.exists()
for i, (start, end) in enumerate(ranges):
    with (P / f'out/sitefix_render_{i}.log').open('w') as log:
        subprocess.run(['node', 'render_v2.cjs', 'short', str(start), str(end-1)], cwd=P, stdout=log, stderr=subprocess.STDOUT, check=True)
    (P / 'out/short-v2.mp4').replace(P / f'out/sitefix_{i}.mp4')
    print('Rendered', start, end, flush=True)

graph = '[0:v]split=3[x0][x1][x2];'
graph += '[x0]trim=start_frame=0:end_frame=15536,setpts=PTS-STARTPTS[a];'
graph += '[1:v]setpts=PTS-STARTPTS[b];'
graph += '[x1]trim=start_frame=16370:end_frame=18587,setpts=PTS-STARTPTS[c];'
graph += '[2:v]setpts=PTS-STARTPTS[d];'
graph += '[x2]trim=start_frame=18681:end_frame=19283,setpts=PTS-STARTPTS[e];'
graph += '[a][b][c][d][e]concat=n=5:v=1:a=0[out]'
with (P / 'out/sitefix_concat.log').open('w') as log:
    subprocess.run(['ffmpeg', '-y', '-i', str(base), '-i', 'out/sitefix_0.mp4', '-i', 'out/sitefix_1.mp4', '-filter_complex', graph, '-map', '[out]', '-an', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '30', '-fps_mode', 'cfr', 'out/visuals-v2-sitefix.mp4'], cwd=P, stdout=log, stderr=subprocess.STDOUT, check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'out/visuals-v2-sitefix.mp4', '-i', 'public/mixed-v2.wav', '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '../final_remotion_tripo_workflow_v2.mp4'], cwd=P, check=True)
record = {'sourceFrameHeld': 540, 'trimBeforeFrames': 150, 'sceneFreezeFrame': 390, 'replacedFrameRangesEndExclusive': ranges, 'baseSha256': hashlib.sha256(base.read_bytes()).hexdigest(), 'finalFramesExpected': m['composition']['durationInFrames'], 'encoding': 'libx264 CRF16 yuv420p, source 30fps retained; AAC from original mix'}
(P.parent / 'site_repair_v2.json').write_text(json.dumps(record, ensure_ascii=False, indent=2))
print('Final MP4 updated; run audit_final_v2.py again.', flush=True)
