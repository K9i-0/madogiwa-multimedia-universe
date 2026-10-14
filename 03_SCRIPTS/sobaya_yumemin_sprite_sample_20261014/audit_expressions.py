from pathlib import Path
import subprocess,json,hashlib
EP=Path(__file__).resolve().parent;v=EP/'final_remotion_expressions.mp4';d=json.loads((EP/'remotion/src/manifest_expressions.json').read_text());old=json.loads((EP/'remotion/src/manifest_hau.json').read_text())
assert [(x['audio'],x['start'],x['frames']) for x in d['lines']]==[(x['audio'],x['start'],x['frames']) for x in old['lines']]
def pcm(path):return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-f','s16le','-acodec','pcm_s16le','-'])
same=pcm(v)==pcm(EP/'final_remotion_sample_hau.mp4')
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(v)]));vs=next(s for s in info['streams'] if s['codec_type']=='video');assert (vs['width'],vs['height'],int(vs['nb_read_frames']))==(1280,720,d['composition']['durationInFrames'])
subprocess.run(['ffmpeg','-v','error','-i',str(v),'-f','null','-'],check=True)
frames=[];counts=[]
for i,line in enumerate(d['lines']):
 if line['who']=='sobaya':
  states=[]
  for t in range(line['frames']):
   en=line['energy'][t]*.6+line['energy'][max(0,t-1)]*.25+line['energy'][max(0,t-2)]*.15
   states.append(en>.09 and (t//3)%3!=2)
  changes=sum(a!=b for a,b in zip(states,states[1:]));assert changes>=4
  opened=next(t for t in range(8,len(states)-1) if states[t]);closed=next(t for t in range(opened+1,len(states)) if not states[t]);frames.extend([(f'{line["pose"]}_open',line['start']+opened),(f'{line["pose"]}_closed',line['start']+closed)])
  counts.append({'pose':line['pose'],'openFrames':sum(states),'stateChanges':changes})
 else:frames.append((f'yumemin_{line["yumeminExpression"]}_{i}',line['start']+20))
for name,frame in frames:subprocess.run(['ffmpeg','-y','-v','error','-i',str(v),'-vf',f'select=eq(n\\,{frame})','-frames:v','1',str(EP/f'remotion/out/expression_{name}.png')],check=True)
report={'durationFrames':d['composition']['durationInFrames'],'width':1280,'height':720,'fps':30,'fullDecode':'passed','audioPCMIdenticalToAcceptedHau':same,'mouthMotion':counts,'auditoryReview':'User accepted previous Hau audio; this revision preserves audio','frames':frames}
(EP/'qa_expressions.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
assert same
