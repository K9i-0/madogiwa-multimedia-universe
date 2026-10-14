from pathlib import Path
from PIL import Image,ImageDraw
import sys
P=Path(__file__).resolve().parent;final='--final' in sys.argv;v2='--v2' in sys.argv
files=sorted((P/('out/final_frames_v2' if v2 else 'out/final_frames')).glob('*.jpg')) if final else sorted((P/'out').glob('v2_still_*.png' if v2 else 'still_*.png'))
for offset in range(0,len(files),12):
 batch=files[offset:offset+12];canvas=Image.new('RGB',(1280,((len(batch)+2)//3)*260),'#ddd');d=ImageDraw.Draw(canvas)
 for i,f in enumerate(batch):
  im=Image.open(f);im.thumbnail((420,236));x=(i%3)*426;y=(i//3)*260;canvas.paste(im,(x,y+22));d.text((x+4,y+4),f.stem,fill='black')
 canvas.save(P/'out'/f'{"final_" if final else ""}{"v2_" if v2 else ""}contact_{offset//12}.jpg')
print(len(files),'screens')
