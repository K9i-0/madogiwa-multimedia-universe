"""Reproducible stereo horror mix: official KK music, canonical voices, original Foley."""
from pathlib import Path
import json, subprocess, hashlib
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sr=24000
m=json.loads((P/'src/edit-manifest.json').read_text());fps=m['composition']['fps'];n=round(m['composition']['durationInFrames']/fps*sr)
mix=np.zeros((n,2),np.float32);rng=np.random.default_rng(241026)
by={r['id']:r for r in m['narration']}
def read(path,stereo=False):
    y,rate=sf.read(path,dtype='float32',always_2d=True)
    y=resample_poly(y,sr,rate,axis=0).astype(np.float32)
    return y if stereo else y.mean(axis=1)
def edges(y,a=.012,b=.035):
    y=y.copy();a=min(round(a*sr),len(y)//2);b=min(round(b*sr),len(y)//2)
    if a:y[:a]*=np.linspace(0,1,a,dtype=np.float32)
    if b:y[-b:]*=np.linspace(1,0,b,dtype=np.float32)
    return y
def level(y,rms=.105,peak=.7):
    active=y[np.abs(y)>.002]
    measure=float(np.sqrt(np.mean(active*active))) if len(active) else 1
    return y*min(rms/max(measure,1e-8),peak/max(float(np.max(np.abs(y))),1e-8))
def echo(y,delays):
    z=np.zeros(len(y)+round(max(d[0] for d in delays)*sr),np.float32)
    z[:len(y)]+=y
    for t,g in delays:
        k=round(t*sr);z[k:k+len(y)]+=g*y
    return z
def place(y,frame,pan=0,gain=1):
    start=round(frame/fps*sr);length=min(len(y),n-start)
    if y.ndim==1:
        # Moderate balance; both channels retain audibility on a phone speaker.
        channels=np.array([1-max(0,pan)*.68,1-max(0,-pan)*.68],np.float32)
        z=y[:length,None]*channels[None,:]
    else:z=y[:length]
    mix[start:start+length]+=z*gain

voice_stem=np.zeros((n,2),np.float32)
for row in m['narration']:
    y=read(P/'public'/row['file']);y=edges(level(y,.105 if row['speaker']=='narrator' else .115))
    pan=0
    if row['id']=='n081':
        y=echo(sosfilt(butter(2,5500,fs=sr,output='sos'),y).astype(np.float32),[(.075,.09),(.17,.045)])
    elif row['id']=='n095':
        # The same F identity as the warning, dry and close at the right ear.
        pan=.78;y=echo(y,[(.008,.07)])
    elif row['speaker']=='sobaya':
        y=sosfilt(butter(2,[65,4300],btype='bandpass',fs=sr,output='sos'),y).astype(np.float32)
        y=echo(y,[(.055,.10),(.145,.055)])
        pan=.5 if row['id']=='n045' else .65
    place(y,row['from'],pan)
voice_stem[:]=mix
sf.write(P/'out/voice-stem.wav',voice_stem,sr,subtype='PCM_24')
del voice_stem

source=ROOT/'.local/y-village-mask-horror-20261024/music/kk_fuan_kyofu_senritsu.wav'
music=read(source,True)
music*=.013/max(float(np.sqrt(np.mean(music*music))),1e-8)
fade=3*sr;window=np.ones(len(music),np.float32)
window[:fade]=np.linspace(0,1,fade);window[-fade:]=np.linspace(1,0,fade)
bed=np.zeros((n,2),np.float32)
for start in range(0,n,len(music)-fade):
    length=min(len(music),n-start);bed[start:start+length]+=music[:length]*window[:length,None]
musicgain=np.ones(n,np.float32);roomgain=np.full(n,.0012,np.float32)
for r in m['soundRegions']:
    a=round(r['from']/fps*sr);b=round(r['to']/fps*sr);edge=min(round(r['fade']/fps*sr),(b-a)//2)
    env=np.ones(b-a,np.float32)
    if edge:env[:edge]=np.linspace(0,1,edge);env[-edge:]=np.linspace(1,0,edge)
    musicgain[a:b]=musicgain[a:b]*(1-env)+r['music']*env
    roomgain[a:b]=roomgain[a:b]*(1-env)+r['ambient']*env
bed*=musicgain[:,None];mix+=bed;del bed,music,musicgain
# Continuous non-tonal room air; seeded generation cannot produce loop seams.
room=sosfilt(butter(2,[55,1700],btype='bandpass',fs=sr,output='sos'),rng.normal(size=n)).astype(np.float32)
room/=max(float(np.sqrt(np.mean(room*room))),1e-8);mix+=room[:,None]*roomgain[:,None]
del room,roomgain

# A real F voice remains in front while the same voice speaks close to the ear.
chant=read(P.parent/'f_chant.wav')
chant=sosfilt(butter(2,[150,3000],btype='bandpass',fs=sr,output='sos'),chant).astype(np.float32)
chant=echo(edges(level(chant,.032,.14),.1,.14),[(.09,.18),(.21,.09),(.39,.04)])
for frame in range(m['ritual']['start'],m['ritual']['end'],round((len(chant)/sr+.65)*fps)):
    gain=1.9 if abs(frame-m['ritual']['surge'])<round(5*fps) else 1
    remaining=round((m['ritual']['end']-frame)/fps*sr)
    place(edges(chant[:remaining],.04,.12),frame,-.15,gain)

def foley(kind):
    seconds={'slide':1.5,'crack':1.0,'breath':1.45,'step':.45,'fabric':.95,'cloth':.7,'wood':.4,'bird':1.6,'lock':.35}[kind]
    t=np.arange(round(seconds*sr))/sr;noise=rng.normal(size=len(t));z=np.zeros(len(t))
    def band(low,high):return sosfilt(butter(2,[low,high],btype='bandpass',fs=sr,output='sos'),noise)
    if kind=='breath':
        breath=band(170,2000)+.24*band(2400,4800)
        env=np.sin(np.pi*t/seconds)**1.6
        z=breath*env*(.8+.2*np.sin(2*np.pi*17*t))* .14
    elif kind=='slide':
        z=band(90,1500)*np.sin(np.pi*t/seconds)**1.2*.035
        z+=np.sin(2*np.pi*(137*t+11*t*t))*np.sin(np.pi*t/seconds)**3*.007
    elif kind=='crack':
        for offset,g in [(0,1),(.075,.48),(.19,.28),(.32,.13)]:
            dt=np.maximum(0,t-offset);env=np.exp(-dt*35)*(t>=offset)
            z+=g*env*(band(1000,9000)*.16+np.sin(2*np.pi*2371*dt)*.035+np.sin(2*np.pi*3877*dt)*.022)
    elif kind=='step':
        z=band(55,800)*np.exp(-t*28)*.13+np.sin(2*np.pi*73*t)*np.exp(-t*33)*.035
        z+=band(800,2900)*np.exp(-t*18)*.012
    elif kind in ['fabric','cloth']:
        z=band(450,4400)*np.sin(np.pi*t/seconds)**2*(.038 if kind=='fabric' else .025)
        z*=.8+.2*np.sin(2*np.pi*21*t)
    elif kind=='wood':z=band(90,1200)*np.exp(-t*29)*.15+np.sin(2*np.pi*155*t)*np.exp(-t*24)*.035
    elif kind=='bird':
        for offset in [.0,.24,.62,.83]:
            dt=t-offset;active=(dt>=0)&(dt<.14);u=np.clip(dt/.14,0,1)
            phase=2*np.pi*(2600*dt+2100*.14*(u-u*u/2))
            z+=np.sin(phase)*np.sin(np.pi*u)**2*active*.016
    elif kind=='lock':z=band(1500,7000)*np.exp(-t*65)*.09+np.sin(2*np.pi*1800*t)*np.exp(-t*50)*.025
    return edges(z.astype(np.float32),.004,.025)
cache={}
for event in m['sfx']:
    kind=event['kind']
    if kind not in cache:
        cache[kind]=foley(kind);sf.write(P/'public/sfx'/f'{kind}.wav',cache[kind],sr,subtype='PCM_16')
    place(cache[kind],event['frame'],event['pan'],event['gain'])
# The tail settles into real silence, without a restart of the curse.
mix[-4*sr:]*=np.linspace(1,0,4*sr)[:,None]
sf.write(P/'out/premix.wav',mix,sr,subtype='PCM_24')
stats=subprocess.run(['ffmpeg','-hide_banner','-i',str(P/'out/premix.wav'),'-af','loudnorm=I=-17:TP=-1.5:LRA=18:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
measure=json.JSONDecoder().raw_decode(stats.stderr[stats.stderr.rfind('{'):])[0]
gain_db=-17-float(measure['input_i'])
gain_db=min(gain_db,-1.5-float(measure['input_tp']))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'out/premix.wav'),'-af',f'volume={gain_db:.5f}dB,alimiter=limit=0.85:level=false:latency=true','-ar','48000',str(P/'public/mix.wav')],check=True)
(P.parent/'audio-review.json').write_text(json.dumps({'duration':n/sr,'sourceMusic':str(source.relative_to(ROOT)),'rawMusicSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'premix':measure,'masterGainDb':gain_db,'preLimiterPeak':float(abs(mix).max()),'narrator':'青山龍星・ノーマル style13 / speed1.0 / pitch0 / intonation0.85','characterVoice':'canonical Irodori; content screened with local ASR','sfx':'original deterministic Foley; seed241026; no externally licensed SFX','spatialDesign':'same inhalation reused at a distance and close to right ear; F chant continues under false release','listening':'No human full-program listening performed. Waveforms, readings, source content, and mix levels audited.'},ensure_ascii=False,indent=2)+'\n')
print('Audio built:',n/sr,'s;',measure['input_i'],'LUFS before master;',gain_db,'dB master gain')
