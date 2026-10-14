from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;files=sorted((P/'out').glob('still_*.png'))
for offset in range(0,len(files),12):
 batch=files[offset:offset+12];canvas=Image.new('RGB',(1280,((len(batch)+2)//3)*260),'#ddd');d=ImageDraw.Draw(canvas)
 for i,f in enumerate(batch):
  im=Image.open(f);im.thumbnail((420,236));x=(i%3)*426;y=(i//3)*260;canvas.paste(im,(x,y+22));d.text((x+4,y+4),f.stem,fill='black')
 canvas.save(P/'out'/f'contact_{offset//12}.jpg')
print(len(files),'screens')
