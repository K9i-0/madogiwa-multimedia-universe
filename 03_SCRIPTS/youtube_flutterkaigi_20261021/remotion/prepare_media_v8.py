from pathlib import Path
import subprocess
from PIL import Image
P=Path(__file__).resolve().parent
for raw,target,start,duration in [('gallery_model2','gallery_model',1,12),('gallery_stage','gallery_stage',1,10),('odatetsu','game_odatetsu',2,16),('sobaya','game_sobaya',2,16),('night','game_night',2,16),('closeup_front2','game_odatetsu_closeup',3,12),('widget2','widget',0,8)]:
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(start),'-i',str(P/'out'/f'{raw}_v8_raw.mov'),'-t',str(duration),'-vf','fps=30,scale=1280:-2:flags=lanczos','-an','-c:v','libx264','-crf','18',str(P/'public'/f'{target}_v8.mp4')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'public/game_odatetsu_closeup_v8.mp4'),'-vf','crop=450:530:415:30','-an','-c:v','libx264','-crf','18',str(P/'public/model_detail_v8.mp4')],check=True)
im=Image.open(P/'public/selection_v8.png');w,h=im.size
im.crop((int(w*.55),int(h*.29),int(w*.90),int(h*.72))).save(P/'public/chikuwa_v8.png')
im.crop((int(w*.55),int(h*.29),int(w*.72),int(h*.72))).save(P/'public/chikuwa_single_v8.png')
