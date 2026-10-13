"""Extract the actual encoded frames around every speech-linked visual cue."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,json,subprocess
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source',default='out/review_v6_01.mp4');args=parser.parse_args()
m=json.loads((P/'src/edit-manifest.json').read_text());ds={d['id']:d for d in m['dialogue']}
cues=json.loads((P/'src/visual-cues-v6.json').read_text());out=P/'out/audit_v6_cues';out.mkdir(exist_ok=True)
points=[]
for id,values in cues.items():
 for index,offset in enumerate(values.values()):
  assert isinstance(offset,int) and 0<offset<ds[id]['durationInFrames']
  for delta in [-1,0,1,9]:
   points.append((f'{id}_{index}_{delta:+03}',ds[id]['startFrame']+offset+delta))
def get(point):
 name,frame=point
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(frame/30),'-i',str((P/args.source).resolve()),'-frames:v','1',str(out/f'{name}.jpg')],check=True)
with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(get,points))
# Each row is the before/settled pair; all boundary frames remain on disk.
selected=[p for p in points if p[0].endswith('-01') or p[0].endswith('+09')]
for i in range(0,len(selected),8):
 canvas=Image.new('RGB',(1280,1520),'white');draw=ImageDraw.Draw(canvas)
 for j,(name,frame) in enumerate(selected[i:i+8]):
  x=j%2*640;y=j//2*380
  canvas.paste(Image.open(out/f'{name}.jpg').resize((640,360)),(x,y));draw.text((x+5,y+360),f'{name} / {frame}',fill='black')
 canvas.save(out/f'contact_{i//8:02}.jpg')
(out/'points.json').write_text(json.dumps(points,indent=2))
print(f'{len(points)} boundary frames; {len(selected)//2} cues')
