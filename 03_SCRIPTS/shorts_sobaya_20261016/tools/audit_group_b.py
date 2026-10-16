import pathlib,json,subprocess,hashlib,math,sys
from PIL import Image,ImageDraw
base=pathlib.Path(__file__).resolve().parents[1];root=base.parents[1];rows=json.loads((base/'group-b.json').read_text());selected=set(sys.argv[1:])
for row in rows:
 if selected and row['slug'] not in selected:continue
 p=root/row['output'];d=p.parent
 if not p.exists():continue
 m=json.loads((d/'shorts-manifest.json').read_text());qa=d/'qa';qa.mkdir(exist_ok=True)
 pr=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));v=next(x for x in pr['streams'] if x['codec_type']=='video');frames=int(v['nb_frames'])
 dec=subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(p),'-f','null','-'],capture_output=True,text=True)
 def ah(f):return subprocess.check_output(['ffmpeg','-v','error','-threads','2','-i',str(f),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()
 orig=ah(root/row['source']);out=ah(p)
 points=sorted(set([0,frames-1,frames//4,frames//2,frames*3//4]+[(c['startFrame']+c['endFrame'])//2 for c in m['captions']]))
 expr='+'.join(f'eq(n\\,{n})' for n in points)
 subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(p),'-vf',f'select={expr},scale=270:480','-fps_mode','vfr','-y',str(qa/'frame-%03d.jpg')],check=True)
 imgs=sorted(qa.glob('frame-*.jpg'));pages=[]
 for page in range(math.ceil(len(imgs)/12)):
  batch=imgs[page*12:(page+1)*12];can=Image.new('RGB',(1080,510*math.ceil(len(batch)/4)),'#202020');dr=ImageDraw.Draw(can)
  for i,fp in enumerate(batch):
   can.paste(Image.open(fp),((i%4)*270,(i//4)*510+25));at=points[page*12+i];dr.text(((i%4)*270+4,(i//4)*510+5),f'{at}f / {at/24:.2f}s',fill='white')
  name=qa/f'contact-{page+1}.jpg';can.save(name);pages.append(str(name.relative_to(root)))
 report={'manifestSha256':hashlib.sha256((d/'shorts-manifest.json').read_bytes()).hexdigest(),'slug':row['slug'],'output':row['output'],'dimensions':[v['width'],v['height']],'fps':v['r_frame_rate'],'sourceFrames':m['durationInFrames'],'outputFrames':frames,'durationSeconds':float(pr['format']['duration']),'sourceAudioBitstreamHash':orig,'outputAudioBitstreamHash':out,'audioBitstreamIdentical':orig==out,'fullDecodeExitCode':dec.returncode,'decodeStderr':dec.stderr,'captionCount':len(m['captions']),'sampleFrames':points,'contactSheets':pages,'outputSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'visualReview':'pending','reviewMethod':'Source representative frames; prompt and reference audio alignment; final caption midpoint/representative image inspection. No full human listening claim.'}
 (d/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(row['slug'],len(points),orig==out,dec.returncode,flush=True)
