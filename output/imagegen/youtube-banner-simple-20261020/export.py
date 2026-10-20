from pathlib import Path
from PIL import Image
import shutil,json
p=Path(__file__).resolve().parent
im=Image.open(p/'logo_source.png').convert('RGB')
bbox=im.convert('L').point(lambda v:255 if v>100 else 0).getbbox()
logo=im.crop(bbox);w=1200;h=round(logo.height*w/logo.width)
logo=logo.resize((w,h),Image.Resampling.LANCZOS)
out=Image.new('RGB',(2560,1440),'black');x=(2560-w)//2;y=(1440-h)//2;out.paste(logo,(x,y))
assert x>=508 and x+w<=2052 and y>=509 and y+h<=931
out.save(p/'youtube_banner_simple_v1.png')
out.crop((508,509,2052,931)).save(p/'mobile_preview.png')
out.crop((508,509,2052,931)).resize((390,107),Image.Resampling.LANCZOS).save(p/'mobile_preview_390px.png')
d=Path.home()/'Desktop/窓際族物語_YouTubeバナー'
for f in ['youtube_banner_simple_v1.png','mobile_preview.png','mobile_preview_390px.png']:shutil.copy2(p/f,d/f)
(p/'layout.json').write_text(json.dumps({'canvas':[2560,1440],'safeArea':[508,509,1544,422],'logoBounds':[x,y,w,h],'reference':'03_SCRIPTS/35_soba_shark/logo_soba_shark_master.png'},indent=2))
