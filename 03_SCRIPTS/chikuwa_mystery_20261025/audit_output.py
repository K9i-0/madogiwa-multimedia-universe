from pathlib import Path
import subprocess,json,re,hashlib,wave
P=Path(__file__).resolve().parent;D=P/'remotion';f=P/'final_remotion_chikuwa_mystery_v4.mp4';m=json.loads((D/'src/edit-manifest.json').read_text())
def run(args):return subprocess.run(args,check=True,capture_output=True,text=True)
probe=json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(f)]).stdout)
v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_read_frames']))==(1280,720,'30/1',m['composition']['durationInFrames'])
assert a['sample_rate']=='48000'
r=run(['ffmpeg','-v','error','-i',str(f),'-f','null','-']);assert not r.stderr.strip(),r.stderr
l=run(['ffmpeg','-hide_banner','-i',str(f),'-af','loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-vn','-f','null','-'])
metrics=json.JSONDecoder().raw_decode(l.stderr[l.stderr.rfind('{'):])[0];assert float(metrics['input_tp'])<0
caps=m['captions'];assert all(len(c['text'].split('\n'))<=2 and max(map(len,c['text'].split('\n')))<=32 for c in caps)
assert ''.join(c['text'].replace('\n','') for c in caps)==''.join(d['text'] for d in m['dialogue'])
for c in m['clips']:
 assert not any(d['startFrame']<c['startFrame']+c['durationInFrames'] and d['startFrame']+d['durationInFrames']>c['startFrame'] for d in m['dialogue'])
for d in m['dialogue']:
 with wave.open(str(P/d['audio'])) as w:assert w.getnframes()>0 and w.getframerate()==24000
# Extract every view, every original-audio clip and every subtitle midpoint in a single decode.
points=sorted(set([0,m['composition']['durationInFrames']-1]+[v['startFrame']+30 for v in m['views']]+[c['startFrame']+c['durationInFrames']//2 for c in m['clips']]+[(c['startFrame']+c['endFrame'])//2 for c in caps]))
out=D/'out/final_audit_v4';out.mkdir(exist_ok=True)
sel='+'.join(f'eq(n\\,{n})' for n in points)
run(['ffmpeg','-v','error','-y','-i',str(f),'-vf',f'select={sel}', '-fps_mode','vfr',str(out/'frame_%03d.jpg')])
(out/'frames.json').write_text(json.dumps(points))
report={'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'durationSeconds':m['composition']['durationInFrames']/30,'frames':v['nb_read_frames'],'resolution':[v['width'],v['height']],'fps':v['avg_frame_rate'],'sampleRate':a['sample_rate'],'fullDecode':'passed','loudness':metrics,'captionTextExact':True,'maxCaptionLines':2,'dialogueCount':len(m['dialogue']),'viewSegments':len(m['views']),'sourceClips':len(m['clips']),'voiceClipOverlap':False,'auditedFrameExtractionCount':len(points),'visualPreviewInspection':'See visual_audit_v4.md for inspected frames','listeningVerified':False,'limitations':['Human continuous listening and real-time lip-sync review not performed.']}
(P/'audit_v4.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
