from pathlib import Path
import json,subprocess
from PIL import Image,ImageDraw
p=Path(__file__).resolve().parent
m=json.loads((p/'src/edit-manifest.json').read_text());points=[]
last=None
for d in m['dialogue']:
 if d['view']!=last:points.append({'view':d['view'],'frame':d['startFrame']+min(45,d['durationInFrames']-1)})
 last=d['view']
points.append({'view':'credits','frame':m['creditsStartFrame']+30})
for name,frame in json.loads((p/'out/timing_frames_v7.json').read_text()):points.append({'view':name,'frame':frame})
reveal=next(d['startFrame'] for d in m['dialogue'] if d['view']=='employee')
points += [{'view':'before_clean_reveal','frame':reveal-1},{'view':'clean_reveal_start','frame':reveal},{'view':'last_frame','frame':m['composition']['durationInFrames']-1}]
source=p.parent/'final_remotion_sobaya_mystery_v7.mp4'
for point in points:
 frame=point['frame'];target=p/'out'/f'final_v7_{frame}.png'
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(frame/30),'-i',str(source),'-frames:v','1',str(target)],check=True)
for batch in range((len(points)+11)//12):
 subset=points[batch*12:batch*12+12];sheet=Image.new('RGB',(1280,390*((len(subset)+1)//2)),'#222')
 for i,r in enumerate(subset):
  im=Image.open(p/'out'/f"final_v7_{r['frame']}.png");im.thumbnail((640,360));x=i%2*640;y=i//2*390;sheet.paste(im,(x,y));ImageDraw.Draw(sheet).text((x+10,y+362),r['view']+' '+str(r['frame']),fill='white')
 sheet.save(p/'out'/f'final_contact_v7_{batch}.jpg')
(p/'out/final_audit_frames_v7.json').write_text(json.dumps(points,ensure_ascii=False,indent=2)+'\n')
print(len(points),'final encode frames extracted')
