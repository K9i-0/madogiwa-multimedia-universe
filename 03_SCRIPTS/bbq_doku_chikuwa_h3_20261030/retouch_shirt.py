"""Local repair of H3 nipple-like dots; retain broad shirt shadows and original audio."""
import argparse,hashlib,json,subprocess
from pathlib import Path
import cv2,numpy as np
EP=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('chapter');args=p.parse_args();name=args.chapter
src=EP/'generated/partials'/f'{name}_480p.mp4'
if not src.exists():src=EP/'generated/h3-bbq-v1/results'/f'{name}_480p.mp4'
out=EP/'generated/retouched'/f'{name}_clean_480p.mp4';out.parent.mkdir(parents=True,exist_ok=True)
# Tight torso-only search windows verified on current scene, not inherited old coordinates.
regions={'ch01':[(370,175,440,220),(466,175,505,212)],'ch02':[(370,175,440,220),(466,175,505,212)],'ch04':[(385,125,450,190),(460,125,515,190)],'ch05':[]}
if name not in regions:raise ValueError('Audit current chapter coordinates before adding it')
cap=cv2.VideoCapture(str(src));w=int(cap.get(3));h=int(cap.get(4));fps=cap.get(5);assert(w,h,fps)==(864,480,24)
pic=out.with_name(name+'_lossless.mkv');enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{w}x{h}','-r','24','-i','-','-an','-c:v','ffv1',str(pic)],stdin=subprocess.PIPE)
records=[];idx=0
fall_keys=np.array([[0,414,148,490,149],[5,414,148,490,149],[6,405,163,481,163],[6.5,377,205,451,202],[7,351,343,422,347],[7.5,475,362,520,416],[8,491,361,525,416],[12.3,491,361,525,416]],dtype=float)
while True:
 ok,frame=cap.read()
 if not ok:break
 gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY);mask=np.zeros((h,w),np.uint8);selected=[]
 current_regions=regions[name]
 anchors=None
 if name=='ch05':
  t=idx/24;anchors=[(float(np.interp(t,fall_keys[:,0],fall_keys[:,1+2*i])),float(np.interp(t,fall_keys[:,0],fall_keys[:,2+2*i]))) for i in range(2)]
  radius=40 if 6.4<t<7.6 else 24
  current_regions=[(int(x-radius),int(y-radius),int(x+radius),int(y+radius)) for x,y in anchors]
 for ri,(x0,y0,x1,y1) in enumerate(current_regions):
  roi=gray[y0:y1,x0:x1];count,labels,stats,centers=cv2.connectedComponentsWithStats((roi<115).astype(np.uint8),8);candidates=[]
  for k in range(1,count):
   x,y,rw,rh,area=map(int,stats[k]);cx,cy=centers[k]+(x0,y0)
   if 15<=area<=95 and 4<=rw<=12 and 4<=rh<=11 and .55<=rw/rh<=1.9:
    if name!='ch05' and ri==1 and (not selected or abs(cy-selected[0][1])>6):continue
    # Require surrounding pixels to be bright shirt fabric, not a can/hand/background.
    patch=gray[max(0,int(cy)-9):int(cy)+10,max(0,int(cx)-9):int(cx)+10]
    if np.median(patch)<120:continue
    candidates.append((k,area,float(cx),float(cy)))
  if candidates:
   k,area,cx,cy=min(candidates,key=lambda a:(a[2]-anchors[ri][0])**2+(a[3]-anchors[ri][1])**2) if anchors else max(candidates,key=lambda a:a[1]);mask[y0:y1,x0:x1]|=(labels==k).astype(np.uint8)*255;selected.append((cx,cy))
 if selected:
  mask=cv2.dilate(mask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
  fixed=cv2.inpaint(frame,mask,4,cv2.INPAINT_TELEA);alpha=cv2.GaussianBlur(mask,(5,5),.9).astype(np.float32)/255
  frame=np.rint(frame*(1-alpha[:,:,None])+fixed*alpha[:,:,None]).astype(np.uint8)
  records.append({'frame':idx,'centers':selected,'mask_pixels':int(np.count_nonzero(mask))})
 enc.stdin.write(frame.tobytes());idx+=1
cap.release();enc.stdin.close();assert enc.wait()==0
subprocess.run(['ffmpeg','-y','-v','error','-i',str(pic),'-i',str(src),'-map','0:v','-map','1:a','-c:v','libx264','-crf','0','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(out)],check=True)
def ahash(path):return hashlib.sha256(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a','-c:a','copy','-f','adts','-'])).hexdigest()
assert ahash(src)==ahash(out)
record={'source':str(src.relative_to(EP)),'output':str(out.relative_to(EP)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'purpose':'Remove generated nipple-like dots only, leaving face/mask/body silhouette/cloth folds/audio unchanged.','regions':regions[name],'fall_keyframes':fall_keys.tolist() if name=='ch05' else None,'method':'dark compact components on bright shirt, 3px expansion, Telea and feather','frames':idx,'repaired_frames':len(records),'audio_stream_copy_verified':True,'tracking':records}
(EP/f'retouch_{name}_record.json').write_text(json.dumps(record,indent=2)+'\n');print('REPAIRED',name,len(records),'/',idx,flush=True)
