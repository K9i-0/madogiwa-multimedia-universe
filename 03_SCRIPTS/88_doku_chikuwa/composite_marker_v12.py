"""Original video preserved; only marker + contact shadow composited at camera keys."""
from pathlib import Path
import cv2,numpy as np,subprocess,json
P=Path(__file__).resolve().parent
keys=[[526,772,182,70],[556,772,182,70],[578,692,249,57],[579,689,250,57],[594,562,345,39],[609,493,372,30],[624,466,369,26],[639,454,367,24],[654,451,368,24],[669,448,369,24],[684,448,369,24],[705,450,369,24],[833,450,369,24],[848,450,369,24],[863,448,369,24],[878,445,369,24],[899,445,369,24]]
for key in keys:
 if key[0]>=594:key[2]+=18
(P/'marker_tracking_v12.json').write_text(json.dumps({'columns':['frame','center_x','base_y','width'],'keys':keys,'source':'wan3_result_v2_480p.mp4','occlusion':'neutral foreground RGB mask, hand/clothes; desk saturation preserved'},indent=2))
a=cv2.imread(str(P/'marker1_cutout_v12.png'),-1); ys,xs=np.where(a[:,:,3]>8);a=a[ys.min():ys.max()+1,xs.min():xs.max()+1];a[:,:,:3]=(a[:,:,:3]*.68).astype('uint8')
c=cv2.VideoCapture(str(P/'wan3_result_v2_480p.mp4'));w=int(c.get(3));h=int(c.get(4));fps=c.get(5)
enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-i',str(P/'wan3_result_v2_480p.mp4'),'-map','0:v','-map','1:a','-c:v','libx264','-crf','16','-preset','fast','-c:a','copy',str(P/'wan3_result_v2_marker_v12_480p.mp4')],stdin=subprocess.PIPE)
k=np.array(keys);n=0;thumb=[]
while True:
 ok,im=c.read()
 if not ok:break
 if 526<=n<=705 or 833<=n<=899:
  x,y,ww=[np.interp(n,k[:,0],k[:,j]) for j in range(1,4)];ww=round(ww);hh=round(ww*a.shape[0]/a.shape[1]);xx=round(x-ww/2);yy=round(y-hh)
  r=cv2.resize(a,(ww,hh),interpolation=cv2.INTER_AREA);roi=im[yy:yy+hh,xx:xx+ww];alpha=r[:,:,3].astype(float)/255
  hsv=cv2.cvtColor(roi,cv2.COLOR_BGR2HSV);occ=(((hsv[:,:,1]<100)&(hsv[:,:,2]>60))|((hsv[:,:,1]<60)&(hsv[:,:,2]>22))).astype('uint8');occ=cv2.dilate(occ,np.ones((3,3),np.uint8));alpha*=1-occ
  shadow=np.zeros((h,w),np.float32);cv2.ellipse(shadow,(round(x),round(y)),(round(ww*.6),max(2,round(ww*.07))),0,0,360,.20,-1);shadow=cv2.GaussianBlur(shadow,(7,7),1.8);im=(im*(1-shadow[:,:,None])).astype('uint8');roi=im[yy:yy+hh,xx:xx+ww]
  im[yy:yy+hh,xx:xx+ww]=(roi*(1-alpha[:,:,None])+r[:,:,:3]*alpha[:,:,None]).astype('uint8')
 if n in [526,556,579,594,609,639,669,705,833,863,893]:
  t=cv2.resize(im,(427,240));cv2.putText(t,str(n),(10,25),0,.6,(0,255,255),1);thumb.append(t)
 enc.stdin.write(im.tobytes());n+=1
enc.stdin.close();assert enc.wait()==0
thumb.append(np.zeros_like(thumb[0]));cv2.imwrite(str(P/'marker_audit_v12.jpg'),np.concatenate([np.concatenate(thumb[i:i+3],1) for i in range(0,12,3)],0));print(n)
