"""Remove white matte, preserving enclosed white artwork; captions are black ink."""
import sys
from pathlib import Path
import cv2
import numpy as np
from scipy.ndimage import distance_transform_edt
src,dst,header=sys.argv[1],sys.argv[2],int(sys.argv[3])
im=cv2.imread(src,cv2.IMREAD_UNCHANGED)
if im.dtype==np.uint16: im=(im/257).round().astype(np.uint8)
rgb=im[:,:,:3].astype(np.float32)/255
# Work from the white composite, regardless of source alpha.
if im.shape[2]==4:
 a=im[:,:,3:4].astype(np.float32)/255
 rgb=rgb*a+1-a
h,w=rgb.shape[:2]
body=rgb[header:]
# Dark/colored boundaries enclose opaque white shirts, masks, eyes and foam.
ink=(np.min(body,axis=2)<0.78).astype(np.uint8)
# The cropped white shirt meets the lower canvas edge; close its silhouette
# before filling so it is not mistaken for exterior white background.
if Path(src).parent.name=='fukuchan':
 ys,xs=np.where(ink>0)
 bottom=int(ys.max())
 row=np.where(ink[bottom]>0)[0]
 if len(row)>1: cv2.line(ink,(int(row.min()),bottom),(int(row.max()),bottom),1,1)
contours,_=cv2.findContours(ink,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
mask=np.zeros(ink.shape,np.uint8)
for c in contours:
 if cv2.contourArea(c)>=12: cv2.drawContours(mask,[c],-1,1,cv2.FILLED)
large=cv2.morphologyEx(mask,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
n,lab,st,_=cv2.connectedComponentsWithStats(mask,8)
for j in range(1,n):
 if st[j,cv2.CC_STAT_AREA]<1600: large[lab==j]=mask[lab==j]
mask=large
# White clothing reaches a cut edge or crosses small line gaps in hand poses.
# Preserve the torso interior between its left/right silhouette boundaries.
member=Path(src).parent.name
if member in ('sobaya','fukuchan'):
 start=(170 if member=='sobaya' else 290)-header
 for y in range(max(0,start),mask.shape[0]):
  xs=np.where(mask[y]>0)[0]
  if len(xs)>1: mask[y,xs.min():xs.max()+1]=1
core=cv2.erode(mask,np.ones((3,3),np.uint8),iterations=1).astype(bool)
_,idx=distance_transform_edt(~core,return_indices=True)
fg=body[idx[0],idx[1]]
# Estimate foreground coverage against white, then remove white contamination.
v=1-fg
alpha=np.clip(np.sum((1-body)*v,axis=2)/np.maximum(np.sum(v*v,axis=2),0.015),0,1)
alpha[core]=1
band=cv2.dilate(mask,np.ones((3,3),np.uint8),iterations=1).astype(bool)
alpha[~band]=0
alpha[alpha<0.12]=0
clean=np.clip((body-(1-alpha[:,:,None]))/np.maximum(alpha[:,:,None],1e-6),0,1)
edge=cv2.distanceTransform(mask,cv2.DIST_L2,5)<3
neutral=(np.max(clean,axis=2)-np.min(clean,axis=2)<0.12)&(np.max(clean,axis=2)<0.8)
clean[edge&neutral]=0
clean[alpha==0]=0
out=np.zeros((h,w,4),np.uint8)
out[header:,:,:3]=(clean*255).round().astype(np.uint8)
out[header:,:,3]=(alpha*255).round().astype(np.uint8)
# Black lettering: white becomes zero coverage, including enclosed counters.
t=1-np.mean(rgb[:header],axis=2)
t[t<0.045]=0
n,labels,stats,_=cv2.connectedComponentsWithStats((t>0.2).astype(np.uint8),8)
keep=np.zeros(t.shape,np.uint8)
for i in range(1,n):
 if stats[i,cv2.CC_STAT_AREA]>=5: keep[labels==i]=1
keep=cv2.dilate(keep,np.ones((3,3),np.uint8)).astype(bool)
t[~keep]=0
out[:header,:,3]=(t*255).round().astype(np.uint8)
# Deliberate 2px white stroke for captions and detached dark emphasis marks.
# Subpixel Gaussian edge coverage avoids a binary jagged outline.
alpha=out[:,:,3].astype(np.float32)/255
stroke_seed=np.zeros((h,w),np.uint8)
stroke_seed[:header]=(alpha[:header]>0.2).astype(np.uint8)
n,labels,stats,_=cv2.connectedComponentsWithStats((alpha[header:]>0.2).astype(np.uint8),8)
for i in range(1,n):
 region=labels==i
 area=stats[i,cv2.CC_STAT_AREA]
 colors=out[header:,:,:3][region]
 if 5<=area<=1600 and len(colors) and np.mean(np.max(colors,axis=1)<100)>0.65:
  stroke_seed[header:][region]=1
stroke=cv2.dilate(stroke_seed,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))).astype(np.float32)
stroke=cv2.GaussianBlur(stroke,(3,3),0.45)
combined=alpha+stroke*(1-alpha)
premult=out[:,:,:3].astype(np.float32)*alpha[:,:,None]+255*stroke[:,:,None]*(1-alpha[:,:,None])
out[:,:,:3]=np.clip(premult/np.maximum(combined[:,:,None],1e-6),0,255).round().astype(np.uint8)
out[:,:,3]=(combined*255).round().astype(np.uint8)
cv2.imwrite(dst,out)
