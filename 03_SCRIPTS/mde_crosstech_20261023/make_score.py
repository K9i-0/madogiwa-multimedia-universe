"""Original restrained electronic underscore, no third-party samples."""
from pathlib import Path
import numpy as np, wave, subprocess
EP=Path(__file__).resolve().parent; ROOT=EP.parents[1]
sr=48000; beat=.625; duration=40.; y=np.zeros(int(sr*duration),dtype=np.float64)
def tone(start,length,freq,gain):
 n=int(length*sr);t=np.arange(n)/sr
 env=np.minimum(t/.035,1)*np.minimum((length-t)/.3,1)*np.exp(-t*.65)
 s=(np.sin(2*np.pi*freq*t)+.18*np.sin(2*np.pi*freq*2*t))*.7*env*gain
 a=int(start*sr);b=min(a+n,len(y));y[a:b]+=s[:b-a]
chords=[[146.832,220,293.665],[130.813,196,261.626],[110,164.814,220],[130.813,196,293.665]]
for bar in range(16):
 notes=chords[(bar//2)%4];at=bar*4*beat
 for freq in notes:tone(at,2.5,freq,.11)
 for i in range(4):tone(at+i*beat,.52,notes[i%3]*2,.055)
 tone(at,1.2,notes[0]/2,.16)
# Seamless harmonic cycle; gently blend loop boundary.
y=np.tanh(y); y[:2400]*=np.linspace(0,1,2400); y[-2400:]*=np.linspace(1,0,2400); raw=ROOT/'.local/mde-crosstech/score.wav'
with wave.open(str(raw),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((y*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-y','-v','error','-i',str(raw),'-af','lowpass=f=3000,loudnorm=I=-34:TP=-8:LRA=4','-ar','48000',str(EP/'remotion/public/score.wav')],check=True)
