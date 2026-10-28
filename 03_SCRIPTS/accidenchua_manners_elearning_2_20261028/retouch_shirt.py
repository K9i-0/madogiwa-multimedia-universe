"""Track and repair only H3's small artificial shirt dot; keep original audio.

Run: uv run --with opencv-python-headless --with numpy python retouch_shirt.py
"""
import hashlib,json,subprocess
from pathlib import Path
import cv2
import numpy as np

EP=Path(__file__).resolve().parent
source=EP/'generated/h3-mega-v2/results/video_480p.mp4'
output=EP/'generated/retouched/mega_v2_480p_clean.mp4'
output.parent.mkdir(parents=True,exist_ok=True)
picture=output.with_name('picture_lossless.mp4')
cap=cv2.VideoCapture(str(source))
fps=cap.get(cv2.CAP_PROP_FPS);width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
assert (width,height,fps)==(640,480,24)
encoder=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s','640x480','-r','24','-i','-','-an','-c:v','libx264','-crf','0','-pix_fmt','yuv420p',str(picture)],stdin=subprocess.PIPE)
records=[];index=0
while True:
    ok,frame=cap.read()
    if not ok:break
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    roi=gray[286:318,520:561]
    count,labels,stats,centers=cv2.connectedComponentsWithStats((roi<95).astype(np.uint8),8)
    candidates=[]
    for k in range(1,count):
        x,y,w,h,area=map(int,stats[k])
        cx,cy=centers[k]+(520,286)
        if 6<=area<=170 and 3<=w<=16 and 3<=h<=18 and 523<=cx<=553 and 290<=cy<=310:
            candidates.append((k,area,cx,cy,w,h))
    if candidates:
        k,area,cx,cy,w,h=max(candidates,key=lambda a:a[1])
        mask=np.zeros((480,640),np.uint8)
        mask[286:318,520:561]=(labels==k).astype(np.uint8)*255
        mask=cv2.dilate(mask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
        fixed=cv2.inpaint(frame,mask,4,cv2.INPAINT_TELEA)
        alpha=cv2.GaussianBlur(mask,(5,5),.9).astype(np.float32)/255
        frame=np.rint(frame*(1-alpha[:,:,None])+fixed*alpha[:,:,None]).astype(np.uint8)
        records.append({'frame':index,'x':round(float(cx),2),'y':round(float(cy),2),'detected_width':w,'detected_height':h,'mask_pixels':int(np.count_nonzero(mask))})
    encoder.stdin.write(frame.tobytes());index+=1
cap.release();encoder.stdin.close()
if encoder.wait():raise RuntimeError('Video encode failed')
assert index==311
subprocess.run(['ffmpeg','-y','-v','error','-i',str(picture),'-i',str(source),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(output)],check=True)
def audio_hash(path):
    return hashlib.sha256(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','adts','-'])).hexdigest()
assert audio_hash(source)==audio_hash(output)
record={'source':str(source.relative_to(EP)),'output':str(output.relative_to(EP)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'purpose':'Remove one generated dark nipple-like shirt dot only; retain broad chest contour, folds, face, mask and props.','detection_roi':[520,286,561,318],'method':'small dark connected component, 3px mask expansion, Telea local inpaint and feather','frames':index,'repaired_frames':len(records),'tracking':records,'scale_change':False,'audio_stream_copy_verified':True}
(EP/'retouch-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('Repaired',len(records),'of',index,'frames; audio bitstream unchanged.')
