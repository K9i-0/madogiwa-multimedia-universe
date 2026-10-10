from pathlib import Path
import shutil,json,subprocess,hashlib
root=Path(__file__).resolve().parents[2];ep=Path(__file__).resolve().parent;public=ep/'remotion/public';public.mkdir(exist_ok=True)
records=[]
def copy(src,name):
 src=root/src;dst=public/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);records.append(dict(file=name,source=str(src.relative_to(root)),sha256=hashlib.sha256(src.read_bytes()).hexdigest()))
pack=root/'03_SCRIPTS/00_TEMPLATES/characters/commentary_duo_v1'
for f in pack.glob('*.png'):copy(str(f.relative_to(root)),'sprites/'+f.name)
copy('03_SCRIPTS/00_TEMPLATES/characters/character_sobaya_basic_sheet.png','sobaya_sheet.png')
for num,ext in [('03','png'),('04','png'),('05','png'),('06','jpeg')]:copy(f'01_WORLD/story_timeline/episode_{num}.{ext}',f'episode_{num}.{ext}')
for f in ['intro.mp3','main.wav','unity.mp3']:copy('03_SCRIPTS/youtube_aeron_chua_explainer_20261008/remotion/public/'+f,f)
sources={'battery':'03_SCRIPTS/40_sobaya_beer_battery/final_video.mp4','taxi':'03_SCRIPTS/82_last_train_police_taxi/final_remotion_exterior_punchline.mp4','quake':'03_SCRIPTS/76_sobaya_yakisoba_quake/final_remotion_revision02.mp4'}
stills={'battery_before':('battery',9),'battery_after':('battery',26),'taxi_before':('taxi',8),'taxi_hit':('taxi',17),'taxi_after':('taxi',25),'quake_before':('quake',2),'quake_shake':('quake',14),'quake_after':('quake',24),'quake_damage':('quake',25.7)}
for name,(key,t) in stills.items():
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(root/sources[key]),'-frames:v','1',str(public/(name+'.jpg'))],check=True)
 records.append(dict(file=name+'.jpg',source=sources[key],sourceFrame=round(t*30)))
clips=[dict(id='battery',afterLine=15,source='battery',sourceStartFrame=510,durationInFrames=285,label='第40話「そば屋、電池切れ」'),dict(id='taxi',afterLine=19,source='taxi',sourceStartFrame=360,durationInFrames=199,label='第82話「終電とタクシー」'),dict(id='police',afterLine=21,source='taxi',sourceStartFrame=733,durationInFrames=63,label='第82話「終電とタクシー」'),dict(id='shake',afterLine=23,source='quake',sourceStartFrame=390,durationInFrames=90,label='第76話「美味しい焼きそば」'),dict(id='rescue',afterLine=24,source='quake',sourceStartFrame=480,durationInFrames=270,label='第76話「美味しい焼きそば」')]
for c in clips:
 source=root/sources[c['source']];c['source']=str(source.relative_to(root));c['file']='clip_'+c['id']+'.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(c['sourceStartFrame']/30),'-i',str(source),'-t',str(c['durationInFrames']/30),'-r','30','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-ar','48000',str(public/c['file'])],check=True)
 c['sourceSha256']=hashlib.sha256(source.read_bytes()).hexdigest()
(ep/'assets.json').write_text(json.dumps({'files':records,'clips':clips,'note':'第76話は採用台本のやめ太郎による注ぎと一致する修正版2を引用。後発のとーくん版とは区別。既存映像の旧缶デザインはそのまま引用。'},ensure_ascii=False,indent=2))
