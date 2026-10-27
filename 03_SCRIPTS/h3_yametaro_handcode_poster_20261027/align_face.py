"""Register H3 face to the source poster using static upper-face features."""
from pathlib import Path
import cv2,numpy as np,json
P=Path(__file__).resolve().parent
ref=cv2.resize(cv2.imread(str(P/'poster.png')),(480,640),interpolation=cv2.INTER_AREA)
mask=np.zeros((640,480),np.uint8);mask[240:420,125:345]=255
sift=cv2.SIFT_create(nfeatures=6000,contrastThreshold=.012)
kr,dr=sift.detectAndCompute(cv2.cvtColor(ref,cv2.COLOR_BGR2GRAY),mask)
matcher=cv2.BFMatcher();reports={}
for chapter in ['ch01','ch02','ch03']:
 cap=cv2.VideoCapture(str(P/'generated/h3-job/results'/f'{chapter}_480p.mp4'));rows=[];n=0
 while True:
  ok,frame=cap.read()
  if not ok:break
  if n%6==0:
   k,d=sift.detectAndCompute(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),None)
   pairs=matcher.knnMatch(d,dr,k=2);good=[a for a,b in pairs if a.distance<.72*b.distance]
   if len(good)>=5:
    src=np.float32([k[x.queryIdx].pt for x in good]);dst=np.float32([kr[x.trainIdx].pt for x in good])
    M,inliers=cv2.estimateAffinePartial2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=2.5,maxIters=4000,confidence=.999)
    if M is not None:
     scale=float(np.hypot(M[0,0],M[1,0]));angle=float(np.degrees(np.arctan2(M[1,0],M[0,0])))
     if .3<scale<1.5 and abs(angle)<15 and inliers.sum()>=5:rows.append({'frame':n,'matrix':M.tolist(),'inliers':int(inliers.sum()),'scale':scale})
  n+=1
 cap.release();reports[chapter]={'frames':n,'samples':rows};print(chapter,n,len(rows),[(x['frame'],round(x['scale'],3),x['inliers']) for x in rows[::max(1,len(rows)//5)]],flush=True)
(P/'generated/alignment-raw.json').write_text(json.dumps(reports,indent=2)+'\n')
# Interpolate feature registration and smooth over nine frames to avoid jitter.
transforms={}
for name,report in reports.items():
 rows=report['samples'];assert len(rows)>=report['frames']//12, 'Too few reliable registrations'
 t=np.array([x['frame'] for x in rows]);arr=np.array([x['matrix'] for x in rows]);allframes=np.arange(report['frames'])
 flat=arr.reshape(len(rows),6)
 interp=np.stack([np.interp(allframes,t,flat[:,i]) for i in range(6)],axis=1)
 smooth=np.stack([np.convolve(np.pad(interp[:,i],(4,4),mode='edge'),np.ones(9)/9,mode='valid') for i in range(6)],axis=1)
 transforms[name]=np.round(smooth,6).tolist()
(P/'remotion/src/face-transforms.json').write_text(json.dumps(transforms,separators=(',',':'))+'\n')
