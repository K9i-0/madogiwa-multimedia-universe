from pathlib import Path
from PIL import Image, ImageDraw
import json
P=Path(__file__).resolve().parent
src=Image.open(P.parent/'game_capture.png').convert('RGBA')
bg=Image.new('RGBA',(1280,720),'#102335')
# Conventional resize/crop only; no generative editing of gameplay.
bg.alpha_composite(src.resize((1460,671),Image.Resampling.LANCZOS),(-90,-150))
records=[]
for key in 'abc':
 overlay=Image.open(P/f'overlay_{key}.png').convert('RGBA')
 assert overlay.getextrema()[3][0]==0, 'True alpha is required'
 overlay=overlay.resize((1280,720),Image.Resampling.LANCZOS)
 final=Image.alpha_composite(bg,overlay).convert('RGB')
 final.save(P/f'thumbnail_{key}.png')
 final.save(P/f'thumbnail_{key}.jpg',quality=95,subsampling=0)
 records.append({'candidate':key,'overlaySource':f'overlay_{key}.png','gameSource':'../game_capture.png','gamePosition':[-90,-150],'gameResized':[1460,671],'output':[1280,720],'imagegen':'entire foreground: hosts, typography, ornaments','background':'original gameplay pixels; navy backing below frame'})
(P/'composition.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
sheet=Image.new('RGB',(960,3*566),'#102335');draw=ImageDraw.Draw(sheet)
for i,key in enumerate('abc'):
 sheet.paste(Image.open(P/f'thumbnail_{key}.jpg').resize((960,540),Image.Resampling.LANCZOS),(0,i*566+26));draw.text((15,i*566+6),key.upper(),fill='white')
sheet.save(P/'comparison.jpg',quality=92)
