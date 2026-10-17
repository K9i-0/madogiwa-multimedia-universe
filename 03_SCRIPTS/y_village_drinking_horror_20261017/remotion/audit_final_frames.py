"""Extract exact numbered frames from the delivered MP4, including cut boundaries."""
from pathlib import Path
import json,subprocess,shutil
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;m=json.loads((P/'src/edit-manifest.json').read_text());by={r['id']:r for r in m['narration']}
out=P/'out/final-stills-v7';out.mkdir(exist_ok=True)
anchors=[('title',45),('excel','n0002v5a1'),('m','n0004'),('y','n0006'),('village','n0019'),('warning','n0027'),('monkeys','n0048a'),('bowl','n0053'),('blame','n0085v5r2'),('cans','n0109'),('recording','n0134'),('cold-answer','n0143'),('empty-room','n0192'),('applause-wait','n0202'),('recollection','n0214'),('moonlit','n0075v7a0'),('wife-question','n0141'),('absence-hearsay','n0167a'),('awareness','n0219v6a4'),('opened','n0219v6a6'),('costume','n0228'),('aura','n0255v5a3'),('authority','n0238'),('rule','n0265'),('four-mugs','n0297'),('reveal',m['revealFrame']+30),('skin','n0320'),('cup','n0333'),('f-view','n0346'),('applause','n0367'),('escape','n0375'),('request','n0415'),('empty-mug','n0421'),('asleep','n0427'),('morning','n0460'),('return','n0471v6a0'),('ending','n0486'),('last-line','n0487')]
cases=[(name,a if isinstance(a,int) else by[a]['from']+min(30,by[a]['duration']//2)) for name,a in anchors]
extra=[]
for i,x in enumerate(m['inserts']):
 for side,f in [('before',x['from']-1),('start',x['from']),('start-plus',x['from']+1),('end',x['to']-1),('after',x['to'])]:extra.append((f'ui-{i}-{side}',f))
for label,f in [('moonlit',m['glimpseFrame']),('moonlit-end',by['n0076']['from']),('reveal',m['revealFrame']),('toast',by['n0133']['from']),('hand-withdrawn',by['n0136']['from']),('can-open',next(s['from'] for s in m['shots'] if s['background']=='hand_can_open_v6'))]:
 for offset in [-1,0,1,15]:extra.append((f'{label}-{offset:+}',f+offset))
longest=max(m['captions'],key=lambda c:max(map(len,c['text'].splitlines())))
extra.append(('longest-caption',longest['from']+10))
frames=sorted({f for _,f in cases+extra});flt='select='+('+'.join(fr'eq(n\,{f})' for f in frames))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P.parent/'review_remotion_horror_aoyama_v7.mp4'),'-vf',flt,'-fps_mode','vfr','-q:v','2',str(out/'frame_%04d.jpg')],check=True)
lookup={f:out/f'frame_{i+1:04}.jpg' for i,f in enumerate(frames)}
for name,f in cases+extra:shutil.copy2(lookup[f],out/(name+'.jpg'))
for page in range((len(cases)+7)//8):
 group=cases[page*8:page*8+8];sheet=Image.new('RGB',(1280,385*((len(group)+1)//2)),'#151515');d=ImageDraw.Draw(sheet)
 for i,(name,f) in enumerate(group):
  im=Image.open(out/(name+'.jpg')).convert('RGB').resize((640,360));x=i%2*640;y=i//2*385
  d.text((x+8,y+5),f'{name} | {f}',fill='white');sheet.paste(im,(x,y+25))
 sheet.save(out/f'contact-{page}.jpg',quality=94)
for page in range((len(extra)+11)//12):
 group=extra[page*12:page*12+12];sheet=Image.new('RGB',(1280,210*((len(group)+3)//4)),'#151515');d=ImageDraw.Draw(sheet)
 for i,(name,f) in enumerate(group):
  im=Image.open(out/(name+'.jpg')).convert('RGB').resize((320,180));x=i%4*320;y=i//4*210
  d.text((x+5,y+5),name,fill='white');sheet.paste(im,(x,y+25))
 sheet.save(out/f'boundaries-{page}.jpg',quality=94)
(out/'frames.json').write_text(json.dumps([{'name':name,'frame':f} for name,f in cases+extra],indent=2)+'\n')
print('Exact final frames extracted:',len(cases+extra))
