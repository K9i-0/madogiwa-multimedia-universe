"""v11 media from the 2026-10-30 iPhone 17 Pro simulator capture.

simctl records the landscape app as a portrait stream, so each clip is rotated
back and the Dynamic Island strip on both short edges is cropped before scaling.
"""
from pathlib import Path
import subprocess
P=Path(__file__).resolve().parent
view='transpose=2,crop=iw-360:ih:180:0,fps=30,scale=1280:-2:flags=lanczos'
for raw,target,start,duration in [('gallery_model','gallery_model',.5,10),('gallery_stage','gallery_stage',2,10),('odatetsu','game_odatetsu',4,16),('sobaya','game_sobaya',4,16),('night','game_night',4,16),('closeup','game_odatetsu_closeup',4,12),('widget','widget',1,8)]:
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(start),'-i',str(P/'out'/f'{raw}_v11_raw.mov'),'-t',str(duration),'-vf',view,'-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(P/'public'/f'{target}_v11.mp4')],check=True)
probe=subprocess.check_output(['ffprobe','-v','error','-select_streams','v','-show_entries','stream=width,height','-of','csv=p=0',str(P/'public/game_odatetsu_closeup_v11.mp4')],text=True).strip().split(',')
w,h=map(int,probe)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'public/game_odatetsu_closeup_v11.mp4'),'-vf',f'crop={int(w*.36)}:{int(h*.92)}:{int(w*.32)}:{int(h*.04)}','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(P/'public/model_detail_v11.mp4')],check=True)
# Model-only crop of the gallery viewer, shown beside the turnaround sheet.
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'public/gallery_model_v11.mp4'),'-vf','crop=380:356:270:184','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(P/'public/model_turn_v11.mp4')],check=True)
