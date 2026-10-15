"""Reproducible layered sticker renderer. Run with ../.venv/bin/python.

Fresh artwork is immutable. Typography is rendered directly into RGBA; its
counters never contain a white matte. Motion fields and effects are independent
of captions. APNGs retain continuous alpha; GIFs are review composites only.
"""
import json, math, shutil, struct, subprocess, zlib
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build'
FONT = '/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc'
SPECS = json.loads((ROOT/'source/redraw-manifest.json').read_text())
LINES = [ ['おはよう'], ['乾杯！'], ['冷えてる。','待遇も。'],
 ['窓際に追い込まれて','いるうちは二流'],
 ['一流の窓際族は','窓際を作り出す'], ['二日酔い'], ['飲みに行こう'], ['禁酒中'] ]
MOTIONS = [
 {'name':'手を振り、口元の輝きが明滅', 'fields':[[.73,.24,.14,.20,.035,0,2]], 'sparkle':[.606,.244]},
 {'name':'乾杯のジャンプを2回', 'jump':True},
 {'name':'上半身が寒さで震え、雪が流れる', 'fields':[[.49,.40,.22,.24,.010,0,7]], 'snow':True},
 {'name':'仮面を固定したまま腕組みした肩がわずかに上下', 'fields':[[.40,.48,.25,.20,0,.012,1]]},
 {'name':'ドリルと手元が小刻みに振動', 'fields':[[.50,.65,.14,.11,.012,.003,8]]},
 {'name':'横たわった胸が小さく呼吸し、頭上の線が揺れる', 'breath':[.50,.37,.23,.15], 'dizzy':True},
 {'name':'手招きし、投げた書類がひらひら動く', 'fields':[[.72,.31,.16,.12,.018,-.009,2],[.24,.16,.16,.13,-.010,-.022,1],[.26,.40,.14,.18,.018,-.026,1],[.73,.68,.12,.11,.014,-.018,1]]},
 {'name':'点滴の滴とビールの泡が動き、ゆっくり呼吸', 'breath':[.60,.52,.25,.12], 'drip':True},
]
DURATIONS = [80]*23+[1160]
N = len(DURATIONS)

def save(im,p):
 p.parent.mkdir(parents=True,exist_ok=True); im.save(p)

def clean_art(src):
 im=np.array(Image.open(src).convert('RGBA')); a=im[:,:,3].copy()
 n,lab,stats,_=cv2.connectedComponentsWithStats((a>35).astype('uint8'),8)
 keep=np.zeros(a.shape,'uint8')
 for k in range(1,n):
  if stats[k,cv2.CC_STAT_AREA]>=24: keep[lab==k]=1
 keep=cv2.dilate(keep,np.ones((3,3),'uint8'))
 a[keep==0]=0; a[a<16]=0
 # Keep original continuous alpha, but replace white/cyan contaminated RGB on
 # outer soft edges by the nearest opaque source colour, as in set 01 matte.
 core=a>=245
 _,idx=distance_transform_edt(~core,return_indices=True)
 edge=(a>0)&(a<245)
 im[:,:,:3][edge]=im[idx[0],idx[1],:3][edge]
 im[:,:,3]=a; im[a==0,:3]=0
 return Image.fromarray(im)

def outline(im,radius):
 # White stroke behind ALL ink silhouettes, continuous antialiased boundary.
 a=im.getchannel('A')
 stroke=a.filter(ImageFilter.MaxFilter(2*radius+1)).filter(ImageFilter.GaussianBlur(.45))
 bg=Image.new('RGBA',im.size,'white'); bg.putalpha(stroke)
 return Image.alpha_composite(bg,im)

def caption(lines,size=1200):
 out=Image.new('RGBA',(size,size),(0,0,0,0)); d=ImageDraw.Draw(out)
 fsize=205 if len(lines)==1 else 127
 while True:
  f=ImageFont.truetype(FONT,fsize,index=0)
  if max(d.textbbox((0,0),s,font=f)[2] for s in lines)<size-70: break
  fsize-=1
 y=20
 for s in lines:
  b=d.textbbox((0,0),s,font=f); w=b[2]-b[0]; h=b[3]-b[1]
  d.text(((size-w)/2-b[0],y-b[1]),s,font=f,fill='black',stroke_width=6,stroke_fill='white')
  y+=h+18
 return out,y+12

def remap_premult(im,mx,my):
 arr=np.asarray(im).astype('float32')/255
 arr[:,:,:3]*=arr[:,:,3:4]
 v=cv2.remap(arr,mx,my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
 v[:,:,3]=np.clip(v[:,:,3],0,1)
 v[:,:,:3]=np.clip(v[:,:,:3]/np.maximum(v[:,:,3:4],1e-6),0,1)
 return Image.fromarray(np.rint(v*255).astype('uint8'))

def render_motion(im,kind,i):
 w,h=im.size; yy,xx=np.mgrid[0:h,0:w].astype('float32')
 phase=0 if i==N-1 else i/(N-1)*2*math.pi
 # Last image and first image intentionally match exactly before long pause.
 dx=np.zeros_like(xx);dy=dx.copy();spec=MOTIONS[kind]
 def fall(cx,cy,rx,ry):
  q=((xx/w-cx)/rx)**2+((yy/h-cy)/ry)**2
  return np.maximum(0,1-q)**2
 for cx,cy,rx,ry,ax,ay,freq in spec.get('fields',[]):
  wt=fall(cx,cy,rx,ry);t=math.sin(phase*freq)
  dx+=wt*ax*w*t;dy+=wt*ay*h*t
 if 'head' in spec:
  cx,cy,rx,ry=spec['head'];wt=fall(cx,cy,rx,ry)
  angle=math.radians(4)*math.sin(phase)
  dx+=-(yy-cy*h)*angle*wt;dy+=(xx-cx*w)*angle*wt
 if 'breath' in spec:
  cx,cy,rx,ry=spec['breath'];wt=fall(cx,cy,rx,ry)
  dy-=wt*.012*h*(1-math.cos(phase))/2
 if spec.get('jump'):
  lift=(1-math.cos(phase*2))/2
  dy-=h*.045*lift
  dx+=(xx-w*.5)*.022*lift
 result=remap_premult(im,xx-dx,yy-dy)
 layer=Image.new('RGBA',(w,h));d=ImageDraw.Draw(layer)
 if 'sparkle' in spec:
  cx,cy=spec['sparkle'];cx*=w;cy*=h
  r=(.018+.018*(1-math.cos(phase*2))/2)*w
  points=[(cx,cy-r),(cx+r*.23,cy-r*.23),(cx+r,cy),(cx+r*.23,cy+r*.23),(cx,cy+r),(cx-r*.23,cy+r*.23),(cx-r,cy),(cx-r*.23,cy-r*.23)]
  d.polygon(points,fill=(255,202,25,210),outline=(255,255,255,255),width=max(1,w//300))
 if spec.get('snow'):
  for k in range(12):
   x=(.16+(k*.137)% .74)*w+(math.sin(phase+k)-math.sin(k))*w*.018
   y=(.12+(k*.113)%.72)*h+(1-math.cos(phase))*h*.025
   r=w*.0035;d.ellipse((x-r,y-r,x+r,y+r),fill=(255,255,255,190))
 if spec.get('dizzy'):
  for cx in [.37,.66]:
   x=cx*w; y=(.08+.008*math.sin(phase*2))*h
   pts=[(x+math.sin(t/2+phase)*w*.005,y+t*h*.004) for t in range(15)]
   d.line(pts,fill='white',width=max(3,w//90));d.line(pts,fill=(45,45,45,255),width=max(1,w//180))
 if spec.get('drip'):
  # Tiny gold drop inside existing chamber, and white bubbles inside beer.
  p=(i/(N-1)*3)%1 if i!=N-1 else 0
  x=.215*w;y=(.400+.025*p)*h;r=w*.004
  d.ellipse((x-r,y-r*1.4,x+r,y+r*1.4),fill=(234,159,0,255))
  for k in range(6):
   x=(.19+(k%3)*.031)*w
   y=(.17+((k*.023-.035*math.sin(phase))%.12))*h
   r=w*.0025;d.ellipse((x-r,y-r,x+r,y+r),fill=(255,247,198,230))
 # Effects stay within the scene's original silhouette.
 la=np.asarray(layer).copy();la[:,:,3]=(la[:,:,3].astype('float32')*np.asarray(im)[:,:,3]/255).astype('uint8')
 return Image.alpha_composite(result,Image.fromarray(la))

def compose(art,cap,header,size=1200):
 out=Image.new('RGBA',(size,size))
 room=size-header-32
 scale=min((size-60)/art.width,room/art.height)
 a=art.resize((round(art.width*scale),round(art.height*scale)),Image.Resampling.LANCZOS)
 a=outline(a,4)
 x=(size-a.width)//2;y=header+(room-a.height)//2
 out.alpha_composite(a,(x,y));out=Image.alpha_composite(out,cap)
 return out

def gif(frames,durations,dst):
 # Shared palette prevents frame-to-frame colour shimmer. Background composites
 # are RGB, so GIF's single-bit transparency never destroys soft alpha edges.
 contact=Image.new('RGB',(frames[0].width,frames[0].height*3))
 for j,k in enumerate([0,6,12]):contact.paste(frames[k].convert('RGB'),(0,j*frames[0].height))
 palette=contact.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
 fs=[f.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
 fs[0].save(dst,save_all=True,append_images=fs[1:],duration=durations,loop=0,optimize=False,disposal=1)

def apng(frames,dst):
 frames[0].save(dst,save_all=True,append_images=frames[1:],duration=DURATIONS,loop=1,disposal=0,blend=0,optimize=True,compress_level=9)
 if dst.stat().st_size>1000000:
  compact=[]
  for im in frames:
   a=np.array(im);a[:,:,:3]=np.minimum(255,((a[:,:,:3].astype('uint16')+2)//4)*4).astype('uint8');compact.append(Image.fromarray(a))
  compact[0].save(dst,save_all=True,append_images=compact[1:],duration=DURATIONS,loop=1,disposal=0,blend=0,optimize=True,compress_level=9)

def main():
 BUILD.mkdir(exist_ok=True);(ROOT/'reports').mkdir(exist_ok=True)
 report=[]
 (ROOT/'source/motion.json').write_text(json.dumps(MOTIONS,ensure_ascii=False,indent=2)+'\n')
 for k,s in enumerate(SPECS):
  sid=s['id'];src=ROOT/'source'/sid;work=BUILD/sid;out=ROOT/'stickers'/sid
  work.mkdir(exist_ok=True);out.mkdir(parents=True,exist_ok=True)
  art=clean_art(src/'art-generated.png');save(art,src/'art.png')
  cap,hh=caption(LINES[k]);save(cap,src/'caption.png')
  # 720px artwork rendering is supersampled against delivery dimensions.
  motionbase=art.resize((720,720),Image.Resampling.LANCZOS)
  display=[];delivery=[]
  for i in range(N):
   moving=render_motion(motionbase,k,i)
   master=compose(moving,cap,hh)
   if i==0:
    save(master,out/'master.png')
    stat=master.resize((310,310),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',(370,320));canvas.alpha_composite(stat,(30,5))
    save(canvas,ROOT/'static/images'/f'{k+1:02d}.png')
   show=master.resize((400,400),Image.Resampling.LANCZOS);save(show,work/f'display{i:02d}.png');display.append(show)
   tile=Image.new('RGBA',(320,270));tile.alpha_composite(master.resize((260,260),Image.Resampling.LANCZOS),(30,5));delivery.append(tile)
  save(display[0],out/'still.png');apng(delivery,out/'sticker.png')
  white=[]
  for im in display:
   b=Image.new('RGBA',im.size,'white');b.alpha_composite(im);white.append(b.convert('RGB'))
  gif(white,DURATIONS,out/'preview.gif')
  report.append({'id':sid,'caption':s['caption'],'motion':MOTIONS[k]['name'],'frames':Image.open(out/'sticker.png').n_frames,'durationMs':3000,'plays':1,'bytes':(out/'sticker.png').stat().st_size,'headerHeight1200':hh})
  print('Rendered',sid,report[-1]['bytes'],flush=True)
 # Audit GIFs are generated FROM DELIVERED APNGs, not from different sources.
 decoded=[]
 for s in SPECS:
  im=Image.open(ROOT/'stickers'/s['id']/'sticker.png');frames=[];ends=[];end=0
  for i in range(im.n_frames):
   im.seek(i);frames.append(im.convert('RGBA').copy());end+=im.info['duration'];ends.append(end)
  # Encoder may merge identical consecutive frames. Sample by elapsed time,
  # never by frame index, so all exported stickers stay synchronized.
  decoded.append([frames[next(j for j,e in enumerate(ends) if t<e)] for t in np.cumsum([0]+DURATIONS[:-1])])
 for bg in ['white','black']:
  sheets=[]
  for i in range(N):
   sheet=Image.new('RGBA',(1280,540),bg)
   for k in range(8):sheet.alpha_composite(decoded[k][i],((k%4)*320,(k//4)*270))
   sheets.append(sheet.convert('RGB'))
  gif(sheets,DURATIONS,ROOT/f'all-members-{bg}-preview.gif')
  save(sheets[0],ROOT/f'all-members-{bg}-still.png')
  sheet=Image.new('RGBA',(1480,640),bg)
  for k in range(8):sheet.alpha_composite(Image.open(ROOT/'static/images'/f'{k+1:02d}.png'),((k%4)*370,(k//4)*320))
  save(sheet.convert('RGB'),ROOT/f'static/preview-{bg}.png')
 (ROOT/'reports/render.json').write_text(json.dumps({'members':report,'delays':DURATIONS,'previewSource':'decoded delivery APNG','font':FONT},ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
