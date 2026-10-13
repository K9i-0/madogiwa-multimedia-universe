from pathlib import Path
import json,subprocess,hashlib
from PIL import Image,ImageDraw
p=Path(__file__).resolve().parent;m=json.loads((p/'remotion/src/edit-manifest.json').read_text());old=json.loads((p/'remotion/src/edit-manifest-revision02.json').read_text())
out=p/'remotion/out/usagi_audit';out.mkdir(parents=True,exist_ok=True);v=p/'final_remotion_kikou5_usagi_normal.mp4'
assert len(m['dialogue'])==len(old['dialogue'])==57
for a,b in zip(m['dialogue'],old['dialogue']):
 assert a['text']==b['text']
 assert a['caption']==b['caption']
 if a['who']=='yametaro':assert a['sha256']==b['sha256']
for a,b in zip(m['clips'],old['clips']):
 assert {k:v for k,v in a.items() if k!='startFrame'}=={k:v for k,v in b.items() if k!='startFrame'}
shots=[(f"line{i:02}",r['startFrame']+min(25,r['durationInFrames']//2)) for i,r in enumerate(m['dialogue'],1)]
shots += [(c['id']+'_'+str(j),c['startFrame']+offset) for c in m['clips'] for j,offset in enumerate([6,c['durationInFrames']//2,c['durationInFrames']-7])]
shots += [('credits',m['composition']['durationInFrames']-45)]
for label,f in shots:
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(f/30),'-i',str(v),'-frames:v','1',str(out/(label+'.png'))],check=True)
for start in range(0,len(shots),6):
 sheet=Image.new('RGB',(1280,1170),'#dddddd');draw=ImageDraw.Draw(sheet)
 for j,(label,f) in enumerate(shots[start:start+6]):
  im=Image.open(out/(label+'.png')).resize((640,360));x=(j%2)*640;y=(j//2)*390
  sheet.paste(im,(x,y));draw.text((x+10,y+365),f'{label}: frame {f} / {f/30:.2f}s',fill='black')
 sheet.save(out/f'contact_{start//6+1:02}.jpg')
(p/'usagi_integrity.json').write_text(json.dumps({'dialogueCount':57,'replacedTakosanLines':29,'unchangedYametaroLines':28,'originalClipsUnchanged':len(m['clips']),'subtitleTextUnchanged':True,'shots':shots,'sha256':hashlib.sha256(v.read_bytes()).hexdigest()},ensure_ascii=False,indent=2)+'\n')
print('PASS: source integrity; actual MP4 shots',len(shots),flush=True)
