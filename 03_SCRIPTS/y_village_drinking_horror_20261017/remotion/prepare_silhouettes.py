from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFilter,ImageChops
from rembg import remove,new_session
import json
P=Path(__file__).resolve().parent;ROOT=P.parents[2];out=P/'public/art'
session=new_session('u2net_human_seg')
records=[]
def save(name,src,crop=None,alpha=False):
 im=Image.open(src).convert('RGBA')
 if crop:im=im.crop(crop)
 if alpha:mask=im.getchannel('A')
 else:mask=remove(im,session=session,only_mask=True).convert('L')
 if name=='y_guitar':
  # Human segmentation omits the instrument neck. Recover its actual dark pixels.
  region=Image.new('L',im.size,0);ImageDraw.Draw(region).rectangle((10,270,165,420),fill=255)
  dark=ImageOps.grayscale(im).point(lambda x:255 if x<105 else 0)
  mask=ImageChops.lighter(mask,ImageChops.multiply(region,dark))
 # Preserve actual photograph contour; discard low-confidence background, antialias edges.
 mask=mask.point(lambda x:255 if x>120 else 0).filter(ImageFilter.GaussianBlur(.45))
 bbox=mask.getbbox();im=im.crop(bbox);mask=mask.crop(bbox)
 black=Image.new('RGBA',im.size,(5,6,7,255));black.putalpha(mask);black.save(out/(name+'.png'))
 gray=ImageOps.grayscale(im).convert('RGBA');gray.putalpha(mask)
 # Preserve faint internal monochrome detail, rather than inventing facial features.
 white=Image.new('RGBA',im.size,(255,255,255,255));white.alpha_composite(black)
 white.convert('RGB').save(P/'out'/f'{name}_white_preview.jpg')
 records.append({'asset':name+'.png','source':str(Path(src).relative_to(ROOT)),'crop':crop,'method':'original alpha' if alpha else 'u2net_human_seg; threshold120; edge blur0.45','treatment':'solid nearly-black original-person pixels; transparent surroundings'})
save('m_photo',ROOT/'03_SCRIPTS/00_TEMPLATES/characters/commentary_duo_v1/yametaro_normal.png',alpha=True)
save('y_photo',ROOT/'02_CHARACTERS/Yotan.jpg')
save('y_guitar',ROOT/'03_SCRIPTS/00_TEMPLATES/characters/character_yotan_basic_sheet.png',(510,0,960,1024))
save('f_photo',P.parent/'reference_f_sensei_costume.png',(540,260,970,850))
save('sobaya_shadow',ROOT/'03_SCRIPTS/00_TEMPLATES/characters/commentary_sobaya_v2/sobaya_normal.png',alpha=True)
temple=Image.open(P.parent/'reference_f_sensei_costume.png').crop((680,0,1672,260))
ImageOps.grayscale(temple).filter(ImageFilter.GaussianBlur(6)).save(out/'temple.png')
(P.parent/'silhouette-sources.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print('DONE',records)
