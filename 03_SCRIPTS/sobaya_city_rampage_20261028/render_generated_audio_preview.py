#!/usr/bin/env python3
"""Comparison exports restoring generated audio during the first 7.8 seconds."""
from pathlib import Path
import json
import subprocess

P = Path(__file__).resolve().parent
manifest = json.loads((P / 'edit_manifest_no_bgm.json').read_text())
# Remove only the opening mute/fade; preserve gain, ending fade and limiter.
original_filter = manifest['audio_filter']
audio_filter = ','.join(part for part in original_filter.split(',')
                        if not part.startswith('afade=t=in:'))
assert audio_filter != original_filter
audio = P / 'generated/generated_audio_full_28p2.m4a'
subprocess.run([
    'ffmpeg', '-v', 'error', '-i', str(P / manifest['audio_source']),
    '-map', '0:a:0', '-af', audio_filter, '-c:a', 'aac', '-b:a', '256k',
    '-ar', '48000', '-ac', '2', '-y', str(audio)
], check=True)
outputs = []
for aspect in ['16x9', '9x16']:
    source = P / f'final_remotion_no_bgm_{aspect}.mp4'
    output = P / f'preview_generated_audio_{aspect}.mp4'
    subprocess.run([
        'ffmpeg', '-v', 'error', '-i', str(source), '-i', str(audio),
        '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy',
        '-t', str(manifest['duration']), '-movflags', '+faststart', '-y', str(output)
    ], check=True)
    print(f'READY: {output}', flush=True)
    outputs.append({'source': source.name, 'output': output.name})
(P / 'edit_manifest_generated_audio_preview.json').write_text(json.dumps({
    'outputs': outputs, 'audio_source': manifest['audio_source'],
    'audio_filter': audio_filter, 'frames': manifest['frames'],
    'fps': manifest['fps'], 'duration': manifest['duration'],
    'purpose': 'Comparison only; opening generated audio restored, including generated music. No added BGM. No publication changes.'
}, ensure_ascii=False, indent=2) + '\n')
