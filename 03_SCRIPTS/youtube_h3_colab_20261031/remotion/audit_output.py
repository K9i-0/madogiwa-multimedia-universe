"""Check the delivered MP4 and extract every central layout and clip boundary."""
from pathlib import Path
import subprocess,json,wave
import numpy as np
P=Path(__file__).resolve().parent;E=P.parent
m=json.loads((P/'src/edit-manifest.json').read_text());movie=E/f'final_remotion_h3_colab_{m["revision"]}.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(movie)]))
v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio');errors=[]
if int(v['nb_read_frames'])!=m['composition']['durationInFrames']:errors.append('frame count')
if (v['width'],v['height'],v['r_frame_rate'])!=(1280,720,'30/1'):errors.append('video format')
if a['sample_rate']!='48000':errors.append('sample rate')
decode=subprocess.run(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'],capture_output=True,text=True)
if decode.returncode or decode.stderr:errors.append('decode '+decode.stderr)
with wave.open(str(P/'public/mixed.wav')) as w:
 x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).astype(np.float32)/32768
if len(x)!=m['composition']['durationInFrames']*1600:errors.append('mixed audio length')
levels=[]
for d in m['dialogue']:
 seg=x[d['startFrame']*1600:(d['startFrame']+d['durationInFrames'])*1600];rms=float(np.sqrt(np.mean(seg**2)))
 levels.append(dict(id=d['id'],rmsDb=round(20*np.log10(max(rms,1e-9)),2),peak=float(np.max(np.abs(seg)))))
 if rms<.002:errors.append('silent dialogue '+d['id'])
if np.max(np.abs(x))>=.999:errors.append('clipping')
frames={}
for d in m['dialogue']:frames.setdefault(d['view'],d['startFrame']+min(35,d['durationInFrames']-1))
for c in m['clips']:
 for label,f in [('before',c['startFrame']-1),('start',c['startFrame']),('end',c['startFrame']+c['durationInFrames']-1),('after',c['startFrame']+c['durationInFrames'])]:frames[f'{c["id"]}-{label}']=f
frames['last']=m['composition']['durationInFrames']-1
for c in m['chapters']:
 if c['cardFrames']:
  for label,offset in [('before',-1),('start',0),('fade-in',6),('middle',30),('fade-out',54),('end',59),('after',60)]:frames[f'chapter-{c["number"]}-{label}']=c['startFrame']+offset
out=P/f'out/final-audit-{m["revision"]}';out.mkdir(exist_ok=True)
for label,f in frames.items():
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(f/30),'-i',str(movie),'-frames:v','1',str(out/f'{label}.png')],check=True)
report=dict(errors=errors,file=movie.name,video=dict(codec=v['codec_name'],width=v['width'],height=v['height'],fps=v['r_frame_rate'],frames=v['nb_read_frames']),audio=dict(codec=a['codec_name'],sampleRate=a['sample_rate']),durationSeconds=m['composition']['durationInFrames']/30,decodePassed=decode.returncode==0,peak=float(np.max(np.abs(x))),dialogueLevels=levels,visualSamples=frames,subjectiveListening='not_performed',continuousVisualPlayback='not_performed',primaryVisualReview='representative layouts checked before render; final samples extracted for all layouts',pricingSource='research/pricing.json')
(E/f'qa_final_{m["revision"]}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['dialogueLevels','visualSamples']},ensure_ascii=False));assert not errors
