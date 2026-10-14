"""Apply a light electronic hologram voice to the two projected-Takosan lines only.
Run with .local/Irodori-TTS/.venv/bin/python; uses NumPy, SciPy and FFmpeg.
No TTS regeneration, pitch shift, time stretch, or video re-encoding.
"""
from pathlib import Path
import json,hashlib,subprocess
import numpy as np
from scipy.signal import butter,sosfilt,fftconvolve
P=Path(__file__).resolve().parent;E=P.parent;R=E.parents[1]
C=json.loads((P/'src/shorts-hologram-audio.json').read_text());V=json.loads((E/'shorts-usagi-record.json').read_text())
S=C['sampleRate'];spf=S/C['fps'];O=P/'out/shorts-hologram';O.mkdir(parents=True,exist_ok=True)
def read(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar',str(S),'-ac','2','-f','f32le','-']),dtype='<f4').reshape(-1,2).copy()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(S),'-ac','2','-i','-','-c:a','pcm_s16le',str(p)],input=x.astype('<f4').tobytes(),check=True)
def streamhash(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:v:0','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
original=read(P/'out/shorts-usagi/mix.wav');a=round(C['effectStartFrame']*spf);b=round(C['effectEndFrame']*spf);dry=np.zeros((b-a,2))
for i in C['lineIndexes']:
 line=V['lines'][i];v=read(E/line['file'])*10**(line['gainDb']/20);at=round(line['startFrame']*spf)-a;dry[at:at+len(v)]+=v
band=sosfilt(butter(2,C['electronicBandHz'],fs=S,btype='bandpass',output='sos'),dry,axis=0)
t=np.arange(len(dry))/S
ring=band*np.sin(2*np.pi*C['ringFrequencyHz']*t)[:,None]*C['ringWetGain']
wet=ring.copy()
for ch,delay in enumerate(C['stereoDelaySeconds']):
 n=round(delay*S);wet[n:,ch]+=band[:-n,ch]*C['stereoDelayGain']
rng=np.random.default_rng(C['reverbSeed']);n=round(C['reverbLengthSeconds']*S);time=np.arange(n)/S;rv=np.zeros_like(dry)
for ch in range(2):
 ir=rng.standard_normal(n)*np.exp(-6.907755*time/C['reverbRt60Seconds']);ir[:round(C['reverbPreDelaySeconds']*S)]=0
 ir=sosfilt(butter(2,[300,4500],fs=S,btype='bandpass',output='sos'),ir);ir/=np.linalg.norm(ir)
 rv[:,ch]=fftconvolve(dry[:,ch],ir)[:len(dry)]
rv*=C['reverbWetRmsRatio']*np.sqrt(np.mean(dry**2))/max(1e-10,np.sqrt(np.mean(rv**2)))
wet+=rv;k=round(C['tailFadeSeconds']*S);wet[-k:]*=np.linspace(1,0,k)[:,None]
processed=C['dryGain']*dry+wet
active=np.mean(dry**2,axis=1)>10**(-35/10)
match=np.sqrt(np.mean(dry[active]**2))/np.sqrt(np.mean(processed[active]**2));processed*=match
mix=original.copy();mix[a:b]+=(processed-dry).astype(np.float32)
assert np.array_equal(mix[:a],original[:a]) and np.array_equal(mix[b:],original[b:])
assert np.max(np.abs(mix))<1
save(O/'mix.wav',mix)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(O/'mix.wav'),'-c:a','aac','-b:a','192k',str(O/'mix.m4a')],check=True)
source=E/'final_remotion_shorts_usagi_9x16.mp4';output=E/C['output']
subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-i',str(O/'mix.m4a'),'-map','0:v:0','-map','1:a:0','-c','copy','-t',str(len(mix)/S),'-movflags','+faststart',str(output)],check=True)
assert streamhash(source)==streamhash(output)
subprocess.run(['ffmpeg','-v','error','-i',str(output),'-f','null','-'],check=True)
assert sha(R/V['horizontalSource'])==V['horizontalSha256']
m=json.loads((E/'shorts-manifest-usagi.json').read_text());m['audioSource']=str((O/'mix.m4a').relative_to(R));m['audioRevision']+='; hologram lines only: subtle ring modulation, stereo delay, short reverb'
(E/'shorts-manifest-hologram.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
report=dict(source=source.name,sourceSha256=sha(source),output=output.name,sha256=sha(output),settings=C,processedLines=[V['lines'][i] for i in C['lineIndexes']],activeSpeechGainMatchDb=float(20*np.log10(match)),peakDbfs=float(20*np.log10(np.max(np.abs(mix)))),outsideEffectWindowPcmIdentical=True,videoStreamIdentical=True,horizontalSourceUnchanged=True,fullDecode=True,subjectiveListening=False)
(E/'shorts-hologram-audio-record.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
