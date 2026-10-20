from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw
import json, hashlib, shutil
import numpy as np
P=Path(__file__).resolve().parent;R=P.parents[2]
src=R/'16_MADOGIWA_STUDIO/public/site/ogp-balcony-20260912.jpg'
original=Image.open(src).convert('RGB')
bg=ImageOps.fit(original,(2560,1440),method=Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(85))
bg=ImageEnhance.Brightness(bg).enhance(.55)
w=1400;h=round(original.height*w/original.width);x,y=580,490
im=original.resize((w,h),Image.Resampling.LANCZOS)
shadow=Image.new('RGBA',bg.size);ImageDraw.Draw(shadow).rectangle((x-8,y-8,x+w+8,y+h+8),fill=(0,0,0,180));shadow=shadow.filter(ImageFilter.GaussianBlur(32))
bg=Image.alpha_composite(bg.convert('RGBA'),shadow).convert('RGB');bg.paste(im,(x,y))
name='youtube_banner_original_composite_v2'
bg.save(P/(name+'.png'),optimize=True);bg.save(P/(name+'.jpg'),quality=95,subsampling=0)
bg.crop((508,509,2052,931)).save(P/'mobile_preview_v2.jpg',quality=95)
assert np.array_equal(np.array(bg.crop((x,y,x+w,y+h))),np.array(im))
(P/'composition_v2.json').write_text(json.dumps({'source':str(src.relative_to(R)),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'originalRect':[x,y,w,h],'originalProcessing':'Lanczos resize only. Entire original rectangle preserved exactly in PNG. No generative edits.','background':'Same original enlarged, Gaussian blur 85px, brightness .55','verified':'All pixels in original rectangle match resized original exactly'},ensure_ascii=False,indent=2))
dest=Path.home()/'Desktop/窓際族物語_YouTubeバナー';dest.mkdir(exist_ok=True)
for f in [name+'.png',name+'.jpg','mobile_preview_v2.jpg']:shutil.copy2(P/f,dest/f)
print([(f.name,f.stat().st_size) for f in [P/(name+'.png'),P/(name+'.jpg')]])
