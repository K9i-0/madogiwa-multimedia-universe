"""Restore the local v12 finishing capture into the v11 filenames used by the adopted edit.
Source: 2026-10-30 iPhone 18 Pro / iOS 27.0, landscape, game 08b2161.
Dart MCP debug launch; Marionette demo/gallery and real Widget tap. No game source edits.
"""
from pathlib import Path
import subprocess
P=Path(__file__).resolve().parent
for raw,target,start,duration in [('odatetsu','game_odatetsu',4,16),('sobaya','game_sobaya',4,16),('night','game_night',4,16),('closeup2','game_odatetsu_closeup',4,12),('gallery_model','gallery_model',1,10),('gallery_stage','gallery_stage',1,10),('widget','widget',1.2,8)]:
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(start),'-i',str(P/'out'/f'{raw}_v12_raw.mov'),'-t',str(duration),'-vf','fps=30,scale=1280:-2:flags=lanczos','-an','-c:v','libx264','-crf','18',str(P/'public'/f'{target}_v11.mp4')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'public/gallery_model_v11.mp4'),'-vf','crop=400:310:290:150','-an','-c:v','libx264','-crf','18',str(P/'public/model_turn_v11.mp4')],check=True)
