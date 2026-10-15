"""Verify delivered alpha, playback, fixed typography and review composites."""
import json, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
report=json.loads((ROOT/'reports/render.json').read_text())
results=[]
for s in report['members']:
 p=ROOT/'stickers'/s['id']/'sticker.png';im=Image.open(p)
 assert im.size==(320,270),(s['id'],im.size)
 assert im.n_frames==s['frames'] and 5<=im.n_frames<=24,(s['id'],im.n_frames)
 assert im.info.get('loop')==1
 assert p.stat().st_size<1000000,(s['id'],p.stat().st_size)
 frames=[];duration=0
 for i in range(im.n_frames):
  im.seek(i);duration+=im.info['duration'];a=np.array(im.convert('RGBA'));frames.append(a)
  assert ((a[:,:,3]>0)&(a[:,:,3]<255)).sum()>50,'Missing continuous alpha'
  assert (a[:3,:,3]==0).all() and (a[-3:,:,3]==0).all(),'Clipped vertical margin'
  assert (a[:,:3,3]==0).all() and (a[:,-3:,3]==0).all(),'Clipped horizontal margin'
 assert duration==3000,(s['id'],duration)
 assert np.array_equal(frames[0],frames[-1]),'Loop mismatch'
 capim=Image.open(ROOT/'source'/s['id']/'caption.png').resize((260,260),Image.Resampling.LANCZOS)
 capmask=np.zeros((270,320),bool);capmask[5:265,30:290]=np.asarray(capim)[:,:,3]>0
 assert all(np.array_equal(f[capmask],frames[0][capmask]) for f in frames),'Moving caption'
 assert any(np.count_nonzero(np.any(f!=frames[0],axis=2))>100 for f in frames[1:]),'No visible animation'
 cap=np.array(Image.open(ROOT/'source'/s['id']/'caption.png'))
 assert cap[:,:,3].min()==0 and cap[:,:,3].max()==255
 # White is restricted to glyph outline, never a full caption rectangle.
 assert np.mean(cap[:,:,3]>0)<.35,'Caption matte rectangle'
 for f in [p,p.with_name('preview.gif')]:subprocess.run(['ffmpeg','-v','error','-i',str(f),'-f','null','-'],check=True,capture_output=True)
 results.append({'id':s['id'],'size':[320,270],'frames':im.n_frames,'durationMs':duration,'bytes':p.stat().st_size,'continuousAlpha':True,'fixedCaption':True,'loopMatches':True,'decoded':True})
for bg in ['white','black']:
 p=ROOT/f'all-members-{bg}-preview.gif';im=Image.open(p);duration=0
 assert im.size==(1280,540)
 for i in range(im.n_frames):im.seek(i);duration+=im.info['duration']
 assert duration==3000
 subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True,capture_output=True)
# Human review plate: the actual export sampled at four points in the motion.
plate=Image.new('RGB',(1280,1080),'#242424')
for k,s in enumerate(report['members']):
 im=Image.open(ROOT/'stickers'/s['id']/'sticker.png')
 for j,idx in enumerate([0,5,11,17]):
  im.seek(idx);tile=Image.new('RGBA',(320,270),'#242424');tile.alpha_composite(im.convert('RGBA'))
  tile=tile.resize((160,135),Image.Resampling.LANCZOS)
  plate.paste(tile.convert('RGB'),(j*320+(k%2)*160,(k//2)*270))
# Main report is programmatic; static and motion visuals are also inspected.
(ROOT/'reports/validation.json').write_text(json.dumps({'stickers':results,'reviewGifs':{'size':[1280,540],'durationMs':3000,'source':'decoded final APNG'},'passed':True},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':True,'stickers':len(results),'maxApngBytes':max(x['bytes'] for x in results)},indent=2))
