"""Render the first-minute YouTube teaser; preserve the adopted v11 source."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
EPISODE = ROOT.parent
FPS = 30
CUT = 1707  # 56.9s: v008 ends at frame 1698; v009 starts at 1708.
CARD = 105

def run(args):
    subprocess.run(args, cwd=ROOT, check=True)

run(['npx', 'remotion', 'render', 'src/teaser-entry.tsx', 'TeaserEndCard',
     'out/teaser_endcard.mp4', '--codec=h264', '--crf=18', '--concurrency=4'])
# Only the silent gap after v008 fades; v009 is never included.
filters = (
    f'[0:v]trim=end_frame={CUT},setpts=PTS-STARTPTS,'
    'fade=t=out:st=56.633333333:d=0.233333333:color=white[v0];'
    '[0:a]atrim=end=56.9,asetpts=PTS-STARTPTS,'
    'afade=t=out:st=56.633333333:d=0.233333333[a0];'
    '[1:v]setpts=PTS-STARTPTS[v1];'
    'anullsrc=r=48000:cl=stereo,atrim=duration=3.5[a1];'
    '[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]'
)
run(['ffmpeg', '-hide_banner', '-y', '-i', str(EPISODE / 'final_remotion_ai_video_workflow_v11.mp4'),
     '-i', 'out/teaser_endcard.mp4', '-filter_complex', filters, '-map', '[v]', '-map', '[a]',
     '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
     '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart',
     str(EPISODE / 'final_remotion_youtube_teaser_v1.mp4')])
