"""v4: photo-derived adult Sobaya contour and existing debug-prayer costume insert."""
from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw,ImageOps
from rembg import remove,new_session
import json
P=Path(__file__).resolve().parent;R=P.parents[2];art=P/'public/art'
source=R/'03_SCRIPTS/00_TEMPLATES/characters/character_sobaya_basic_sheet.png'
im=Image.open(source).convert('RGBA').crop((0,110,400,910))
mask=remove(im,session=new_session('u2net_human_seg'),only_mask=True).convert('L')
mask=mask.point(lambda p:255 if p>120 else 0).filter(ImageFilter.GaussianBlur(.45))
bbox=mask.getbbox();mask=mask.crop(bbox)
sil=Image.new('RGBA',mask.size,(5,6,7,255));sil.putalpha(mask);sil.save(art/'sobaya_shadow_v4.png')
source2=R/'03_SCRIPTS/31_debug_prayer_news/scene_02b_gyungyun_pose_start_production.png'
# Lower torso and legs only: the bottom of the old-name badge is above y=535.
crop=(672,535,965,930)
detail=Image.open(source2).convert('RGB').crop(crop)
base=Image.open(art/'temple.png').convert('RGB').resize((1280,720)).filter(ImageFilter.GaussianBlur(12))
base=Image.blend(base,Image.new('RGB',base.size,'#0c0b0b'),.72)
detail.thumbnail((800,650),Image.Resampling.LANCZOS)
# Resize from the original once, keeping the costume proportions intact.
detail=Image.open(source2).convert('RGB').crop(crop).resize((482,650),Image.Resampling.LANCZOS)
base.paste(detail,((1280-detail.width)//2,15));base.save(art/'f_hakama.png')
record={'sobaya':{'source':str(source.relative_to(R)),'crop':[0,110,400,910],'output':'art/sobaya_shadow_v4.png','method':'original full-body crop; u2net_human_seg mask; solid silhouette; proportions unchanged'},'costume':{'source':str(source2.relative_to(R)),'crop':list(crop),'output':'art/f_hakama.png','method':'original lower-body crop; no head, name badge, attendants or deity; no generated replacement'}}
(P.parent/'feedback-assets-v4.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(record)
