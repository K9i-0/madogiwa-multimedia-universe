"""Create face/motion review plates and a portable delivery archive."""
import zipfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
boxes=[(430,20,770,390),(530,270,740,520),(470,250,710,510),(400,45,810,410),(400,400,660,630),(500,110,810,340),(550,0,840,270),(640,240,970,560)]
plate=Image.new('RGB',(1000,500),'#eeeeee')
for i,(d,b) in enumerate(zip(sorted((ROOT/'source').glob('0*')),boxes)):
 im=Image.open(d/'art.png').crop(b);im.thumbnail((240,240))
 tile=Image.new('RGBA',(250,250),'#eeeeee');tile.alpha_composite(im,((250-im.width)//2,(250-im.height)//2))
 plate.paste(tile.convert('RGB'),((i%4)*250,(i//4)*250))
plate.save(ROOT/'reports/face-review.png')
plate=Image.new('RGB',(1280,2160),'#222222')
for k,d in enumerate(sorted((ROOT/'stickers').iterdir())):
 im=Image.open(d/'sticker.png')
 for j,f in enumerate([0,5,11,17]):
  im.seek(f);tile=Image.new('RGBA',im.size,'black' if j%2 else 'white');tile.alpha_composite(im.convert('RGBA'))
  plate.paste(tile.convert('RGB'),(j*320,k*270))
plate.save(ROOT/'reports/motion-review.png')
with zipfile.ZipFile(ROOT/'release.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(ROOT.rglob('*')):
  rel=p.relative_to(ROOT)
  if not p.is_file() or rel.parts[0] in ['build','.venv','drafts'] or p.name in ['release.zip','.gitignore'] or '__pycache__' in rel.parts:continue
  z.write(p,rel)
print('Created',ROOT/'release.zip')
