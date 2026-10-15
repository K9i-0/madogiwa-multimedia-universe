"""Check final delivery format and compositing invariants, not artistic quality."""
import json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'reports/render.json').read_text());results=[]
for s in r['members']:
 p=ROOT/'stickers'/s['id']/'sticker.png';im=Image.open(p)
 assert im.size==(320,270)
 assert im.n_frames==s['frames'] and 5<=im.n_frames<=20
 assert im.info['loop']==1 and p.stat().st_size<1000000
 frames=[];durations=[]
 for i in range(im.n_frames):
  im.seek(i);durations.append(round(im.info['duration']));a=np.array(im.convert('RGBA'));frames.append(a)
  assert ((a[:,:,3]>0)&(a[:,:,3]<255)).sum()>50,'No soft alpha'
  assert not a[:3,:,3].any() and not a[-3:,:,3].any() and not a[:,:3,3].any() and not a[:,-3:,3].any(),'Clipped delivery'
 assert sum(durations)==3000,(s['id'],durations)
 cap=Image.open(ROOT/'source/animation'/s['id']/'caption.png')
 capim=cap.resize((260,260),Image.Resampling.LANCZOS)
 mask=np.zeros((270,320),bool);mask[5:265,30:290]=np.array(capim)[:,:,3]>0
 assert all(np.array_equal(a[mask],frames[0][mask]) for a in frames),'Moving typography'
 assert np.mean(np.array(cap)[:,:,3]>0)<.35,'Caption background matte'
 assert any(np.count_nonzero(np.any(a!=frames[0],axis=2))>100 for a in frames[1:]),'No motion'
 assert durations[-1]>=1000,'Missing end hold'
 # Intentional one-shot: do NOT require final pose to equal initial pose.
 for f in [p,p.with_name('preview.gif')]:subprocess.run(['ffmpeg','-v','error','-i',str(f),'-f','null','-'],check=True,capture_output=True)
 st=Image.open(ROOT/'static/images'/f'{len(results)+1:02d}.png');assert st.size==(370,320) and st.mode=='RGBA'
 results.append({'id':s['id'],'frames':len(frames),'durationMs':sum(durations),'bytes':p.stat().st_size,'size':[320,270],'plays':1,'softAlpha':True,'fixedCaption':True,'endHoldMs':durations[-1],'decoded':True})
for bg in ['white','black']:
 im=Image.open(ROOT/f'all-members-{bg}-preview.gif');assert im.size==(1280,540);total=0
 for i in range(im.n_frames):im.seek(i);total+=im.info['duration']
 assert total==3000,total
 subprocess.run(['ffmpeg','-v','error','-i',str(ROOT/f'all-members-{bg}-preview.gif'),'-f','null','-'],check=True,capture_output=True)
assert [x['id'] for x in r['members']][1]=='02_hataraiteruka'
assert 'remap' not in (ROOT/'tools/build.py').read_text(),'Old deformation renderer present'
listing=[]
for name,size,animated in [('main.png',(240,240),True),('tab.png',(96,74),False)]:
 p=ROOT/name;im=Image.open(p);assert im.size==size and im.mode=='RGBA' and p.stat().st_size<1_000_000
 assert 5<=im.n_frames<=20 if animated else im.n_frames==1
 ds=[];fs=[]
 for i in range(im.n_frames):
  im.seek(i);a=np.array(im.convert('RGBA'));fs.append(a);ds.append(round(im.info.get('duration',0)))
  assert (a[:,:,3]==0).any() and (a[:,:,3]==255).any()
  assert not a[:2,:,3].any() and not a[-2:,:,3].any() and not a[:,:2,3].any() and not a[:,-2:,3].any()
 if animated:
  assert sum(ds) in [1000,2000,3000,4000]
  assert 1<=im.info['loop']<=4 and sum(ds)*im.info['loop']<=4000
  assert any(not np.array_equal(a,fs[0]) for a in fs[1:])
 subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True,capture_output=True)
 listing.append({'file':name,'size':list(size),'format':'APNG' if animated else 'PNG','frames':im.n_frames,'durationMs':sum(ds),'plays':im.info.get('loop'),'bytes':p.stat().st_size,'transparent':True,'decoded':True})
(ROOT/'reports/validation.json').write_text(json.dumps({'passed':True,'method':'generated pose sequences','stickers':results,'listing':listing,'officialGuideline':'https://creator.line.me/ja/guideline/animationsticker/','previewGifs':{'size':[1280,540],'durationMs':3000,'source':'decoded final APNG'},'note':'One-shot animations finish on final gesture. No forced reverse or loop closure.'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':True,'stickers':len(results),'maxBytes':max(x['bytes'] for x in results)},indent=2))
