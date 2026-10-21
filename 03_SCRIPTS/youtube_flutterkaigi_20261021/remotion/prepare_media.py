from pathlib import Path
import subprocess
from PIL import Image
p=Path(__file__).resolve().parent
for raw,name,start,duration in [('odatetsu','game_odatetsu',3,18),('sobaya','game_sobaya',3,18),('night','game_night',3,18),('closeup','game_odatetsu_closeup',1,12)]:
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(start),'-i',str(p/'out'/f'{raw}_v4_raw.mov'),'-t',str(duration),'-an','-vf','fps=30,scale=1280:-2:flags=lanczos','-c:v','libx264','-crf','18',str(p/'public'/f'{name}_v4.mp4')],check=True)
im=Image.open(p/'public/selection_v4.png');w,h=im.size
im.crop((int(w*.55),int(h*.30),int(w*.97),int(h*.82))).save(p/'public/chikuwa_v4.png')
im.crop((int(w*.55),int(h*.30),int(w*.76),int(h*.82))).save(p/'public/chikuwa_single_v4.png')
