"""Three generated-pose motion candidates, separate from adopted set."""
import json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import build as b
ROOT=b.ROOT;OUT=ROOT/'drafts/elbow-weight'
labels=['A 軽く預ける','B 肘側へもたれる','C ゆっくり預ける']
delays=[[300,120,120,120,120,2220],[400,140,140,140,140,2040],[700,200,240,260,240,1360]]
allframes=[];report=[]
for k,name in enumerate('ABC'):
 d=OUT/name;sheet=Image.open(d/'keyframes.png').convert('RGBA');cw=sheet.width//3;ch=sheet.height//2
 fs=[b.clean(b.fit_cell(sheet.crop((i%3*cw,i//3*ch,(i%3+1)*cw,(i//3+1)*ch)))) for i in range(6)]
 base=fs[0];regs=[];aligned=[base]
 for im in fs[1:]:
  im,r=b.register(base,im,[(20,410,100,65),(390,420,95,50)],64);aligned.append(im);regs.append(r)
 # Only chest/shoulder girdle, neck and head may settle; arms/hands/beer are fixed.
 mask=Image.new('L',(512,512));dr=ImageDraw.Draw(mask)
 dr.polygon([(185,40),(395,40),(395,215),(465,240),(485,280),(385,300),(300,325),(260,350),(140,350),(145,270),(185,235)],fill=255)
 mask=mask.filter(ImageFilter.GaussianBlur(1.3))
 fs=[Image.composite(im,base,mask) for im in aligned]
 for i,f in enumerate(fs):b.save(f,d/'poses'/f'{i:02d}.png')
 bb=[f.getbbox() for f in fs];box=(min(x[0] for x in bb),min(x[1] for x in bb),max(x[2] for x in bb),max(x[3] for x in bb));fs=[f.crop(box) for f in fs]
 cap,hh=b.caption(['ちゃんと','働いてるか？']);masters=[b.compose(f,cap,hh) for f in fs];display=[f.resize((400,400),Image.Resampling.LANCZOS) for f in masters]
 for bg in ['white','black']:
  rgb=[]
  for f in display:
   z=Image.new('RGBA',f.size,bg);z.alpha_composite(f);rgb.append(z.convert('RGB'))
  b.gif(rgb,delays[k],d/f'preview-{bg}.gif')
 display[0].save(d/'still.png');delivery=[]
 for f in masters:
  z=Image.new('RGBA',(320,270));z.alpha_composite(f.resize((260,260),Image.Resampling.LANCZOS),(30,5));delivery.append(z)
 delivery[0].save(d/'sticker.png',save_all=True,append_images=delivery[1:],duration=delays[k],loop=1,disposal=0,blend=0)
 total=0;timed=[]
 for delay,f in zip(delays[k],display):total+=delay;timed.append((total,f))
 allframes.append(timed)
 # Verify hands are identical before common crop (not a fake body deformation).
 final=Image.open(d/'poses/05.png');first=Image.open(d/'poses/00.png');a=np.array(first);z=np.array(final)
 fixed=np.array(mask)==0
 assert np.array_equal(a[fixed],z[fixed]);assert total==3000
 changes=[int(np.count_nonzero(np.any(np.array(Image.open(d/'poses'/f'{i:02d}.png'))!=a,axis=2))) for i in range(6)]
 assert max(changes)>100
 report.append({'id':name,'delays':delays[k],'registration':regs,'changedPixels':changes,'fixedOutsideChestHeadMask':True,'method':'generated poses; fixed arms composite; no deformation'})
 for f in [d/'preview-white.gif',d/'sticker.png']:subprocess.run(['ffmpeg','-v','error','-i',str(f),'-f','null','-'],check=True,capture_output=True)
font=ImageFont.truetype(b.FONT,24,index=0);times=sorted({0,3000}|{t for fs in allframes for t,_ in fs});ds=[y-x for x,y in zip(times,times[1:])]
for bg in ['white','black']:
 sheets=[]
 for t in times[:-1]:
  sh=Image.new('RGBA',(1200,450),bg);dr=ImageDraw.Draw(sh)
  for k,fs in enumerate(allframes):
   dr.text((k*400+25,8),labels[k],font=font,fill='black' if bg=='white' else 'white');sh.alpha_composite(b.at(fs,t),(k*400,50))
  sheets.append(sh.convert('RGB'))
 b.gif(sheets,ds,OUT/f'comparison-{bg}.gif');sheets[0].save(OUT/f'comparison-{bg}.png')
(OUT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Created 3 elbow-weight candidates and comparison GIFs')
