"""Rebuild the confirmation mix. Source music is a separated reference, not a master."""
import json, subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
m=json.loads((P/'src/edit-manifest.json').read_text());fps=m['composition']['fps'];sr=24000
n=round(m['composition']['durationInFrames']/fps*sr)
voice=np.zeros(n,dtype=np.float32)
for r in m['narration']:
    y,rate=sf.read(P/'public'/r['file'],dtype='float32')
    assert rate==sr
    start=round(r['from']/fps*sr)
    voice[start:start+len(y)]+=y
sf.write(P/'out/narration.wav',voice,sr,subtype='PCM_16')
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'out/narration.wav'),'-af','loudnorm=I=-19:TP=-2.5:LRA=10','-ar',str(sr),str(P/'out/narration_normalized.wav')],check=True)
voice,_=sf.read(P/'out/narration_normalized.wav',dtype='float32');voice=voice[:n]
musicpath=ROOT/'.local/y-village-horror/separated/htdemucs/music_sample/no_vocals.wav'
y,rate=sf.read(musicpath,dtype='float32',always_2d=True)
y=resample_poly(y,sr,rate,axis=0).astype(np.float32)
# Remove separation startup/end artifacts and overlap every loop by four seconds.
y=y[4*sr:-4*sr]
y*=.014/max(float(np.sqrt(np.mean(y*y))),1e-8)
fade=4*sr;win=np.ones(len(y),np.float32);win[:fade]=np.linspace(0,1,fade);win[-fade:]=np.linspace(1,0,fade)
music=np.zeros((n,2),np.float32)
for start in range(0,n,len(y)-fade):
    length=min(len(y),n-start);music[start:start+length]+=y[:length]*win[:length,None]
# Encounter bed: reversed, lowered and filtered source; crossfade back at morning.
dark,rate=sf.read(P/'out/encounter_music.wav',dtype='float32',always_2d=True)
assert rate==sr
dark*=.014/max(float(np.sqrt(np.mean(dark*dark))),1e-8)
darkwin=np.ones(len(dark),np.float32);darkwin[:fade]=np.linspace(0,1,fade);darkwin[-fade:]=np.linspace(1,0,fade)
darkbed=np.zeros_like(music)
for start in range(0,n,len(dark)-fade):
    length=min(len(dark),n-start);darkbed[start:start+length]+=dark[:length]*darkwin[:length,None]
env=np.zeros(n,np.float32)
def dark_region(start,end,crossfade):
    a=max(0,round(start*sr));b=min(n,round(end*sr));f=min(round(crossfade*sr),(b-a)//2)
    env[a:b]=1
    env[a:a+f]=np.linspace(0,1,f);env[b-f:b]=np.linspace(1,0,f)
early=next(e for e in m['characterAudio'] if e.get('intelligible') == 'partly')
dark_region(early['from']/fps-2,early['from']/fps+14,2)
morning=next(r['from']/fps for r in m['narration'] if r['id']=='n0430')
dark_region(m['revealFrame']/fps-2,morning+4,4)
music=music*(1-env[:,None])+darkbed*env[:,None]
# Silence at the first appearance; do not cover the pause with a sting.
reveal=m['revealFrame'];a=round((reveal/fps-3)*sr);b=round((reveal/fps+6)*sr)
music[a:b]*=np.concatenate([np.linspace(1,0,sr),np.zeros(max(0,b-a-2*sr)),np.linspace(0,1,sr)])[:,None]
for region in m.get('quietRegions',[]):
    a=round(region['from']/fps*sr);b=min(n,round(region['to']/fps*sr));edge=min(round(.3*sr),(b-a)//2)
    dip=np.full(b-a,region['level'],np.float32)
    dip[:edge]=np.linspace(1,region['level'],edge);dip[-edge:]=np.linspace(region['level'],1,edge)
    music[a:b]*=dip[:,None]
music[-6*sr:]*=np.linspace(1,0,6*sr)[:,None]
mix=music+voice[:,None]
for event in m.get('environmentalAudio',[]):
    z,rate=sf.read(P/'public'/event['file'],dtype='float32')
    z=resample_poly(z,sr,rate).astype(np.float32)
    z*=min(event['rms']/max(float(np.sqrt(np.mean(z*z))),1e-8),.22/max(float(np.max(np.abs(z))),1e-8))
    at=round(event['from']/fps*sr);z=z[:round(event['duration']/fps*sr)]
    mix[at:at+len(z)]+=z[:,None]
for event in m.get('characterAudio',[]):
    z,rate=sf.read(P.parent/event['file'],dtype='float32')
    if z.ndim>1:z=z.mean(axis=1)
    z=resample_poly(z,sr,rate).astype(np.float32)
    # Canonical monster processing is already applied. Match the scene level only.
    active=z[np.abs(z)>.003]
    rms=float(np.sqrt(np.mean(active*active))) if len(active) else 1
    z*=min(.11/max(rms,1e-8),.65/max(float(np.max(np.abs(z))),1e-8))
    z*=event.get('gain',1.0)
    at=round(event['from']/fps*sr)
    mix[at:at+len(z)]+=z[:,None]
rng=np.random.default_rng(171026)
for e in m['sfx']:
    kind=e['kind'];duration={'wood':.55,'glass':1.1,'can':.5,'hum':1.8,'creak':1.2,'clap':1.0}[kind]
    t=np.arange(round(duration*sr))/sr
    if kind=='glass':
        z=sum(np.sin(2*np.pi*h*t)*np.exp(-t*d) for h,d in [(1300,6),(2113,9),(3317,13)])*.025
    elif kind=='wood':
        z=sosfilt(butter(2,1800,fs=sr,output='sos'),rng.normal(size=len(t)))*np.exp(-t*16)*.11+np.sin(2*np.pi*85*t)*np.exp(-t*20)*.05
    elif kind=='can':z=rng.normal(size=len(t))*np.exp(-t*15)*.035
    elif kind=='hum':z=(np.sin(2*np.pi*100*t)+.3*np.sin(2*np.pi*200*t))*.009*np.sin(np.pi*t/duration)**2
    elif kind=='clap':
        noise=sosfilt(butter(2,[400,2800],btype='bandpass',fs=sr,output='sos'),rng.normal(size=len(t)))
        z=noise*(np.exp(-t*35)+np.where(t>=.45,np.exp(-np.maximum(0,t-.45)*35),0))*.09
    else:z=np.sin(2*np.pi*(180*t+65*t*t))*.018*np.sin(np.pi*t/duration)**2
    z[:120]*=np.linspace(0,1,120);z[-240:]*=np.linspace(1,0,240)
    sf.write(P/'public/sfx'/f'{kind}.wav',z,sr,subtype='PCM_16')
    at=round(e['frame']/fps*sr);mix[at:at+len(z)]+=z[:,None]
sf.write(P/'out/premix.wav',mix,sr,subtype='PCM_24')
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'out/premix.wav'),'-af','alimiter=limit=0.89:level=false','-ar','48000',str(P/'public/mix.wav')],check=True)
(P/'out/audio-build.json').write_text(json.dumps({'seconds':n/sr,'preLimiterPeak':float(np.max(np.abs(mix))),'musicSource':str(musicpath.relative_to(ROOT)),'musicStatus':'reference extraction; title/master unconfirmed','sfx':'original deterministic procedural synthesis; seed171026; real howler excerpt credited in monkey-audio-source.json','environmentalAudio':m.get('environmentalAudio',[]),'quietRegions':m.get('quietRegions',[]),'voice':'VOICEVOX:青山龍星 style13 speed1.0; normalized -19 LUFS','sobaya':'canonical Irodori v4 Large; main growl + partially intelligible early murmur; see sound-processing-v4.json','encounterMusic':'reversed/pitched/filtered source; 4-second crossfade; morning restoration'},ensure_ascii=False,indent=2))
print('Audio complete',n/sr,float(np.max(np.abs(mix))))
