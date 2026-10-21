"""Derive editorial crops without changing the adopted original footage."""
from pathlib import Path
import subprocess
P=Path(__file__).resolve().parent
for source,target,vf,seconds in [
 ('public/tripo_excerpt.mp4','public/tripo_detail_v5.mp4','crop=1000:490:140:75',15),
 ('public/game_odatetsu_closeup_v4.mp4','public/model_detail_v5.mp4','crop=450:560:415:40',12),
 ('out/widget_v5_raw.mov','public/widget_v5.mp4','fps=30,scale=1280:-2',8),
]:
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/source),'-t',str(seconds),'-vf',vf,'-an','-c:v','libx264','-crf','18',str(P/target)],check=True)
