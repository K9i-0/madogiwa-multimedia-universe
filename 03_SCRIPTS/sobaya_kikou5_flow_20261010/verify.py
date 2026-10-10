from pathlib import Path
import json,subprocess
p=Path(__file__).resolve().parent;m=json.loads((p/'remotion/src/edit-manifest.json').read_text());v=p/'final_remotion_kikou5_revision02.mp4'
d=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(v)]));vs=next(s for s in d['streams'] if s['codec_type']=='video');au=next(s for s in d['streams'] if s['codec_type']=='audio')
assert (vs['width'],vs['height'],vs['r_frame_rate'])==(1280,720,'30/1');assert int(vs['nb_read_frames'])==m['composition']['durationInFrames'];assert au['sample_rate']=='48000'
for c in m['clips']:
 assert not any(max(c['startFrame'],r['startFrame'])<min(c['startFrame']+c['durationInFrames'],r['startFrame']+r['durationInFrames']) for r in m['dialogue'])
subprocess.run(['ffmpeg','-v','error','-i',str(v),'-f','null','-'],check=True)
seen=set();frames=[]
for r in m['dialogue']:
 if r['visual'] not in seen:frames.append(r['startFrame']+min(25,r['durationInFrames']//2));seen.add(r['visual'])
frames += [c['startFrame']+c['durationInFrames']//2 for c in m['clips']]+[m['composition']['durationInFrames']-45]
frames.sort();out=p/'remotion/out'
filt='select='+ '+'.join(f'eq(n\\,{f})' for f in frames)+',scale=480:270,tile=4x7'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(v),'-vf',filt,'-frames:v','1',str(out/'contact.jpg')],check=True)
report=dict(width=vs['width'],height=vs['height'],frames=int(vs['nb_read_frames']),seconds=int(vs['nb_read_frames'])/30,fps=30,decode='pass',voiceLines=len(m['dialogue']),sourceClips=len(m['clips']),clipNarrationOverlap=False,listening='Not independently listened; ASR screening only',visualFrames=frames)
(p/'qa.json').write_text(json.dumps(report,indent=2));print(report)
