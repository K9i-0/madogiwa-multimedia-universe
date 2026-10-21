from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
video=P.parent/'final_remotion_flutterkaigi_v1.mp4'
out=P/'out/final_audit';out.mkdir(parents=True,exist_ok=True)
m=json.loads((P/'src/edit-manifest.json').read_text())
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1280,720,'30/1',14706)
assert a['sample_rate']=='48000' and a['channels']==2
subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
frames={0,14705}; mids=[]
for d in m['dialogue']:
 for c in d['captions']:
  start=d['startFrame']+c['fromFrame'];end=d['startFrame']+c['toFrame']
  frames.update([start,max(start,end-1)]);mids.append((start+end)//2)
frames.update(mids)
frames=sorted(frames)
selection='+'.join(f'eq(n\\,{n})' for n in frames)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf',f'select={selection},scale=640:360','-fps_mode','vfr',str(out/'frame_%04d.jpg')],check=True)
lookup={f:out/f'frame_{i+1:04d}.jpg' for i,f in enumerate(frames)}
for part in range((len(mids)+19)//20):
 group=mids[part*20:(part+1)*20];sheet=Image.new('RGB',(2560,390*5),'white');draw=ImageDraw.Draw(sheet)
 for i,f in enumerate(group):
  x=(i%4)*640;y=(i//4)*390;sheet.paste(Image.open(lookup[f]),(x,y));draw.text((x+10,y+363),f'{f/30:.2f}s / frame {f}',fill='black')
 sheet.save(out/f'captions_{part}.jpg',quality=90)
(out/'report.json').write_text(json.dumps({'video':v,'audio':a,'decode':'passed','captions':len(mids),'checked_boundary_frames':frames,'subjective_listening':False},ensure_ascii=False,indent=2))
print(json.dumps({'frames':len(frames),'captions':len(mids),'duration':probe['format']['duration'],'bytes':probe['format']['size']}))
