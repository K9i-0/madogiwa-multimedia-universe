from pathlib import Path
import json,subprocess,argparse,concurrent.futures
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source',default='../final_remotion_ai_video_workflow_v4.mp4');parser.add_argument('--tag',default='v4');parser.add_argument('--manifest',default='src/edit-manifest.json');args=parser.parse_args()
m=json.loads((P/args.manifest).read_text());src=(P/args.source).resolve();out=P/'out'/f'audit_{args.tag}';out.mkdir(exist_ok=True)
points=[('opening',30)]
for i,d in enumerate(m['dialogue']):
 points.append((f'{i:03}_{d["view"]}',d['startFrame']+min(35,d['durationInFrames']//2)))
points.extend([('ending_hold',m['composition']['durationInFrames']-40),('last',m['composition']['durationInFrames']-5)])
for c in m['clips']:
 points.extend([(c['id']+'_start',c['startFrame']+3),(c['id']+'_middle',c['startFrame']+c['durationInFrames']//2),(c['id']+'_end',c['startFrame']+c['durationInFrames']-3)])
for view in ('edit_demo','api_split','validation','skill_loop','export'):
 rows=[d for d in m['dialogue'] if d['view']==view]
 if rows:points.append((view+'_late',rows[-1]['startFrame']+rows[-1]['durationInFrames']//2))
points.sort(key=lambda x:x[1])
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
