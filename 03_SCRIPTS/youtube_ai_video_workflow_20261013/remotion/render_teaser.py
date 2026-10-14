"""Render the first-minute YouTube teaser; preserve the adopted v11 source."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
EPISODE = ROOT.parent
FPS = 30
CUT = 1707  # 56.9s: v008 ends at frame 1698; v009 starts at 1708.

def run(args):
    subprocess.run(args, cwd=ROOT, check=True)

# Only the silent gap after v008 fades; v009 is never included.
filters = (
    f'[0:v]trim=end_frame={CUT},setpts=PTS-STARTPTS,'
    'fade=t=out:st=56.633333333:d=0.233333333:color=white[v];'
    '[0:a]atrim=end=56.9,asetpts=PTS-STARTPTS,'
    'afade=t=out:st=56.633333333:d=0.233333333[a]'

)
run(['ffmpeg', '-hide_banner', '-y', '-i', str(EPISODE / 'final_remotion_ai_video_workflow_v11.mp4'),
     '-filter_complex', filters, '-map', '[v]', '-map', '[a]',
     '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
     '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart',
     str(EPISODE / 'final_remotion_youtube_teaser_v2.mp4')])
