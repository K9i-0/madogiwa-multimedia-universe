"""Restore source song at unchanged timing and mix the Wan crowd bed."""
from pathlib import Path
import subprocess
P = Path(__file__).resolve().parent
subprocess.run(['ffmpeg','-y','-v','error','-i',str(P/'local/wan3_part01_480p.mp4'),'-i',str(P/'local/original_audio.wav'),'-filter_complex','[0:v]scale=960:720:flags=lanczos,setsar=1[v];[0:a]volume=0.22[crowd];[1:a]volume=0.8[song];[song][crowd]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.97:level=0:latency=1[a]','-map','[v]','-map','[a]','-t','15','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-movflags','+faststart',str(P/'final_gyunrevo_part01_720p.mp4')], check=True)
