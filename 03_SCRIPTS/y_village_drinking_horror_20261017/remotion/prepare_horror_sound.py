"""Deterministic v3 processing of adopted Sobaya voice and reference music."""
from pathlib import Path
import json,subprocess,hashlib
import numpy as np
import soundfile as sf
from scipy.signal import butter,sosfilt,resample_poly
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sr=24000
# Reverse syllable order, slow/pitch down, ring-modulate, filter and add short echoes.
source=P.parent/'sobaya_beer.wav'
y,rate=sf.read(source,dtype='float32');y=y.mean(axis=1) if y.ndim>1 else y
y=resample_poly(y,sr,rate)[::-1];y=resample_poly(y,5,3)
t=np.arange(len(y))/sr
y=sosfilt(butter(3,[100,1550],btype='bandpass',fs=sr,output='sos'),y)
y=np.tanh(y*7)*np.sin(2*np.pi*47*t)
z=np.zeros(len(y)+int(.32*sr))
for delay,gain in [(0,1),(.13,.35),(.29,.2)]:
 at=round(delay*sr);z[at:at+len(y)]+=gain*y
z[:1200]*=np.linspace(0,1,1200);z[-2400:]*=np.linspace(1,0,2400)
z*=.55/max(abs(z))
sf.write(P.parent/'sobaya_early_murmur.wav',z,sr,subtype='PCM_16')
# Same source, transformed into an encounter-only bed. No newly sourced music.
source_music=ROOT/'.local/y-village-horror/separated/htdemucs/music_sample/no_vocals.wav'
target=P/'out/encounter_music.wav'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(source_music),'-af','atrim=start=4:end=86,areverse,asetrate=33075,aresample=24000,highpass=f=45,lowpass=f=1500,aecho=0.8:0.6:430|910:0.2|0.12','-ac','2',str(target)],check=True)
(P.parent/'sound-processing-v3.json').write_text(json.dumps({'earlyVoice':{'source':'sobaya_beer.wav','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'processing':'reverse; 0.6 playback ratio; 100–1550 Hz bandpass; tanh saturation; 47 Hz ring modulation; 130/290 ms echoes; 50/100 ms fades','output':'sobaya_early_murmur.wav','seconds':len(z)/sr,'subtitle':None},'encounterMusic':{'source':str(source_music.relative_to(ROOT)),'processing':'reverse; playback ratio 0.75; 45–1500 Hz bandpass; 430/910 ms echoes','output':'remotion/out/encounter_music.wav','status':'processed provisional reference extraction; original title/master unconfirmed'}},ensure_ascii=False,indent=2)+'\n')
print('Prepared sound',len(z)/sr)
