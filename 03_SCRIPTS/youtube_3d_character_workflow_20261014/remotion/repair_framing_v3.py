"""Re-render Takosan views with room for moving feet, preserving exact frames.

A fresh render_v3.cjs full already includes this camera correction. This helper
reuses the initial full visual render; no audio or timing is altered.
"""
from pathlib import Path
import hashlib
import json
import subprocess

P = Path(__file__).resolve().parent
m = json.loads((P / 'src/edit-manifest-v3.json').read_text())
rows = m['dialogue']
ranges = []
for i, row in enumerate(rows):
    if row['view'] in {'takosan_intro', 'tako_fix', 'tako_bones'} and (i == 0 or rows[i-1]['view'] != row['view']):
        end = next((d['startFrame'] for d in rows[i+1:] if d['view'] != row['view']), m['composition']['durationInFrames'])
        ranges.append((row['startFrame'], end))
assert len(ranges) == 3
base = P / 'out/visuals-v3.mp4'
assert base.exists()
for i, (start, end) in enumerate(ranges):
    with (P / f'out/framingfix_v3_{i}.log').open('w') as log:
        subprocess.run(['node', 'render_v3.cjs', 'short', str(start), str(end-1)], cwd=P, stdout=log, stderr=subprocess.STDOUT, check=True)
    (P / 'out/short-v3.mp4').replace(P / f'out/framingfix_v3_{i}.mp4')
    print('Rendered', start, end, flush=True)

graph = f"[0:v]split={len(ranges)+1}" + ''.join(f'[x{i}]' for i in range(len(ranges)+1)) + ';'
cursor = 0
labels = []
for i, (start, end) in enumerate(ranges):
    graph += f'[x{i}]trim=start_frame={cursor}:end_frame={start},setpts=PTS-STARTPTS[a{i}];'
    graph += f'[{i+1}:v]setpts=PTS-STARTPTS[b{i}];'
    labels += [f'[a{i}]', f'[b{i}]']
    cursor = end
graph += f'[x{len(ranges)}]trim=start_frame={cursor}:end_frame={m["composition"]["durationInFrames"]},setpts=PTS-STARTPTS[tail];'
labels.append('[tail]')
graph += ''.join(labels) + f'concat=n={len(labels)}:v=1:a=0[out]'
inputs = ['-i', str(base)]
for i in range(len(ranges)):
    inputs += ['-i', f'out/framingfix_v3_{i}.mp4']
with (P / 'out/framingfix_v3_concat.log').open('w') as log:
    subprocess.run(['ffmpeg', '-y', *inputs, '-filter_complex', graph, '-map', '[out]', '-an', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '30', '-fps_mode', 'cfr', 'out/visuals-v3-framingfix.mp4'], cwd=P, stdout=log, stderr=subprocess.STDOUT, check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'out/visuals-v3-framingfix.mp4', '-i', 'public/mixed-v3.wav', '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '../final_remotion_tripo_workflow_v3.mp4'], cwd=P, check=True)
record = {'reason': 'Moving Takosan foot touched lower viewport edge; add 10% camera margin in all three matching views.', 'cameraZoom': 0.90, 'replacedFrameRangesEndExclusive': ranges, 'baseSha256': hashlib.sha256(base.read_bytes()).hexdigest(), 'expectedFrames': m['composition']['durationInFrames'], 'encoding': 'libx264 CRF16 yuv420p, 30fps; AAC from unchanged source mix'}
(P.parent / 'framing_repair_v3.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
print('Final MP4 updated; audit again.', flush=True)
