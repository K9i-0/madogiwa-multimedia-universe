"""Render a review candidate; the adopted MP4 is never overwritten implicitly."""
from pathlib import Path
import argparse
import subprocess
import sys

P = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('output_path', nargs='?', help='MP4 path, relative to the Remotion project')
parser.add_argument('--output', help='MP4 path, relative to the Remotion project')
parser.add_argument('--skip-mix', action='store_true', help='Reuse the existing mixed.wav')
parser.add_argument('--concurrency', type=int, default=4)
args = parser.parse_args()
if args.output and args.output_path:
    parser.error('Supply either a positional output or --output, not both')
output = Path(args.output or args.output_path or 'out/review_v9_01.mp4')
if not output.is_absolute():
    output = P / output
output.parent.mkdir(parents=True, exist_ok=True)
visuals = P / 'out' / f'{output.stem}_visuals.mp4'
subprocess.run([sys.executable, str(P / 'validate_timeline.py')], check=True)
if not args.skip_mix:
    subprocess.run([sys.executable, str(P / 'mix_audio.py')], check=True)
subprocess.run(['npx', 'remotion', 'render', 'src/index.ts', 'Explainer', str(visuals),
                '--muted', f'--concurrency={args.concurrency}', '--crf=18', '--log=error'], cwd=P, check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(visuals), '-i', str(P / 'public/mixed.wav'),
                '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                '-movflags', '+faststart', str(output)], check=True)
print(output)
