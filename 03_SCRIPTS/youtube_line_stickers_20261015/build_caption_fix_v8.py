#!/usr/bin/env python3
"""Render the caption-only correction, keeping the adopted v7 AAC packets."""
from pathlib import Path
import argparse
import hashlib
import subprocess

EPISODE = Path(__file__).resolve().parent
REMOTION = EPISODE / 'remotion'
SOURCE = EPISODE / 'final_remotion_line_stickers_v7.mp4'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('target', choices=['main', 'x'])
    parser.add_argument('--mux-only', action='store_true')
    args = parser.parse_args()
    with SOURCE.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == '7d9be5e4b37384300578140e3d58a55a5b061d6eb9e95dd895f93341cdfa6ab9'
    short = args.target == 'x'
    visual = REMOTION / 'out' / ('x_opening_16x9_visuals.mp4' if short else 'final_remotion_line_stickers_v8_visuals.mp4')
    output = EPISODE / ('final_remotion_x_opening_16x9.mp4' if short else 'final_remotion_line_stickers_v8.mp4')
    if not args.mux_only:
        subprocess.run(['npx', 'remotion', 'render', 'src/index.ts', 'Explainer', str(visual),
                        *(['--frames=0-1185'] if short else []), '--muted',
                        f'--concurrency={2 if short else 6}', '--crf=18', '--log=error'],
                       cwd=REMOTION, check=True)
    # Same complete AAC packet prefix as the 1186-frame vertical Short.
    cutoff = (int(1186 / 30 * 48000) // 1024 * 1024 - 1) / 48000
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(visual), '-i', str(SOURCE),
                    '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy',
                    *(['-t', str(cutoff)] if short else []),
                    '-movflags', '+faststart', '-y', str(output)], check=True)
    print(output)


if __name__ == '__main__':
    main()
