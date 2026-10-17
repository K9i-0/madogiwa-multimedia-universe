"""v6 mix: native narration, recorded testimony, room tone, reserved silence."""
import json, subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
m=json.loads((P/'src/edit-manifest.json').read_text());fps=m['composition']['fps'];sr=24000
n=round(m['composition']['durationInFrames']/fps*sr)
(P/'out').mkdir(exist_ok=True)
voice=np.zeros(n,dtype=np.float32)
for r in m['narration']:
    y,rate=sf.read(P/'public'/r['file'],dtype='float32');assert rate==sr
    if r['audioStyle']=='recording':
        # Same voice and normal speed; reduced bandwidth, no synthetic monster voice.
        y=sosfilt(butter(2,[240,3400],btype='bandpass',fs=sr,output='sos'),y).astype(np.float32)
        delay=round(.045*sr);y[delay:]+=.08*y[:-delay];y*=.90
    start=round(r['from']/fps*sr);voice[start:start+len(y)]+=y
sf.write(P/'out/narration.wav',voice,sr,subtype='PCM_16')
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'out/narration.wav'),'-af','loudnorm=I=-19:TP=-2.5:LRA=12','-ar',str(sr),str(P/'out/narration_normalized.wav')],check=True)
voice,_=sf.read(P/'out/narration_normalized.wav',dtype='float32');voice=voice[:n]
musicpath=ROOT/'.local/y-village-horror/separated/htdemucs/music_sample/no_vocals.wav'
y,rate=sf.read(musicpath,dtype='float32',always_2d=True)
y=resample_poly(y,sr,rate,axis=0).astype(np.float32)[4*sr:-4*sr]
y*=.011/max(float(np.sqrt(np.mean(y*y))),1e-8)
fade=4*sr
win=np.ones(len(y),np.float32);win[:fade]=np.linspace(0,1,fade);win[-fade:]=np.linspace(1,0,fade)
music=np.zeros((n,2),np.float32)
for start in range(0,n,len(y)-fade):
    length=min(len(y),n-start);music[start:start+length]+=y[:length]*win[:length,None]
dark,rate=sf.read(P/'out/encounter_music.wav',dtype='float32',always_2d=True);assert rate==sr
dark*=.011/max(float(np.sqrt(np.mean(dark*dark))),1e-8)
darkwin=np.ones(len(dark),np.float32);darkwin[:fade]=np.linspace(0,1,fade);darkwin[-fade:]=np.linspace(1,0,fade)
darkbed=np.zeros_like(music)
for start in range(0,n,len(dark)-fade):
    length=min(len(dark),n-start);darkbed[start:start+length]+=dark[:length]*darkwin[:length,None]
env=np.zeros(n,np.float32)
def dark_region(start,end,crossfade):
    a=max(0,round(start*sr));b=min(n,round(end*sr));f=min(round(crossfade*sr),(b-a)//2)
    env[a:b]=1;env[a:a+f]=np.linspace(0,1,f);env[b-f:b]=np.linspace(1,0,f)
by={r['id']:r for r in m['narration']}
dark_region(by['n0073']['from']/fps-1,by['n0078']['from']/fps+5,1)
dark_region(m['revealFrame']/fps-1,by['n0430']['from']/fps+3,3)
music*=1-env[:,None];music+=darkbed*env[:,None];del darkbed,env
musicgain=np.ones(n,np.float32);roomgain=np.zeros(n,np.float32)
for r in m['soundRegions']:
    a=round(r['from']/fps*sr);b=min(n,round(r['to']/fps*sr));length=b-a
    edge=min(round(r['fade']/fps*sr),length//2)
    blend=np.ones(length,np.float32)
    if edge:
        blend[:edge]=np.linspace(0,1,edge);blend[-edge:]=np.linspace(1,0,edge)
    musicgain[a:b]=musicgain[a:b]*(1-blend)+r['music']*blend
    roomgain[a:b]=roomgain[a:b]*(1-blend)+r['ambient']*blend
music*=musicgain[:,None];del musicgain
music[-5*sr:]*=np.linspace(1,0,5*sr)[:,None]
mix=music+voice[:,None];del music,voice
rng=np.random.default_rng(171026)
# One reproducible, quiet room bed. No added entity sounds in a witness's footage.
roomlen=31*sr;t=np.arange(roomlen,dtype=np.float32)/sr
room=sosfilt(butter(2,[45,1300],btype='bandpass',fs=sr,output='sos'),rng.normal(size=roomlen)).astype(np.float32)
room+=.12*np.sin(2*np.pi*100*t)+.04*np.sin(2*np.pi*200*t)
room/=max(float(np.sqrt(np.mean(room*room))),1e-8)
room=np.tile(room,n//roomlen+1)[:n]
# Loop endpoints are crossfaded into a separate bed to avoid seams.
for at in range(roomlen,n,roomlen):
    a=max(0,at-240);b=min(n,at+240);room[a:b]=np.linspace(room[a],room[b-1],b-a)
mix+=room[:,None]*roomgain[:,None];del room,roomgain
for event in m.get('environmentalAudio',[]):
    z,rate=sf.read(P/'public'/event['file'],dtype='float32');z=resample_poly(z,sr,rate).astype(np.float32)
    z=z[:round(event['duration']/fps*sr)]
    z*=min(event['rms']/max(float(np.sqrt(np.mean(z*z))),1e-8),.18/max(float(np.max(np.abs(z))),1e-8))
    edge=min(sr//3,len(z)//2);z[:edge]*=np.linspace(0,1,edge);z[-edge:]*=np.linspace(1,0,edge)
    at=round(event['from']/fps*sr);mix[at:at+len(z)]+=z[:,None]
for event in m.get('characterAudio',[]):
    z,rate=sf.read(P.parent/event['file'],dtype='float32')
    if z.ndim>1:z=z.mean(axis=1)
    z=resample_poly(z,sr,rate).astype(np.float32);active=z[np.abs(z)>.003]
    rms=float(np.sqrt(np.mean(active*active))) if len(active) else 1
    z*=min(.11/max(rms,1e-8),.65/max(float(np.max(np.abs(z))),1e-8))*event.get('gain',1.0)
    at=round(event['from']/fps*sr);mix[at:at+len(z)]+=z[:,None]
for e in m['sfx']:
    kind=e['kind'];duration={'wood':.65,'glass':1.1,'can':.6,'hum':2.4,'creak':1.2,'clap':1.2,'chair':.85,'mug-drag':.8,'mug-set':.6}[kind]
    t=np.arange(round(duration*sr))/sr;noise=rng.normal(size=len(t))
    if kind=='glass':z=sum(np.sin(2*np.pi*h*t)*np.exp(-t*d) for h,d in [(1300,6),(2113,9),(3317,13)])*.024
    elif kind=='wood':z=sosfilt(butter(2,1800,fs=sr,output='sos'),noise)*np.exp(-t*16)*.11+np.sin(2*np.pi*85*t)*np.exp(-t*20)*.05
    elif kind=='can':
        pop=sosfilt(butter(2,[1200,7000],btype='bandpass',fs=sr,output='sos'),noise)
        z=pop*(np.exp(-t*65)+.28*np.where(t>.1,np.exp(-np.maximum(t-.1,0)*9),0))*.07
        z+=np.sin(2*np.pi*1900*t)*np.exp(-t*80)*.018
    elif kind=='hum':z=(np.sin(2*np.pi*100*t)+.3*np.sin(2*np.pi*200*t))*.007*np.sin(np.pi*t/duration)**2
    elif kind=='clap':
        noise=sosfilt(butter(2,[400,2800],btype='bandpass',fs=sr,output='sos'),noise)
        z=noise*(np.exp(-t*35)+np.where(t>=.55,np.exp(-np.maximum(0,t-.55)*35),0))*.08
    elif kind=='creak':z=np.sin(2*np.pi*(180*t+65*t*t))*.012*np.sin(np.pi*t/duration)**2
    elif kind in ('chair','mug-drag'):
        z=sosfilt(butter(2,[120,1800],btype='bandpass',fs=sr,output='sos'),noise)*.022*np.sin(np.pi*t/duration)**2
        z+=np.sin(2*np.pi*(310*t+40*t*t))*.006*np.sin(np.pi*t/duration)**2
    else:z=np.sin(2*np.pi*170*t)*np.exp(-t*24)*.04+sosfilt(butter(2,1200,fs=sr,output='sos'),noise)*np.exp(-t*45)*.035
    z[:120]*=np.linspace(0,1,120);z[-240:]*=np.linspace(1,0,240);z*=e.get('gain',1)
    sf.write(P/'public/sfx'/f'{kind}.wav',z,sr,subtype='PCM_16')
    at=round(e['frame']/fps*sr);mix[at:at+len(z)]+=z[:,None]
sf.write(P/'out/premix.wav',mix,sr,subtype='PCM_24')
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'out/premix.wav'),'-af','alimiter=limit=0.85:level=false','-ar','48000',str(P/'public/mix.wav')],check=True)
(P/'out/audio-build.json').write_text(json.dumps({'seconds':n/sr,'preLimiterPeak':float(np.max(np.abs(mix))),'musicSource':str(musicpath.relative_to(ROOT)),'musicStatus':'reference extraction; title/master unconfirmed','sfx':'original deterministic synthesis; real howler from credited adopted source','environmentalAudio':m['environmentalAudio'],'soundRegions':m['soundRegions'],'voice':'VOICEVOX:青山龍星 style13 speed1.0; no time stretch; normalized -19 LUFS','recordedDialogue':[r['id'] for r in m['narration'] if r['audioStyle']=='recording'],'sobaya':'canonical Irodori v4 Large; v4 processing preserved; two growls','encounterMusic':'reversed/pitched/filtered original reference; distinct room-only scenes'},ensure_ascii=False,indent=2))
print('Audio complete',n/sr,float(np.max(np.abs(mix))))
