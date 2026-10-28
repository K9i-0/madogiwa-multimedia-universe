#!/usr/bin/env python3
"""Export adopted landscape and Shorts with the original effects-only mix."""
from pathlib import Path
import json
import subprocess

P = Path(__file__).resolve().parent
FRAMES = 846
FPS = 30
prior = json.loads((P / 'edit_manifest_v8b.json').read_text())
audio_filter = (
    f"aresample=48000,atrim=end_sample={FRAMES * 1600},asetpts=PTS-STARTPTS,"
    f"volume={prior['sfx_gain_db']}dB,"
    f"afade=t=in:st={234 / FPS}:d={2 / FPS},"
    f"afade=t=out:st={837 / FPS}:d={9 / FPS}:curve=hsin,"
    "alimiter=limit=0.891251:level=0:latency=1"
)
audio = P / 'generated/sfx_only_28p2.m4a'
subprocess.run([
    'ffmpeg', '-v', 'error', '-i', str(P / 'generated/assembled_v8b_lossless.mkv'),
    '-map', '0:a:0', '-af', audio_filter, '-c:a', 'aac', '-b:a', '256k',
    '-ar', '48000', '-ac', '2', '-y', str(audio)
], check=True)
outputs = []
for source, name in [
    ('final_sobaya_brewery_28p2_music_finish_720p.mp4', 'final_remotion_no_bgm_16x9.mp4'),
    ('final_remotion_shorts_9x16.mp4', 'final_remotion_no_bgm_9x16.mp4'),
]:
    output = P / name
    subprocess.run([
        'ffmpeg', '-v', 'error', '-i', str(P / source), '-i', str(audio),
        '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy',
        '-t', str(FRAMES / FPS), '-movflags', '+faststart', '-y', str(output)
    ], check=True)
    outputs.append({'source': source, 'output': name})
    print(f'READY: {output}', flush=True)
(P / 'edit_manifest_no_bgm.json').write_text(json.dumps({
    'title': 'THE SOBAYA', 'fps': FPS, 'frames': FRAMES,
    'duration': FRAMES / FPS, 'outputs': outputs,
    'audio_source': 'generated/assembled_v8b_lossless.mkv',
    'audio_filter': audio_filter, 'bgm': None,
    'note': 'Effects-only branch of approved mix; first 234 frames muted to suppress generated music. Video streams copied without re-encoding. No publication changes.',
}, ensure_ascii=False, indent=2) + '\n')
