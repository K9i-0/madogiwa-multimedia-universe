from pathlib import Path
import json,wave
import numpy as np
P=Path(__file__).resolve().parent
pub=P/'remotion/public'
m=json.loads((P/'remotion/src/edit-manifest-v5.json').read_text())
shots=[]
# Replace the entire mismatched close-up and adjacent existing cutaway.
for s in m['shots']:
 a=s['from'];b=a+s['duration']
 if b<=730 or a>=885:shots.append(s)
 elif a<730:shots.append(dict(s,duration=730-a))
shots.append(dict(kind='image',file='oden_toxic_c_reference.png',from_=730,duration=155,sourceStart=0))
shots[-1]['from']=shots[-1].pop('from_')
for s in shots:
 if s['from']==1492:s['file']='oden_toxic_c_reference.png'
m['shots']=sorted(shots,key=lambda s:s['from']);m['audio']='master_v6.wav'
(P/'remotion/src/edit-manifest-v6.json').write_text(json.dumps(m,indent=2)+'\n')
with wave.open(str(pub/'master_v5.wav'),'rb') as w:
 sr=w.getframerate();base=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).astype(np.float64)/32768
n=len(base);t=np.arange(n)/sr;rng=np.random.default_rng(88);bed=np.zeros(n)
# Original restrained suspense bed: low pedal, sparse bell/piano-like partials.
stop=888/30
env=np.minimum(t/1.3,1)*np.clip((stop-t)/.09,0,1)
bed+=(.009*np.sin(2*np.pi*55*t)+.004*np.sin(2*np.pi*82.4069*t)+.002*np.sin(2*np.pi*110.2*t))*env
for at,f in [(0.5,220),(4.7,233.08),(9,164.81),(14,220),(19.8,164.81),(24.5,233.08),(27.5,220)]:
 u=t-at;v=np.maximum(u,0);e=(u>=0)*np.minimum(v/.008,1)*np.exp(-v/1.4)*np.clip((stop-t)/.09,0,1)
 bed+=.012*e*(np.sin(2*np.pi*f*v)+.3*np.sin(2*np.pi*f*2.004*v)+.13*np.sin(2*np.pi*f*3.01*v))
# Quiet short radio squelch at entrance; footsteps on entry and intrusion.
for at in [13.0,17.7]:
 a=int(at*sr);l=int(.15*sr);noise=rng.normal(size=l);noise=np.convolve(noise,np.ones(8)/8,mode='same');bed[a:a+l]+=.009*noise*np.sin(np.linspace(0,np.pi,l))
for at in [18.5,19.05,32.3,32.93,33.58,34.25,34.9]:
 a=int(at*sr);l=int(.15*sr);u=np.arange(l)/sr
 bed[a:a+l]+=.017*np.exp(-u*32)*np.sin(2*np.pi*(90*u-70*u*u))+.003*rng.normal(size=l)*np.exp(-u*45)
# Small glass ring as Sobaya enters, not a comic sting.
a=int(35.5*sr);l=int(.65*sr);u=np.arange(l)/sr
bed[a:a+l]+=.005*np.exp(-u*9)*(np.sin(2*np.pi*1650*u)+.4*np.sin(2*np.pi*2473*u))
out=base+bed[:,None]
assert abs(out).max()<1,abs(out).max()
with wave.open(str(pub/'master_v6.wav'),'wb') as w:
 w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes(np.round(out*32768).astype('<i2').tobytes())
print('frames',m['durationInFrames'],'peak',abs(out).max())
