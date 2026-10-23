"""Restore Remotion public assets and cut the completed non-video compilation."""
from pathlib import Path
import json,shutil,subprocess
p=Path(__file__).resolve().parent
public=p/'remotion/public';public.mkdir(parents=True,exist_ok=True)
for pattern in ['*.png','voice_*.wav']:
 for f in p.glob(pattern):shutil.copy2(f,public/f.name)
source=p.parent/'25_chikuwa_landing_news/chikuwa_hamamatsu_news_seedance2.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-t',str(json.loads((p/'remotion/src/edit-manifest.json').read_text())['intro']/30),'-c:v','libx264','-crf','18','-c:a','aac',str(public/'anchor_intro.mp4')],check=True)
master=p/'completed_nonvideo_parts.mp4'
if master.exists():
 t=json.loads((p/'remotion/src/edit-manifest.json').read_text());start=0
 for i,k in enumerate(['intro','forest','comparison','interruption'],1):
  subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),'-ss',str(start/30),'-t',str(t[k]/30),'-c:v','libx264','-crf','18','-c:a','aac','-movflags','+faststart',str(p/f'part_{i:02}_{k}.mp4')],check=True);start+=t[k]
