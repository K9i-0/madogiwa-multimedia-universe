from pathlib import Path
import subprocess
p=Path(__file__).resolve().parent
out=p.parent/'final_remotion_saturn_lyrics_720p.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(p/'out/lyrics_silent.mp4'),'-i',str(p/'public/input.mp4'),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(out)],check=True)
subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(out),'-vf','fps=1/3,scale=640:360,tile=3x3','-frames:v','1',str(p/'out/contact.jpg')],check=True)
print(out)
