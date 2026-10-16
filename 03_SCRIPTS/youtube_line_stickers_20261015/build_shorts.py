#!/usr/bin/env python3
"""Render the adopted excerpt with the shared Shorts layout and ending CTA."""
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
OUT = REMOTION / 'out'
MANIFEST = EPISODE / 'shorts-manifest.json'


def run(args, cwd=REPO):
    subprocess.run([str(a) for a in args], cwd=cwd, check=True)


def sha256(path):
    with open(path, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy-layout', action='store_true', help='Render the superseded horizontal-in-portrait layout')
    parser.add_argument('--skip-clean-render', action='store_true')
    parser.add_argument('--still', type=int)
    args = parser.parse_args()
    if not args.legacy_layout:
        run(['python3', EPISODE / 'build_portrait_trial.py'])
        shutil.copy2(OUT / 'shorts_portrait_trial.mp4', EPISODE / 'final_remotion_shorts_9x16.mp4')
        return
    m = json.loads(MANIFEST.read_text())
    source = REPO / m['audioSource']
    frames, fps = m['durationInFrames'], m['fps']
    if sha256(source) != m['sourceSha256']:
        raise SystemExit('The approved source hash has changed.')
    OUT.mkdir(exist_ok=True)
    clean = REPO / m['clips'][0]['source']
    if not args.skip_clean_render:
        run(['npx', 'remotion', 'render', 'src/index.ts', 'Explainer', clean,
             '--props', json.dumps({'hideCaptions': True, 'silentPreview': True}),
             '--frames', f"0-{m['sourceRange']['endFrameExclusive'] - 1}", '--muted', '--concurrency=6',
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
    if 'audioFadeOutStartFrame' in m:
        start, end = m['audioFadeOutStartFrame'] / fps, m['audioTrimEndFrame'] / fps
        audio = OUT / 'shorts_extended_audio.wav'
        run(['ffmpeg', '-v', 'error', '-i', source, '-vn', '-af',
             f'atrim=end={end},afade=t=out:st={start}:d={end-start},apad,atrim=end={frames/fps}',
             '-c:a', 'pcm_s16le', '-y', audio])
        run(['ffmpeg', '-v', 'error', '-i', silent, '-i', audio,
             '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac',
             '-b:a', '192k', '-movflags', '+faststart', '-y', output])
        print(output)
        return
    # Stop before the next AAC packet: keep the original packets while avoiding
    # an audio tail beyond the final video frame (48 kHz AAC uses 1024 samples).
    audio_cutoff = (int(frames / fps * 48000) // 1024 * 1024 - 1) / 48000
    run(['ffmpeg', '-v', 'error', '-i', silent, '-i', source,
         '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy',
         '-t', str(audio_cutoff), '-movflags', '+faststart', '-y', output])
    print(output)


if __name__ == '__main__':
    main()
