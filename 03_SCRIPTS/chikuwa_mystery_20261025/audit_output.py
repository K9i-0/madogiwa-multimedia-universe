from pathlib import Path
import subprocess,json,re,hashlib,wave
P=Path(__file__).resolve().parent;D=P/'remotion';f=P/'final_remotion_chikuwa_mystery_v9.mp4';m=json.loads((D/'src/edit-manifest.json').read_text())
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
# All generated B-roll is real 480p/24fps footage; source audio is excluded by the React components.
h3=[]
for i in range(1,6):
 source=P/f'h3_v9/results/ch{i:02}_480p.mp4'
 hp=json.loads(run(['ffprobe','-v','error','-show_streams','-of','json',str(source)]).stdout)
 hv=next(s for s in hp['streams'] if s['codec_type']=='video')
 assert (hv['width'],hv['height'],hv['avg_frame_rate'])==(864,480,'24/1')
 h3.append(dict(file=str(source.relative_to(P)),frames=hv['nb_frames'],sha256=hashlib.sha256(source.read_bytes()).hexdigest(),mutedInEdit=True))
# Extract every view, every original-audio clip and every subtitle midpoint in a single decode.
points=sorted(set([m['codaStartFrame']+90,m['codaStartFrame']+330,m['codaStartFrame']+510,0,m['composition']['durationInFrames']-1]+[v['startFrame']+30 for v in m['views']]+[c['startFrame']+c['durationInFrames']//2 for c in m['clips']]+[(c['startFrame']+c['endFrame'])//2 for c in caps]))
points=sorted(set(points+[m['cues'][key]+delta for key in ['chargeReveal','logicReveal','absenceReveal','lifeReveal','teacherReveal'] for delta in [-1,15]]))
out=D/'out/final_audit_v9';out.mkdir(exist_ok=True)
sel='+'.join(f'eq(n\\,{n})' for n in points)
run(['ffmpeg','-v','error','-y','-i',str(f),'-vf',f'select={sel}', '-fps_mode','vfr',str(out/'frame_%03d.jpg')])
(out/'frames.json').write_text(json.dumps(points))
report={'h3Sources':h3,'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'durationSeconds':m['composition']['durationInFrames']/30,'frames':v['nb_read_frames'],'resolution':[v['width'],v['height']],'fps':v['avg_frame_rate'],'sampleRate':a['sample_rate'],'fullDecode':'passed','loudness':metrics,'captionTextExact':True,'maxCaptionLines':2,'dialogueCount':len(m['dialogue']),'viewSegments':len(m['views']),'sourceClips':len(m['clips']),'voiceClipOverlap':False,'auditedFrameExtractionCount':len(points),'visualPreviewInspection':'See visual_audit_v9.md for inspected frames','listeningVerified':False,'limitations':['Human continuous listening and real-time lip-sync review not performed.']}
(P/'audit_v9.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
