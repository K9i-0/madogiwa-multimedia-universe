from pathlib import Path
import shutil,json,subprocess,hashlib
root=Path(__file__).resolve().parents[2];ep=Path(__file__).resolve().parent;public=ep/'remotion/public';public.mkdir(exist_ok=True)
records=[]
def copy(src,name):
 src=root/src;dst=public/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);records.append(dict(file=name,source=str(src.relative_to(root)),sha256=hashlib.sha256(src.read_bytes()).hexdigest()))
for f in (root/'03_SCRIPTS/00_TEMPLATES/characters/commentary_duo_v1').glob('*.png'):copy(str(f.relative_to(root)),'sprites/'+f.name)
copy('03_SCRIPTS/00_TEMPLATES/characters/character_sobaya_basic_sheet.png','sobaya_sheet.png')
for f in ['intro.mp3','main.wav','unity.mp3']:copy('03_SCRIPTS/youtube_aeron_chua_explainer_20261008/remotion/public/'+f,f)
sources={'excel':'03_SCRIPTS/59_sobaya_professional_window_side/final_remotion_documentary_irodori_16x9.mp4','catch':'03_SCRIPTS/34_sobaya_frozen_beer_catch/sobaya_beer_only_15s.mp4','bar':'03_SCRIPTS/48_balcony_bar_timelapse/wan3_episode48_balcony_bar_timelapse_prime_seed300049_480p.mp4','quake':'03_SCRIPTS/76_sobaya_yakisoba_quake/final_remotion_revision02.mp4','proxy':'03_SCRIPTS/53_sobaya_proxy_worker_news/final_remotion_news.mp4'}
stills={'excel_before':('excel',7),'excel_after':('excel',18),'catch_before':('catch',1),'catch_after':('catch',12),'bar_before':('bar',1),'bar_middle':('bar',11),'bar_after':('bar',29),'quake_before':('quake',2),'quake_shake':('quake',14),'quake_after':('quake',24),'quake_damage':('quake',25.7),'proxy_before':('proxy',12),'proxy_home':('proxy',19),'proxy_after':('proxy',28)}
for name,(key,t) in stills.items():
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(root/sources[key]),'-frames:v','1',str(public/(name+'.jpg'))],check=True)
 records.append(dict(file=name+'.jpg',source=sources[key],sourceFrame=round(t*30)))
clips=json.loads((ep/'clip_plan.json').read_text())
for c in clips:
 c['source']=sources[c['sourceKey']];source=root/c['source']
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(c['sourceStartFrame']/30),'-i',str(source),'-t',str(c['durationInFrames']/30),'-r','30','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-ar','48000',str(public/c['file'])],check=True)
 c['sourceSha256']=hashlib.sha256(source.read_bytes()).hexdigest()
(ep/'assets.json').write_text(json.dumps({'files':records,'clips':clips,'note':'48は撤去工程を改善したPrime版。76はやめ太郎が注ぐrevision02。既存の缶・衣装は引用のまま。'},ensure_ascii=False,indent=2))
