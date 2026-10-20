from pathlib import Path
from PIL import Image,ImageOps,ImageFilter
from collections import deque
import numpy as np
import shutil
p=Path(__file__).resolve().parent
im=Image.open(p/'youtube_banner_simple_v1.png').convert('RGB');a=np.array(im);gray=np.array(im.convert('L'))
mask=np.zeros(gray.shape,dtype=np.uint8)
for sx,sy in [(743,635),(871,635),(734,787),(874,787)]:
 assert gray[sy,sx]<180,(sx,sy)
 q=deque([(sx,sy)])
 while q:
  x,y=q.popleft()
  if mask[y,x] or gray[y,x]>=180:continue
  mask[y,x]=255
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:q.append((x+dx,y+dy))
assert 1000<(mask>0).sum()<15000
edge=np.array(Image.fromarray(mask).filter(ImageFilter.MaxFilter(3)))>0
alpha=(255-gray.astype(float))/255
red=a.astype(float).copy();target=np.array([190,24,32])
red[edge]=255*(1-alpha[edge,None])+target*alpha[edge,None]
variants={'inverted':ImageOps.invert(im),'red_lines':Image.fromarray(np.uint8(np.clip(red,0,255)))}
d=Path.home()/'Desktop/窓際族物語_YouTubeバナー'
for name,v in variants.items():
 filename=f'youtube_banner_simple_{name}.png';v.save(p/filename);shutil.copy2(p/filename,d/filename)
 preview=f'mobile_preview_{name}.png';v.crop((508,509,2052,931)).resize((780,213),Image.Resampling.LANCZOS).save(p/preview);shutil.copy2(p/preview,d/preview)
assert np.array_equal(np.array(variants['red_lines'])[~edge],a[~edge])
print('Verified: only four mask markings changed; inverted version is exact RGB inversion.')
