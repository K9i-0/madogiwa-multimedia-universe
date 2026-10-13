from pathlib import Path
import subprocess,json,sys
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
path=Path(sys.argv[1]) if len(sys.argv)>1 else P.parent/'final_remotion_members.mp4'
m=json.loads((P/'src/edit-manifest.json').read_text());fps=30
# Full decode, stream/frame counts, subtitle structure and exact text, no double voices.
subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','null','-'],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)]));v=next(x for x in probe['streams'] if x['codec_type']=='video');a=next(x for x in probe['streams'] if x['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'])==(1280,720,'30/1');assert int(v['nb_read_frames'])==m['composition']['durationInFrames'];assert a['sample_rate']=='48000'
for d in m['dialogue']:
 assert ''.join(c['text'].replace('\n','') for c in d['captions'])==d['text'],d['id']
 for c in d['captions']:
  assert len(c['text'].split('\n'))<=2,(d['id'],c)
  assert max(map(len,c['text'].split('\n')))<=31
  assert c['to']>c['from']
for c in m['clips']:
 assert all(c['startFrame']+c['durationInFrames']<=d['startFrame'] or c['startFrame']>=d['startFrame']+d['durationInFrames'] for d in m['dialogue'])
seen=set();samples=[]
for d in m['dialogue']:
 if d['view'] not in seen:samples.append((d['startFrame']+min(28,d['durationInFrames']-1),d['view']));seen.add(d['view'])
for c in m['clips']:
 samples.extend([(c['startFrame']+min(30,c['durationInFrames']-1),'clip '+c['id']+' in'),(c['startFrame']+c['durationInFrames']-2,'clip '+c['id']+' out')])
for cc in json.loads((P/'src/clip-captions.json').read_text()):
 c=next(c for c in m['clips'] if c['id']==cc['clip'])
 samples.append((c['startFrame']+(cc['from']+cc['to'])//2,'caption '+cc['clip']+' '+cc['who']))
# Long captions and all multi-page transitions, viewed in final encoded frames.
for d in m['dialogue']:
 if len(d['captions'])>1:
  for cap in d['captions']:samples.append((d['startFrame']+cap['from']+3,'page '+d['id']))
samples.append((m['creditsStartFrame']+20,'credits'))
out=P/'out'/path.stem;out.mkdir(exist_ok=True)
for i,(frame,label) in enumerate(samples):
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(frame/30),'-i',str(path),'-frames:v','1',str(out/f'{i:03}.jpg')],check=True)
for page,start in enumerate(range(0,len(samples),12)):
 sheet=Image.new('RGB',(1536,1280),'#ddd');draw=ImageDraw.Draw(sheet)
 for i,(frame,label) in enumerate(samples[start:start+12]):
  im=Image.open(out/f'{start+i:03}.jpg');im=im.resize((512,288));x=i%3*512;y=i//3*320;sheet.paste(im,(x,y+28));draw.text((x+5,y+6),f'{start+i:02} {frame/30:.2f}s {label}',fill='black')
 sheet.save(out/f'contact_{page}.jpg')
report={'path':str(path),'duration':probe['format']['duration'],'frames':v['nb_read_frames'],'resolution':[v['width'],v['height']],'fps':v['r_frame_rate'],'audioSampleRate':a['sample_rate'],'fullDecode':'passed','captionText':'exact','captionMaxLines':2,'captionMaxChars':31,'clipNarrationOverlap':False,'uniqueViews':len(seen),'sampledFrames':len(samples),'samples':samples,'subjectiveAudioReview':'not performed; numerical and ASR checks are separate'}
(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},ensure_ascii=False))
