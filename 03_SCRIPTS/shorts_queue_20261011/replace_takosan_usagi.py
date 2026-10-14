"""Shorts-only voice revision. Reuses adopted background stems; no horizontal mutations.
Run with repository .local/Irodori-TTS/.venv/bin/python. Generation queries are
stored per episode; WAV files are adopted inputs. Render with render_usagi.mjs.
"""
from pathlib import Path
import json,hashlib,subprocess,urllib.request
import numpy as np
ROOT=Path(__file__).resolve().parents[2]; Q=Path(__file__).resolve().parent; SR=48000; SPF=1600
SPECS={'80_sobaya_clone_lab':dict(window=[348,751],starts=[361,469,548,638],ends=[429,529,635,750]),'85_pakurareta':dict(window=[198,426],starts=[209,254],ends=[253,386]),'84_madogiwa_tribe_origin':dict(window=[1024,1134],starts=[1029,1064,1110],ends=[1057,1093,1130])}
def read(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar',str(SR),'-ac','2','-f','f32le','-']),dtype='<f4').reshape(-1,2).copy()
def save(p,x):
 subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-c:a','pcm_s16le',str(p)],input=x.astype('<f4').tobytes(),check=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def loop(x,n,k):
 out=x.copy();f=np.linspace(0,1,k)[:,None]
 while len(out)<n:out=np.concatenate([out[:-k],out[-k:]*(1-f)+x[:k]*f,x[k:]])
 return out[:n]
for ep,s in SPECS.items():
 E=ROOT/'03_SCRIPTS'/ep; M=json.loads((E/'shorts-manifest.json').read_text()); O=E/'remotion/out/shorts-usagi';O.mkdir(parents=True,exist_ok=True)
 source=E/'final_remotion_shorts_9x16.mp4';original=read(source)[:M['durationInFrames']*SPF];mix=original.copy();a,b=[v*SPF for v in s['window']]
 if ep.startswith('80'):
  bed=read(E/'pod_ambience_loop.wav');bed*=10**(-36/20)/np.sqrt(np.mean(bed**2));bed=loop(bed,751*SPF,round(.2*SR))[a:b]
 elif ep.startswith('85'):
  # Same office ambience construction as adopted mix_audio.py.
  bed=read(ROOT/'.local/ep85-edit/separated/htdemucs/original/no_vocals.wav')
  office=loop(read(E/'office_typing_phones.wav')[:420*SPF],420*SPF,9*SPF)*10**(-6/20)
  office[:6*SPF]*=np.linspace(0,1,6*SPF)[:,None];office[-8*SPF:]*=np.linspace(1,0,8*SPF)[:,None]
  bed[:len(office)]+=office;bed=bed[a:b]
 else:
  # Past clip starts at output frame 444. Stem starts at past second 18.
  offset=(444+540)*SPF
  bed=read(ROOT/'.local/ep84-takosan-patch/separated/htdemucs/target/no_vocals.wav')[a-offset:b-offset]
 fade=np.ones((b-a,1));k=480;fade[:k]=np.linspace(0,1,k)[:,None];fade[-k:]=np.linspace(1,0,k)[:,None]
 mix[a:b]=original[a:b]*(1-fade)+bed*fade
 queries=json.loads((E/'shorts-usagi-queries.json').read_text());reports=[]
 # Match active speech RMS to the adopted voice in each episode.
 old=original[a:b]-bed;energy=np.mean(old**2,axis=1);oldrms=np.sqrt(np.mean(energy[energy>10**(-35/10)]))
 for i,(line,start,end) in enumerate(zip(queries['lines'],s['starts'],s['ends'])):
  wav=E/line['file']
  if not wav.exists():
   req=urllib.request.Request('http://127.0.0.1:50021/synthesis?speaker=61',data=json.dumps(line['query']).encode(),headers={'Content-Type':'application/json'})
   wav.write_bytes(urllib.request.urlopen(req,timeout=120).read())
  v=read(wav);energy=np.mean(v**2,axis=1);rms=np.sqrt(np.mean(energy[energy>10**(-35/10)]));gain=min(oldrms/rms,.8/np.max(np.abs(v)))
  at=start*SPF;assert at>=a and at+len(v)<=b
  mix[at:at+len(v)]+=v*gain
  reports.append(dict(file=wav.name,sha256=sha(wav),startFrame=start,endFrame=end,durationSamples=len(v),gainDb=float(20*np.log10(gain))))
 assert np.max(np.abs(mix))<1
 assert np.array_equal(mix[:a],original[:a]) and np.array_equal(mix[b:],original[b:])
 save(O/'mix.wav',mix)
 # AAC intermediate for copy mux on every render.
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(O/'mix.wav'),'-c:a','aac','-b:a','192k',str(O/'mix.m4a')],check=True)
 captions=[c for c in M['captions'] if c['speaker']=='たこさん']
 if len(captions)==len(reports):
  for c,r in zip(captions,reports):c.update(startFrame=r['startFrame'],endFrame=r['endFrame'])
 M['audioSource']=str((O/'mix.m4a').relative_to(ROOT));M['audioRevision']='shorts-only VOICEVOX:中国うさぎ / style61 / speed1.1 / pitch0'
 (E/'shorts-manifest-usagi.json').write_text(json.dumps(M,ensure_ascii=False,indent=2)+'\n')
 record=dict(engine='VOICEVOX 0.25.1',speaker=61,speedScale=1.1,pitchScale=0,sourceShorts=str(source.relative_to(ROOT)),sourceSha256=sha(source),horizontalSource=M['clips'][0]['source'],horizontalSha256=sha(ROOT/M['clips'][0]['source']),windowFrames=s['window'],lines=reports,peakDbfs=float(20*np.log10(np.max(np.abs(mix)))),outsideWindowPcmIdentical=True,timeStretch=False,fullQueryFile='shorts-usagi-queries.json',subjectiveListening=False,output='final_remotion_shorts_usagi_9x16.mp4')
 (E/'shorts-usagi-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(ep,record['peakDbfs'],flush=True)
