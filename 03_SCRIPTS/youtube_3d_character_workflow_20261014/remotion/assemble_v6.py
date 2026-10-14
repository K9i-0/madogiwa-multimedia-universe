"""Reuse the unchanged v5 prefix and join the re-rendered v6 ending at an IDR."""
from pathlib import Path
import hashlib
import json
import subprocess

P = Path(__file__).resolve().parent
CUT = 19429  # v5 IDR immediately before the changed chapter 8 progress indicator.
FPS = 30
old = json.loads((P / 'src/edit-manifest-v5.json').read_text())
new = json.loads((P / 'src/edit-manifest-v6.json').read_text())
assert CUT < old['endingStartFrame'] == new['endingStartFrame']
old_rows = {d['id']: d for d in old['dialogue']}
for d in new['dialogue']:
    if d['startFrame'] < new['endingStartFrame']:
        for key in ('text', 'who', 'startFrame', 'durationInFrames', 'audioSha256', 'captionSegments', 'view', 'envelope'):
            assert d[key] == old_rows[d['id']][key], (d['id'], key)

def run(args):
    subprocess.run(args, cwd=P, check=True)

def probe(path):
    return json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_streams', '-of', 'json', str(path)
    ]))['streams'][0]

source = P / 'out/visuals-v5.mp4'
tail = P / 'out/tail-v6.mp4'
keyframes = json.loads(subprocess.check_output([
    'ffprobe', '-v', 'error', '-skip_frame', 'nokey', '-select_streams', 'v:0',
    '-show_frames', '-show_entries', 'frame=pts_time', '-of', 'json', str(source)
]))['frames']
assert CUT in [round(float(f['pts_time']) * FPS) for f in keyframes]
assert int(probe(tail)['nb_frames']) == new['composition']['durationInFrames'] - CUT
run(['ffmpeg', '-v', 'error', '-y', '-i', str(source), '-map', '0:v:0', '-c', 'copy',
     '-f', 'segment', '-segment_times', str(CUT / FPS), '-reset_timestamps', '1',
     'out/v5_split_%02d.mp4'])
prefix = P / 'out/v5_split_00.mp4'
assert int(probe(prefix)['nb_frames']) == CUT
for key in ('codec_name', 'profile', 'level', 'pix_fmt', 'width', 'height', 'time_base', 'r_frame_rate'):
    assert probe(prefix)[key] == probe(tail)[key], key
# Segment muxing may shift the initial PTS for B-frames. The explicit duration
# keeps the next segment at exactly CUT/FPS instead of the padded container end.
concat = P / 'out/v6_concat.txt'
concat.write_text(f"file 'v5_split_00.mp4'\nduration {CUT / FPS:.12f}\nfile 'tail-v6.mp4'\n")
run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(concat),
     '-map', '0:v:0', '-c', 'copy', '-movflags', '+faststart', 'out/visuals-v6.mp4'])
assert int(probe(P / 'out/visuals-v6.mp4')['nb_frames']) == new['composition']['durationInFrames']
run(['ffmpeg', '-v', 'error', '-y', '-i', 'out/visuals-v6.mp4', '-i', 'public/mixed-v6.wav',
     '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
     '-movflags', '+faststart', '../final_remotion_tripo_workflow_v6.mp4'])

def decoded_hashes(path, frames):
    output = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:v:0',
                                      '-frames:v', str(frames), '-f', 'framemd5', '-'])
    return [line.rsplit(b',', 1)[-1].strip() for line in output.splitlines() if not line.startswith(b'#')]

final = P.parent / 'final_remotion_tripo_workflow_v6.mp4'
before = decoded_hashes(source, CUT)
after = decoded_hashes(final, CUT)
assert len(before) == len(after) == CUT and before == after
times = json.loads(subprocess.check_output([
    'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_frames',
    '-show_entries', 'frame=best_effort_timestamp_time', '-of', 'json', str(final)
]))['frames']
assert len(times) == new['composition']['durationInFrames']
assert all(abs(float(f['best_effort_timestamp_time']) - i / FPS) < 0.00002 for i, f in enumerate(times))
record = {'source': 'final_remotion_tripo_workflow_v5.mp4', 'sourceVisuals': 'remotion/out/visuals-v5.mp4',
          'sourceVisualsSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'reusedFrames': CUT, 'renderedRange': [CUT, new['composition']['durationInFrames'] - 1],
          'prefixAllDecodedFrameHashesEqual': True,
          'allPresentationTimestampsOn30FpsGrid': True,
          'reason': 'Chapter 8 progress, new comments, ending timing and fade are re-rendered; earlier pixels are unchanged.'}
(P.parent / 'render_reuse_v6.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(record, ensure_ascii=False, indent=2))
