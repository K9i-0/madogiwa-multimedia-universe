from pathlib import Path
import subprocess,json,wave
import numpy as np
P=Path(__file__).resolve().parent;E=P.parent;m=json.loads((P/'src/edit-manifest.json').read_text());movie=E/'final_remotion_project_intro_v3.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(movie)]));v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio');errors=[]
if int(v['nb_read_frames'])!=m['composition']['durationInFrames']:errors.append('frame count')
if (v['width'],v['height'],v['r_frame_rate'])!=(1280,720,'30/1'):errors.append('video format')
if a['sample_rate']!='48000':errors.append('sample rate')
decode=subprocess.run(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'],capture_output=True,text=True)
if decode.returncode or decode.stderr:errors.append('decode '+decode.stderr)
with wave.open(str(P/'public/mixed.wav')) as w:x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).astype(float)/32768
if np.max(np.abs(x[:6*48000]))<.001:errors.append('missing intro audio')
levels=[]
for d in m['dialogue']:
 seg=x[d['startFrame']*1600:(d['startFrame']+d['durationInFrames'])*1600];rms=float(np.sqrt(np.mean(seg**2)));levels.append(dict(id=d['id'],rmsDb=round(20*np.log10(max(rms,1e-9)),2),peak=float(np.max(np.abs(seg)))))
 if rms<.002:errors.append('silent dialogue '+d['id'])
if np.max(np.abs(x))>=.999:errors.append('clipping')
# Final encoded samples: each layout, source clip boundaries and the final frames.
(P/'out/final-audit').mkdir(exist_ok=True)
frames={}
for d in m['dialogue']:frames.setdefault(d['view'],d['startFrame']+min(35,d['durationInFrames']-1))
revision=json.loads((E/'revision_v3.json').read_text())
changed={d['id'] for d in revision['changedDialogue']}
for d in m['dialogue']:
 if d['id'] in changed:frames['changed-'+d['id']]=d['startFrame']+min(35,d['durationInFrames']-1)
for c in m['clips']:
 for label,f in [('before',c['startFrame']-1),('start',c['startFrame']),('end',c['startFrame']+c['durationInFrames']-1),('after',c['startFrame']+c['durationInFrames'])]:frames[f'clip-{label}']=f
frames['last']=m['composition']['durationInFrames']-1
for label,f in frames.items():subprocess.run(['ffmpeg','-v','error','-y','-ss',str(f/30),'-i',str(movie),'-frames:v','1',str(P/'out/final-audit'/f'{label}.jpg')],check=True)
report=dict(errors=errors,file=movie.name,video=dict(codec=v['codec_name'],width=v['width'],height=v['height'],fps=v['r_frame_rate'],frames=v['nb_read_frames']),audio=dict(codec=a['codec_name'],sampleRate=a['sample_rate']),durationSeconds=m['composition']['durationInFrames']/30,decodePassed=decode.returncode==0,introSixSecondsSilent=not np.any(x[:6*48000]),peak=float(np.max(np.abs(x))),dialogueLevels=levels,visualSamples=len(frames),subjectiveListening='not_performed',continuousVisualPlayback='not_performed')
(E/'qa_final.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='dialogueLevels'},ensure_ascii=False));assert not errors
