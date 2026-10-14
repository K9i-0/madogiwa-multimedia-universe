from pathlib import Path
import cv2,numpy as np,subprocess,json,os
P=Path(__file__).resolve().parent
keys=np.array([[0,676,358],[15,676,353],[30,677,337],[45,678,323],[60,673,314],[75,675,320],[90,682,367],[107,682,368]],float)
c=cv2.VideoCapture(str(P/'wan3_aftermath_v15_480p.mp4'));w=int(c.get(3));h=int(c.get(4));fps=c.get(5)
name='wan3_aftermath_mosaic_v18_480p.mp4'
enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-i',str(P/'wan3_aftermath_v15_480p.mp4'),'-map','0:v','-map','1:a','-c:v','libx264','-crf','16','-preset','fast','-c:a','copy',str(P/name)],stdin=subprocess.PIPE)
thumb=[];n=0
while True:
 ok,im=c.read()
 if not ok:break
 x=round(np.interp(n,keys[:,0],keys[:,1]));y=round(np.interp(n,keys[:,0],keys[:,2]));left=x-48;top=y-48
 roi=im[top:top+96,left:left+96];small=cv2.resize(roi,(6,6),interpolation=cv2.INTER_AREA);im[top:top+96,left:left+96]=cv2.resize(small,(96,96),interpolation=cv2.INTER_NEAREST)
 if n in keys[:,0]:
  a=cv2.resize(im,(427,240));cv2.putText(a,str(n),(10,25),0,.6,(0,255,255),1);thumb.append(a)
 enc.stdin.write(im.tobytes());n+=1
enc.stdin.close();assert enc.wait()==0
cv2.imwrite(str(P/'.mosaic_audit_v18.jpg'),np.concatenate([np.concatenate(thumb[:4],1),np.concatenate(thumb[4:],1)],0))
S=P/'remotion/src';m=json.loads((S/'edit-manifest-v17.json').read_text())
for s in m['shots']:
 if s['file']=='wan3_aftermath_v15_480p.mp4':s['file']=name
(S/'edit-manifest-v18.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
pub=P/'remotion/public'/name
if not pub.exists():os.link(P/name,pub)
f=S/'Root.tsx';s=f.read_text()
if 'edit-manifest-v18' not in s:
 s=s.replace('export const Root',"import censored from './edit-manifest-v18.json';\nexport const Root")
 s=s.replace('</>;', '<Composition id="DokuChikuwaMosaic" component={DokuChikuwa} defaultProps={{manifest:censored,drama:true,records:true,enhanced:true}} width={1280} height={720} fps={30} durationInFrames={censored.durationInFrames}/>\n</>;');f.write_text(s)
(P/'edit_v18_record.json').write_text(json.dumps(dict(effect='tracked rectangular pixel mosaic over Sobaya head; comic censorship, not mask repair',source='wan3_aftermath_v15_480p.mp4',source_size=[w,h],roi_size=[96,96],pixel_grid=[6,6],tracking_keys=keys.tolist(),timeline_frames=[1361,1469],audio='master_v17.wav unchanged',video_generation=False),ensure_ascii=False,indent=2)+'\n')
