from pathlib import Path
import json,subprocess,sys,concurrent.futures
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;m=json.loads((P/'src/edit-manifest.json').read_text());tag=sys.argv[1] if len(sys.argv)>1 else 'v1';src=P.parent/'final_remotion_ai_video_workflow.mp4';out=P/'out'/f'audit_{tag}';out.mkdir(exist_ok=True)
points=[(f'opening_{i}',i*180+70) for i in range(3)];seen=set()
for i,d in enumerate(m['dialogue']):
 if d['view'] not in seen:points.append((f'{i:03}_{d["view"]}',d['startFrame']+min(35,d['durationInFrames']//2)));seen.add(d['view'])
points.extend([('credits',m['creditsStartFrame']+60),('last',m['composition']['durationInFrames']-5)])
def get(x):
 name,frame=x;subprocess.run(['ffmpeg','-v','error','-y','-ss',str(frame/30),'-i',str(src),'-frames:v','1',str(out/f'{name}.jpg')],check=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(get,points))
for i in range(0,len(points),6):
 canvas=Image.new('RGB',(1280,1170),'#fff');draw=ImageDraw.Draw(canvas)
 for j,(name,f) in enumerate(points[i:i+6]):
  x=(j%2)*640;y=(j//2)*390;im=Image.open(out/f'{name}.jpg').resize((640,360));canvas.paste(im,(x,y));draw.text((x+8,y+363),f'{name} | {f/30:.2f}s',fill='black')
 canvas.save(out/f'contact_{i//6+1:02}.jpg')
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(src)]))
subprocess.run(['ffmpeg','-v','error','-i',str(src),'-f','null','-'],check=True)
(out/'probe.json').write_text(json.dumps(info,indent=2));(out/'points.json').write_text(json.dumps(points,indent=2));print('AUDIT EXTRACTED',len(points))
