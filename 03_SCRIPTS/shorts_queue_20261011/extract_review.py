#!/usr/bin/env python3
"""Extract completed-video review frames and all subtitle-card midpoint crops. Requires Pillow."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,subprocess,tempfile,math,concurrent.futures,hashlib
Q=Path(__file__).resolve().parent;R=Q.parents[1]
def one(row):
 p=R/row['output'];m=json.loads((R/row['manifest']).read_text());out=Q/'out/review'/row['slug'];out.mkdir(parents=True,exist_ok=True)
 marker=out/'source-sha256.txt'
 digest=hashlib.sha256(p.read_bytes()).hexdigest()
 if marker.exists() and marker.read_text()==digest:return row['slug']
 frames=sorted(set([0, max(0,m['durationInFrames']-2),m['durationInFrames']//2,*[round((c['startFrame']+c['endFrame'])/2) for c in m['captions']]]))
 expr='+'.join(f'eq(n,{n})' for n in frames)
 subprocess.run(['ffmpeg','-v','error','-threads','1','-i',str(p),'-vf',f"select='{expr}'",'-fps_mode','vfr','-y',str(out/'%03d.png')],check=True)
 mapped={n:out/f'{j+1:03d}.png' for j,n in enumerate(frames)}
 chosen=[frames[0],m['durationInFrames']//2,round((max(m['captions'],key=lambda c:len(c['text']))['startFrame']+max(m['captions'],key=lambda c:len(c['text']))['endFrame'])/2) if m['captions'] else m['durationInFrames']//2,frames[-1]]
 sheet=Image.new('RGB',(720,1320),'#18232c');draw=ImageDraw.Draw(sheet)
 for j,f in enumerate(chosen):
  im=Image.open(mapped[f]).convert('RGB').resize((360,640));x=(j%2)*360;y=(j//2)*660;sheet.paste(im,(x,y+20));draw.text((x+5,y+3),f"{row['order']:02d} frame {f}",fill='white')
 sheet.save(out/'contact.jpg',quality=90)
 for k in range(0,len(m['captions']),10):
  cs=m['captions'][k:k+10];sheet=Image.new('RGB',(1200,math.ceil(len(cs)/2)*260),'#18232c');draw=ImageDraw.Draw(sheet)
  for j,c in enumerate(cs):
   f=round((c['startFrame']+c['endFrame'])/2);im=Image.open(mapped[f]).convert('RGB').crop((30,860,650,1110)).resize((595,240));x=(j%2)*600;y=(j//2)*260;sheet.paste(im,(x,y+20));draw.text((x+5,y+3),f"{k+j}: {c['startFrame']}..{c['endFrame']}",fill='white')
  sheet.save(out/f'captions-{k:02d}.jpg',quality=90)
 # Review poster from the finished output, beyond the opening fade.
 f=round((m['captions'][0]['startFrame']+m['captions'][0]['endFrame'])/2) if m['captions'] else m['durationInFrames']//2
 Image.open(mapped[f]).save(Q/'remotion/out'/f"{row['slug']}.png")
 marker.write_text(digest);return row['slug']
def main():
 rows=[r for r in json.loads((Q/'queue.json').read_text()) if (R/r['output']).exists() and (Q/'remotion/out'/f"{r['slug']}.render.json").exists()]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for slug in pool.map(one,rows):print('REVIEW',slug,flush=True)
if __name__=='__main__':main()
