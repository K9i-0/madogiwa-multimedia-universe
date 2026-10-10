from pathlib import Path
import subprocess,json,hashlib,os
P=Path(__file__).resolve().parent;root=P.parents[2]
sources={'tribe':root/'03_SCRIPTS/74_yhk_jungle_available/final_remotion_documentary.mp4','space':root/'03_SCRIPTS/64_madogiwa_super_try_space/final_remotion_cm.mp4','clone':root/'03_SCRIPTS/80_sobaya_clone_lab/final_remotion_clone_lab_skin.mp4','capture':root/'03_SCRIPTS/84_madogiwa_tribe_origin/final_remotion_story.mp4'}
# Full source frames were inspected in out/*_sheet.jpg. Crop only encoded subtitles/letterbox.
stills={'forest':('tribe',5),'sobaya':('capture',30),'beer':('capture',30),'window':('tribe',72),'jungle':('tribe',26),'ritual':('tribe',90),'waiting':('tribe',110),'offering':('tribe',52),'captives':('capture',18),'capture':('capture',30),'earth':('space',6),'approach':('space',14),'swim':('space',17),'spacebeer':('space',22),'lab':('clone',18),'tanks':('clone',18),'researcher':('clone',22),'pursuit':('clone',29),'badge':('tribe',138),'office':('capture',10)}
records=[]
for name,(key,t) in stills.items():
 target=P/'public'/f'{name}.jpg'
 crop='crop=iw:ih*0.82:0:ih*0.05'
 if name=='window':crop='crop=iw:ih*0.72:0:ih*0.05'
 if name=='sobaya':crop='crop=iw*0.38:ih*0.82:iw*0.32:ih*0.05'
 if name=='beer':crop='crop=iw*0.36:ih*0.55:iw*0.32:ih*0.32'
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(sources[key]),'-frames:v','1','-vf',crop+',scale=1200:-2',str(target)],check=True)
 records.append({'asset':target.name,'source':str(sources[key].relative_to(root)),'sourceSeconds':t,'filter':crop,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
for name,key,start,duration in [('jungle_motion','tribe',26,6),('swim_motion','space',14,6),('capture_motion','capture',26,7),('lab_motion','clone',17,6)]:
 target=P/'public'/f'{name}.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(start),'-i',str(sources[key]),'-t',str(duration),'-an','-vf','crop=iw:ih*0.82:0:ih*0.05,fps=30','-c:v','libx264','-crf','18','-preset','fast',str(target)],check=True)
 records.append({'asset':target.name,'source':str(sources[key].relative_to(root)),'sourceSeconds':start,'durationSeconds':duration,'audio':'muted archival excerpt under narration','sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
forest=root/'03_SCRIPTS/74_yhk_jungle_available/backgrounds/intro_island.png'
import shutil
shutil.copy2(forest,P/'public/forest.png')
records.append({'asset':'forest.png','source':str(forest.relative_to(root)),'sha256':hashlib.sha256(forest.read_bytes()).hexdigest()})
old=root/'03_SCRIPTS/youtube_aeron_chua_explainer_20261008/remotion/public'
for f in old.glob('*.png'):
 if f.name.startswith(('zunda_','metan_')):
  target=P/'public'/f.name
  if not target.exists():os.link(f,target)
(P.parent/'asset_sources.json').write_text(json.dumps({'sources':records,'portraits':{'author':'坂本アヒル','provenance':'03_SCRIPTS/youtube_explainer_pilot_20261008/asset_sources.json'},'music':'Original procedural ambient score; mix_audio.py'},ensure_ascii=False,indent=2)+'\n')

# Adopted generated illustrations, retained as production inputs.
for f in (P.parent/"inputs").glob("*_v3.png"):
 shutil.copy2(f,P/"public"/f.name)
