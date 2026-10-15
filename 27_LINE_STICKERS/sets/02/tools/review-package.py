"""Generate audit contact sheet and reproducible delivery archives."""
import json,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
specs=json.loads((ROOT/'reports/render.json').read_text())['members']
plate=Image.new('RGB',(1920,2160),'#333333')
for k,s in enumerate(specs):
 im=Image.open(ROOT/'stickers'/s['id']/'sticker.png');n=im.n_frames
 for j in range(6):
  im.seek(round(j*(n-1)/5));tile=Image.new('RGBA',im.size,'white' if j%2==0 else 'black');tile.alpha_composite(im.convert('RGBA'));plate.paste(tile.convert('RGB'),(j*320,k*270))
plate.save(ROOT/'reports/motion-review.png')
# Current first-pose face plate (the prior redraw face plate is superseded).
boxes=[(190,25,320,165),(190,55,355,265),(205,90,335,220),(195,30,335,180),(155,125,285,275),(230,35,355,165),(245,15,365,150),(280,75,425,235)]
face=Image.new('RGB',(1000,500),'#eeeeee')
for k,(s,box) in enumerate(zip(specs,boxes)):
 im=Image.open(ROOT/'source/animation'/s['id']/'poses/00.png').crop(box);im.thumbnail((230,230));tile=Image.new('RGBA',(250,250),'#eeeeee');tile.alpha_composite(im,((250-im.width)//2,(250-im.height)//2));face.paste(tile.convert('RGB'),((k%4)*250,(k//4)*250))
face.save(ROOT/'reports/face-review.png')
# Full source-pose plate, useful for auditing the mask's facial identity.
contact=Image.new('RGB',(1536,2048),'#555555')
for row,s in enumerate(specs):
 paths=sorted((ROOT/'source/animation'/s['id']/'poses').glob('*.png'))
 for j in range(6):
  im=Image.open(paths[round(j*(len(paths)-1)/5)]).resize((256,256));bg=Image.new('RGBA',(256,256),'white' if j%2==0 else 'black');bg.alpha_composite(im);contact.paste(bg.convert('RGB'),(j*256,row*256))
contact.save(ROOT/'reports/pose-contact.png')
# Full delivery archive excludes historical rejected assets from active package.
with zipfile.ZipFile(ROOT/'release.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for s in specs:
  for p in sorted((ROOT/'stickers'/s['id']).glob('*')):
   if p.is_file():z.write(p,p.relative_to(ROOT))
  for p in sorted((ROOT/'source/animation'/s['id']).rglob('*')):
   if p.is_file():z.write(p,p.relative_to(ROOT))
 for folder in ['static','tools','reports','source/references']:
  for p in sorted((ROOT/folder).rglob('*')):
   if p.is_file() and '__pycache__' not in p.parts and p.name!='face-review.png':z.write(p,p.relative_to(ROOT))
 for name in ['README.md','set.json','source/animation-manifest.json','all-members-white-preview.gif','all-members-black-preview.gif','all-members-white-still.png','all-members-black-still.png']:
  z.write(ROOT/name,name)
# Flat APNG set is convenient for handoff; not an automatic LINE submission.
with zipfile.ZipFile(ROOT/'animated-stickers.zip','w',zipfile.ZIP_DEFLATED) as z:
 for i,s in enumerate(specs):z.write(ROOT/'stickers'/s['id']/'sticker.png',f'{i+1:02d}.png')
print('Created release.zip and animated-stickers.zip')
