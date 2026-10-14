from pathlib import Path
import cv2,numpy as np,subprocess
P=Path(__file__).resolve().parent
ref=cv2.resize(cv2.imread(str(P/'blocking_aftermath_v12.png')),(854,480))
mask=np.zeros((480,854),np.uint8);mask[175:225,368:452]=255
# Exclude edge of pot/reference marker; ellipse tightly encompasses ingredients and vessel.
mask[:]=0;cv2.ellipse(mask,(409,200),(35,19),0,0,360,255,-1);mask=cv2.GaussianBlur(mask,(7,7),1.1)
sift=cv2.SIFT_create();featuremask=np.full((480,854),255,np.uint8);featuremask[0:330,225:360]=0;featuremask[:,500:650]=0;featuremask[300:]=0;featuremask[170:230,360:460]=0
k1,d1=sift.detectAndCompute(ref,featuremask);bf=cv2.BFMatcher()
c=cv2.VideoCapture(str(P/'wan3_aftermath_v12c_480p.mp4'))
enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s','854x480','-r','30','-i','-','-i',str(P/'wan3_aftermath_v12c_480p.mp4'),'-map','0:v','-map','1:a','-c:v','libx264','-crf','16','-c:a','copy',str(P/'wan3_aftermath_v12c_potfix_480p.mp4')],stdin=subprocess.PIPE)
H=np.eye(3);thumb=[];n=0
while True:
 ok,im=c.read()
 if not ok:break
 k2,d2=sift.detectAndCompute(im,None);matches=bf.knnMatch(d1,d2,k=2);good=[a for a,b in matches if a.distance<.7*b.distance]
 if len(good)>10:
  hh,inl=cv2.findHomography(np.float32([k1[m.queryIdx].pt for m in good]),np.float32([k2[m.trainIdx].pt for m in good]),cv2.RANSAC,3)
  if hh is not None:H=hh
 patch=cv2.warpPerspective(ref,H,(854,480));alpha=cv2.warpPerspective(mask,H,(854,480)).astype(float)/255
 im=np.round(im*(1-alpha[:,:,None])+patch*alpha[:,:,None]).astype('uint8');enc.stdin.write(im.tobytes())
 if n%30==0:thumb.append(cv2.resize(im,(427,240)))
 n+=1
enc.stdin.close();assert enc.wait()==0
cv2.imwrite(str(P/'aftermath_potfix_audit_v12.jpg'),np.concatenate([np.concatenate(thumb[i:i+3],1) for i in [0,3]],0))
