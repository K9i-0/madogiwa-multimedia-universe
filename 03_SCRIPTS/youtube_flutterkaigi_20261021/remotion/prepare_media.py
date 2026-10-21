from pathlib import Path
import subprocess,json
P=Path(__file__).resolve().parent
for raw,name in [('odatetsu','game_odatetsu'),('sobaya','game_sobaya'),('night','game_night')]:
 subprocess.run(['ffmpeg','-v','error','-y','-ss','5','-i',str(P/'out'/f'{raw}_raw.mov'),'-t','18','-an','-vf','fps=30,scale=1280:-2:flags=lanczos','-c:v','libx264','-crf','18',str(P/'public'/f'{name}.mp4')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'public/selection.png'),'-vf','crop=iw*0.66:ih*0.51:iw*0.30:ih*0.22','-frames:v','1',str(P/'public/chikuwa.png')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'public/chikuwa.png'),'-vf','crop=iw/2:ih:0:0','-frames:v','1',str(P/'public/chikuwa_single.png')],check=True)
