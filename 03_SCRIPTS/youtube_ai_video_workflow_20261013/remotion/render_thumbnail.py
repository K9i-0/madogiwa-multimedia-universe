"""Build the thumbnail from original video frames and canonical transparent sprites."""
from pathlib import Path
import subprocess
P=Path(__file__).resolve().parent
for name,seconds in [('anchor',3),('arrest',9),('home',20),('office',16)]:
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(seconds),'-i',str(P/'public/news_raw.mp4'),'-frames:v','1',str(P/f'public/thumbnail_{name}.png')],check=True)
subprocess.run(['npx','remotion','still','src/thumbnail-entry.tsx','Thumbnail','../thumbnails/thumbnail_text_v5.png','--scale=2','--log=error'],cwd=P,check=True)
