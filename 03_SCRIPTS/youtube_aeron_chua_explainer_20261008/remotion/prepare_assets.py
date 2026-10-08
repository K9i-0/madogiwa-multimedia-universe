from pathlib import Path
import os,shutil,subprocess
p=Path(__file__).resolve().parent;base=p.parents[1];pilot=base/'youtube_explainer_pilot_20261008/remotion/public'
(p/'public').mkdir(exist_ok=True);(p/'out').mkdir(exist_ok=True)
for f in pilot.glob('*.png'):shutil.copy2(f,p/'public'/f.name)
for name in ['intro.mp3','main.wav']:shutil.copy2(pilot/name,p/'public'/name)
for src,dest in [(base/'51_aronchia_makers_vlog/wan3_result_seed510030_480p.mp4','diy.mp4'),(base/'chuagostini_20261003/final_remotion_cm_sobaya_blurred.mp4','cm.mp4')]:
 target=p/'public'/dest
 if not target.exists():
  try:os.link(src,target)
  except OSError:shutil.copy2(src,target)
for src,time,dst in [('diy.mp4',10,'workshop.png'),('diy.mp4',26.8,'seated.png'),('cm.mp4',27,'kit.png'),('cm.mp4',18,'kitroom.png')]:
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(time),'-i',str(p/'public'/src),'-frames:v','1',str(p/'public'/dst)],check=True)
