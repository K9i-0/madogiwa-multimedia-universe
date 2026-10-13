from pathlib import Path
from PIL import Image
import os,shutil,json,subprocess,hashlib
P=Path(__file__).resolve().parent;R=P.parents[2];S=R/'03_SCRIPTS';T=S/'youtube_aeron_chua_explainer_20261008/remotion/public';records=[]
def link(src,dst):
 src=Path(src);dst=P/'public'/dst
 if not dst.exists():os.link(src,dst)
 records.append({'file':dst.name,'source':str(src.relative_to(R)),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
for who in ['zunda','metan']:
 for f in T.glob(who+'_*.png'):link(f,f.name)
for name in ['intro.mp3','main.wav','unity.mp3']:link(T/name,name)
vids={
'doc.mp4':'59_sobaya_professional_window_side/final_remotion_documentary_irodori_16x9.mp4',
'lab.mp4':'80_sobaya_clone_lab/final_remotion_clone_lab_skin.mp4',
'quake.mp4':'76_sobaya_yakisoba_quake/final_remotion_revision04.mp4',
'underground.mp4':'65_madogiwa_super_try_underground/final_remotion_cm_v4.mp4',
'invasion.mp4':'66_madogiwa_super_try_invasion/final_remotion_cm.mp4',
'mimic.mp4':'58_sobaya_takosan_fukuchan_mimic_chain/final_remotion_mimic_chain.mp4',
'kingdom.mp4':'86_gyungyun_kingdom/final_gyungyun_kingdom_no_yametaro_line_720p.mp4',
'bar.mp4':'48_balcony_bar_timelapse/wan3_balcony_bar_prime_seed300049_480p.mp4'}
for dst,src in list(vids.items()):
 if not (S/src).exists():
  if dst=='bar.mp4':
   matches=list((S/'48_balcony_bar_timelapse').glob('*prime*.mp4'))
   print('bar candidates',matches)
   if matches:src=str(matches[0].relative_to(S));vids[dst]=src
  else:raise FileNotFoundError(src)
 link(S/src,dst)
for name,file in [('sobaya','Sobaya.jpg'),('fukugyun','Fukuchan.jpg'),('tokun','Tokun.jpg'),('yotan','Yotan.jpg'),('yametaro','Yametaro.jpg'),('okayaman','Okayaman.jpg'),('yumemin','Yumemin.jpg')]:link(R/'02_CHARACTERS'/file,name+'.jpg')
# Neutral pose from the canonical toy-diorama sheet; keep the source image untouched.
src=S/'00_TEMPLATES/characters/character_takosan_basic_sheet.png';im=Image.open(src);w,h=im.size
im.crop((int(w*.032),int(h*.145),int(w*.237),int(h*.536))).save(P/'public/takosan.png')
records.append({'file':'takosan.png','source':str(src.relative_to(R)),'cropFraction':[.032,.145,.237,.536]})
for n in [1,3,4,7,8,9,10,11,13,14,15]:
 matches=list((R/'01_WORLD/story_timeline').glob(f'episode_{n:02}.*'));f=next(p for p in matches if p.suffix in ['.png','.jpeg','.jpg']);link(f,f'manga{n}{f.suffix}')
link(S/'59_sobaya_professional_window_side/prop_yametaro_wanted_poster.png','wanted.png');link(T/'chair.png','chair.png')
frames={'office':('doc.mp4',1),'sobaya_beer':('doc.mp4',7),'bar':('bar.mp4',28),'doc_still':('doc.mp4',23),'lab_still':('lab.mp4',7),'lab_wide':('lab.mp4',18.6),'quake_still':('quake.mp4',10),'underground_still':('underground.mp4',2),'yotan_offer':('underground.mp4',17),'invasion_still':('invasion.mp4',7),'tako_cockpit':('invasion.mp4',19.7),'mimic_still':('mimic.mp4',1),'mimic_result':('mimic.mp4',14),'kingdom_still':('kingdom.mp4',2),'hospital':('kingdom.mp4',35)}
for name,(src,t) in frames.items():
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(P/'public'/src),'-frames:v','1',str(P/'public'/(name+'.jpg'))],check=True)
 records.append({'file':name+'.jpg','source':vids[src],'timeSeconds':t})
link(S/'59_sobaya_professional_window_side/office_window_desk_reference_production.png','office_clean.png')
(P.parent/'asset_sources.json').write_text(json.dumps({'assets':records,'referenceArticle':'https://note.com/sobaya/n/n9b1ba408a198','musicTermsChecked':'2026-10-13','musicTerms':'https://www.thefatrat.com/terms-and-conditions'},ensure_ascii=False,indent=2))
