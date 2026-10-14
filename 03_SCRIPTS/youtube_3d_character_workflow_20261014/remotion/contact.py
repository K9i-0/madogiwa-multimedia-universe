from pathlib import Path
from PIL import Image,ImageDraw
import sys
P=Path(__file__).resolve().parent;final='--final' in sys.argv;version='v5' if '--v5' in sys.argv else 'v4' if '--v4' in sys.argv else 'v3' if '--v3' in sys.argv else 'v2' if '--v2' in sys.argv else ''
files=sorted((P/('out/final_frames'+('_'+version if version else ''))).glob('*.jpg')) if final else sorted((P/'out').glob(version+'_still_*.png' if version else 'still_*.png'))
for offset in range(0,len(files),12):
 batch=files[offset:offset+12];canvas=Image.new('RGB',(1280,((len(batch)+2)//3)*260),'#ddd');d=ImageDraw.Draw(canvas)
 for i,f in enumerate(batch):
  im=Image.open(f);im.thumbnail((420,236));x=(i%3)*426;y=(i//3)*260;canvas.paste(im,(x,y+22));d.text((x+4,y+4),f.stem,fill='black')
 canvas.save(P/'out'/f'{"final_" if final else ""}{version+"_" if version else ""}contact_{offset//12}.jpg')
print(len(files),'screens')
