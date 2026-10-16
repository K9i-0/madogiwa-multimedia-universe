#!/usr/bin/env python3
"""Render the adopted v7 cold open with the shared Shorts layout and original AAC."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess

EPISODE = Path(__file__).resolve().parent
REPO = EPISODE.parents[1]
SHARED = REPO / '03_SCRIPTS/shorts_queue_20261011/remotion'
REMOTION = EPISODE / 'remotion'
SOURCE = EPISODE / 'final_remotion_line_stickers_v7.mp4'
OUT = REMOTION / 'out'
MANIFEST = EPISODE / 'shorts-manifest.json'


def run(args, cwd=REPO):
    subprocess.run([str(a) for a in args], cwd=cwd, check=True)


def sha256(path):
    with open(path, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip-clean-render', action='store_true')
    parser.add_argument('--still', type=int)
    args = parser.parse_args()
    m = json.loads(MANIFEST.read_text())
    frames, fps = m['durationInFrames'], m['fps']
    if sha256(SOURCE) != m['sourceSha256']:
        raise SystemExit('The approved v7 source hash has changed.')
    OUT.mkdir(exist_ok=True)
    clean = REPO / m['clips'][0]['source']
    if not args.skip_clean_render:
        run(['npx', 'remotion', 'render', 'src/index.ts', 'Explainer', clean,
             '--props', json.dumps({'hideCaptions': True, 'silentPreview': True}),
             '--frames', f'0-{frames - 1}', '--muted', '--concurrency=6',
             '--crf=18', '--log=error'], REMOTION)
    if not clean.is_file():
        raise SystemExit(f'Missing subtitle-free render: {clean}')
    target = SHARED / 'public' / m['clips'][0]['file']
    target.parent.mkdir(exist_ok=True)
    if target.exists():
        target.unlink()
    try:
        os.link(clean, target)
    except OSError:
        shutil.copy2(clean, target)
    if args.still is not None:
        run(['npx', 'remotion', 'still', 'src/index.tsx', 'Shorts',
             OUT / 'shorts-audit' / f'still-{args.still:04d}.png',
             '--props', MANIFEST, '--frame', args.still, '--log=error'], SHARED)
        return
    silent = OUT / 'shorts_9x16_silent.mp4'
    run(['npx', 'remotion', 'render', 'src/index.tsx', 'Shorts', silent,
         '--props', MANIFEST, '--muted', '--concurrency=4',
         '--crf=18', '--log=error'], SHARED)
    output = EPISODE / 'final_remotion_shorts_9x16.mp4'
    # Stop before the next AAC packet: keep the original packets while avoiding
    # an audio tail beyond the final video frame (48 kHz AAC uses 1024 samples).
    audio_cutoff = (int(frames / fps * 48000) // 1024 * 1024 - 1) / 48000
    run(['ffmpeg', '-v', 'error', '-i', silent, '-i', SOURCE,
         '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy',
         '-t', str(audio_cutoff), '-movflags', '+faststart', '-y', output])
    print(output)


if __name__ == '__main__':
    main()
