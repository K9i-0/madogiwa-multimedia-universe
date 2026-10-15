"""Render generated pose sheets. No body deformation or motion interpolation.
Only rigid whole-frame translation registers stationary scene anchors; a fixed
background composite protects stationary scenery. Character motion is drawn.
"""
import json, shutil, math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import distance_transform_edt
ROOT=Path(__file__).resolve().parents[1]
FONT='/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc'
SPECS=json.loads((ROOT/'source/animation-manifest.json').read_text())
# Stationary patches in 512px cell coordinates; no moving face/limb registration.
ANCHORS=[[(80,70,60,100),(90,370,65,70),(380,55,55,120)],
 [(20,400,100,65),(400,410,85,50),(95,190,55,90)],
 [(70,320,60,100),(360,360,60,80),(110,35,60,100)],
 [(325,355,50,80),(405,40,65,130),(180,380,80,70)],
 [(340,50,65,150),(320,410,75,55),(50,75,70,60)],
 [(105,210,35,70),(390,60,65,65),(395,310,55,45)],
 [(85,310,65,95),(100,285,55,50)],
 [(100,60,65,90),(65,20,40,80),(65,410,160,40)]]
# Regions containing the complete union of moving anatomy, in base cell coords.
POLYS=[ [[(310,40),(457,40),(457,455),(282,455),(282,180),(310,180)]],
 [[(182,25),(500,35),(510,395),(405,405),(405,490),(240,490),(245,360),(175,320)]],
 [[(160,80),(365,80),(402,290),(320,307),(178,285),(145,220),(112,210),(112,105)]],
 [[(188,15),(330,15),(400,130),(410,310),(300,315),(267,205),(150,180),(150,140)]],
 [[(40,65),(270,65),(290,260),(355,325),(320,410),(110,430),(45,355)]],
 [],[],
 [[(365,155),(480,155),(490,382),(335,385),(315,295),(350,245)]]]
NAMES=['下ろした手を上げ、口元が輝く','仕切り越しに前へ乗り出してのぞく','肩をすくめて震え、白い息を吐く','指差す手を下ろし、窓を向く','ドリルで締め、引いて窓を見る','両手で頭を抱え、丸くなる','書類を投げ、手招きして帰る','寝たまま手を上げてサムズアップ']

def save(im,p):
 p.parent.mkdir(parents=True,exist_ok=True);im.save(p)

def clean(im):
 a=np.array(im.convert('RGBA'));alpha=a[:,:,3].copy()
 # Generated fully covered pixels are 253/254; normalize opaque interiors.
 alpha[alpha>=245]=255;alpha[alpha<18]=0
 n,lab,stats,_=cv2.connectedComponentsWithStats((alpha>60).astype('uint8'),8)
 keep=np.zeros(alpha.shape,'uint8')
 for k in range(1,n):
  if stats[k,cv2.CC_STAT_AREA]>=12:keep[lab==k]=1
 keep=cv2.dilate(keep,np.ones((3,3),'uint8'));alpha[keep==0]=0
 core=alpha==255
 if core.any():
  _,idx=distance_transform_edt(~core,return_indices=True)
  edge=(alpha>0)&(alpha<255);a[:,:,:3][edge]=a[idx[0],idx[1],:3][edge]
 a[:,:,3]=alpha;a[alpha==0,:3]=0
 return Image.fromarray(a)

def gray(im):
 bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im)
 return cv2.cvtColor(np.asarray(bg.convert('RGB')),cv2.COLOR_RGB2GRAY)

def register(base,other,anchors):
 g0=gray(base);g=gray(other);moves=[]
 for x,y,w,h in anchors:
  t=g0[y:y+h,x:x+w];sx=max(0,x-38);sy=max(0,y-38)
  search=g[sy:min(512,y+h+38),sx:min(512,x+w+38)]
  res=cv2.matchTemplate(search,t,cv2.TM_CCOEFF_NORMED);_,score,_,loc=cv2.minMaxLoc(res)
  if score>.65:moves.append((sx+loc[0]-x,sy+loc[1]-y,score))
 if not moves:return other,{'dx':0,'dy':0,'matches':[]}
 dx,dy=np.rint(np.median(np.array(moves)[:,:2],axis=0)).astype(int)
 out=Image.new('RGBA',(512,512));out.paste(other,(-int(dx),-int(dy)))
 return out,{'dx':int(dx),'dy':int(dy),'matches':moves}

def prepare(k,s):
 d=ROOT/'source/animation'/s['id'];sheet=Image.open(d/'keyframes.png').convert('RGBA')
 cw=sheet.width//3;ch=sheet.height//2
 raw=[clean(sheet.crop((i%3*cw,i//3*ch,(i%3+1)*cw,(i//3+1)*ch)).resize((512,512),Image.Resampling.LANCZOS)) for i in range(6)]
 if k==4:
  extra=Image.open(d/'finish-keyframes.png').convert('RGBA');ew=extra.width//3;eh=extra.height//2
  # Replace abrupt final pose with five generated intermediate/end poses.
  raw=raw[:5]+[clean(extra.crop((i%3*ew,i//3*eh,(i%3+1)*ew,(i//3+1)*eh)).resize((512,512),Image.Resampling.LANCZOS)) for i in range(1,6)]
 frames=[raw[0]];regs=[]
 for im in raw[1:]:
  aligned,r=register(raw[0],im,ANCHORS[k]);frames.append(aligned);regs.append(r)
 if POLYS[k]:
  m=Image.new('L',(512,512));dr=ImageDraw.Draw(m)
  for p in POLYS[k]:dr.polygon(p,fill=255)
  # A narrow feather in static areas, not optical-flow interpolation.
  m=m.filter(ImageFilter.GaussianBlur(1))
  frames=[Image.composite(f,frames[0],m) for f in frames]
 (d/'registration.json').write_text(json.dumps(regs,indent=2)+'\n')
 if k==5:
  # Reject disconnected narrow slivers from neighbouring sprite cells.
  kept=[]
  for f in frames:
   arr=np.array(f);n,lab,stats,_=cv2.connectedComponentsWithStats((arr[:,:,3]>30).astype('uint8'),8)
   main=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);keep=cv2.dilate((lab==main).astype('uint8'),np.ones((3,3),'uint8'))
   arr[keep==0]=0;kept.append(Image.fromarray(arr))
  frames=kept
 for i,f in enumerate(frames):save(f,d/'poses'/f'{i:02d}.png')
 # One COMMON crop across ALL poses preserves intentional motion and scale.
 boxes=[f.getbbox() for f in frames]
 box=(max(0,min(b[0] for b in boxes)-3),max(0,min(b[1] for b in boxes)-3),min(512,max(b[2] for b in boxes)+3),min(512,max(b[3] for b in boxes)+3))
 return [f.crop(box) for f in frames],box

def caption(lines):
 out=Image.new('RGBA',(1200,1200));d=ImageDraw.Draw(out);fs=205 if len(lines)==1 else 127
 while True:
  f=ImageFont.truetype(FONT,fs,index=0)
  if max(d.textbbox((0,0),s,font=f)[2] for s in lines)<1120:break
  fs-=1
 y=24
 for s in lines:
  b=d.textbbox((0,0),s,font=f);d.text(((1200-(b[2]-b[0]))/2-b[0],y-b[1]),s,font=f,fill='black',stroke_width=6,stroke_fill='white');y+=b[3]-b[1]+18
 return out,y+14

def outline(im):
 alpha=im.getchannel('A').filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(.4))
 white=Image.new('RGBA',im.size,'white');white.putalpha(alpha)
 return Image.alpha_composite(white,im)

def compose(art,cap,hh):
 a=Image.new('RGBA',(1200,1200));scale=min(1120/art.width,(1200-hh-36)/art.height)
 fg=outline(art.resize((round(art.width*scale),round(art.height*scale)),Image.Resampling.LANCZOS))
 a.alpha_composite(fg,((1200-fg.width)//2,hh+(1200-hh-36-fg.height)//2));a.alpha_composite(cap);return a

def sparkle(im,r,box):
 # Separate graphic effect next to mouth, no deformation of the mask.
 out=im.copy();d=ImageDraw.Draw(out);x,y=310-box[0],130-box[1]
 pts=[(x,y-r),(x+r*.23,y-r*.23),(x+r,y),(x+r*.23,y+r*.23),(x,y+r),(x-r*.23,y+r*.23),(x-r,y),(x-r*.23,y-r*.23)]
 d.polygon(pts,fill=(255,197,20,255));d.polygon([(x,y-r*.65),(x+r*.14,y-r*.14),(x+r*.65,y),(x+r*.14,y+r*.14),(x,y+r*.65),(x-r*.14,y+r*.14),(x-r*.65,y),(x-r*.14,y-r*.14)],fill='white')
 return out

def chair_label(im,box):
 out=im.copy();d=ImageDraw.Draw(out);f=ImageFont.truetype(FONT,19,index=0)
 for j,t in enumerate(['アーロン','チュア']):d.text((203-box[0],383+j*24-box[1]),t,font=f,fill=(30,24,18,255))
 return out

def snow(im,i,box):
 out=im.copy();d=ImageDraw.Draw(out)
 for j in range(9):
  x=125+(j*37)%300-box[0];y=32+(j*19+i*5)%92-box[1]
  if 0<x<im.width and 0<y<im.height and im.getpixel((int(x),int(y)))[3]>240:
   d.ellipse((x-1.4,y-1.4,x+1.4,y+1.4),fill=(255,255,255,255))
 return out

def gif(frames,ds,p):
 sample=Image.new('RGB',(frames[0].width,frames[0].height*3))
 for j,i in enumerate([0,len(frames)//2,len(frames)-1]):sample.paste(frames[i].convert('RGB'),(0,j*frames[0].height))
 pal=sample.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
 fs=[im.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE) for im in frames]
 fs[0].save(p,save_all=True,append_images=fs[1:],duration=ds,loop=0,disposal=1,optimize=False)

def decode(p):
 im=Image.open(p);out=[];t=0
 for i in range(im.n_frames):
  im.seek(i);t+=round(im.info['duration']);out.append((t,im.convert('RGBA').copy()))
 return out

def at(frames,t):return next(f for e,f in frames if t<e)

def main():
 report=[];selected=[]
 for k,s in enumerate(SPECS):
  sid=s['id'];src=ROOT/'source/animation'/sid;out=ROOT/'stickers'/sid;out.mkdir(parents=True,exist_ok=True)
  frames,box=prepare(k,s);cap,hh=caption(s['lines']);save(cap,src/'caption.png')
  order=list(range(6));ds=[360,180,180,180,180,1920]
  if k==2:order=[0,1,2,3,4,5,1,2,3,4,5,0];ds=[160]*11+[1240]
  if k==3:ds=[420,180,240,220,220,1720]
  if k==4:order=[0,1,2,3,2,3,4,5,6,7,8,9];ds=[300,160,130,130,130,130,180,160,160,160,160,1200]
  if k==5:ds=[360,180,200,220,220,1820]
  if k==6:ds=[300,160,180,180,200,1980]
  arts=[frames[i] for i in order]
  if k==2:arts=[snow(f,i,box) for i,f in enumerate(arts)]
  if k==3:arts=[chair_label(f,box) for f in arts]
  if k==0:
   order=list(range(6))+[5,5];ds=[360,180,180,180,180,120,120,1680]
   arts=frames[:5]+[sparkle(frames[5],8,box),sparkle(frames[5],18,box),sparkle(frames[5],12,box)]
  masters=[compose(f,cap,hh) for f in arts]
  display=[f.resize((400,400),Image.Resampling.LANCZOS) for f in masters]
  delivery=[]
  for im in masters:
   tile=Image.new('RGBA',(320,270));tile.alpha_composite(im.resize((260,260),Image.Resampling.LANCZOS),(30,5));delivery.append(tile)
  p=out/'sticker.png'
  delivery[0].save(p,save_all=True,append_images=delivery[1:],duration=ds,loop=1,disposal=0,blend=0,optimize=True,compress_level=9)
  # Representative still is final gesture, except two-level quote/beckon.
  hero=0 if k in [3] else 3 if k==6 else len(masters)-1
  save(masters[hero],out/'master.png');save(display[hero],out/'still.png')
  save(masters[0],out/'start.png');save(masters[-1],out/'end.png')
  st=Image.new('RGBA',(370,320));st.alpha_composite(masters[hero].resize((310,310),Image.Resampling.LANCZOS),(30,5));save(st,ROOT/'static/images'/f'{k+1:02d}.png')
  white=[]
  for f in display:
   w=Image.new('RGBA',f.size,'white');w.alpha_composite(f);white.append(w.convert('RGB'))
  gif(white,ds,out/'preview.gif')
  actual=decode(p)
  report.append({'id':sid,'caption':s['caption'],'motion':NAMES[k],'frames':len(actual),'durationMs':sum(ds),'plays':1,'bytes':p.stat().st_size,'headerHeight1200':hh,'poseOrder':order,'durations':ds,'source':f'source/animation/{sid}/keyframes.png','commonCrop':box,'method':'generated keyframes; rigid registration; fixed-background compositing; no body warp'})
  selected.append(masters[hero]);print('Rendered',sid,len(actual),p.stat().st_size,flush=True)
 # Synchronize review composites by elapsed time, decoded FROM final APNGs.
 decoded=[decode(ROOT/'stickers'/s['id']/'sticker.png') for s in SPECS]
 times=sorted({0,3000}|{end for fs in decoded for end,_ in fs});ds=[b-a for a,b in zip(times,times[1:])]
 for bg in ['white','black']:
  sheets=[]
  for t in times[:-1]:
   sh=Image.new('RGBA',(1280,540),bg)
   for k,fs in enumerate(decoded):sh.alpha_composite(at(fs,t),((k%4)*320,(k//4)*270))
   sheets.append(sh.convert('RGB'))
  gif(sheets,ds,ROOT/f'all-members-{bg}-preview.gif')
  still=Image.new('RGBA',(1280,540),bg);static=Image.new('RGBA',(1480,640),bg)
  for k,m in enumerate(selected):
   still.alpha_composite(m.resize((260,260),Image.Resampling.LANCZOS),((k%4)*320+30,(k//4)*270+5))
   static.alpha_composite(Image.open(ROOT/'static/images'/f'{k+1:02d}.png'),((k%4)*370,(k//4)*320))
  save(still.convert('RGB'),ROOT/f'all-members-{bg}-still.png');save(static.convert('RGB'),ROOT/f'static/preview-{bg}.png')
 (ROOT/'reports/render.json').write_text(json.dumps({'members':report,'previewSource':'decoded delivery APNG','font':FONT,'durationMs':3000,'method':'generated sequential pose sheets'},ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
