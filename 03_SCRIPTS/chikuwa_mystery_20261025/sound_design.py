"""Original, deterministic diegetic sound effects for v9 (no stock samples)."""
import numpy as np

def build_effects(manifest,sr,length):
    out=np.zeros((length,2),np.float32);events=[];rng=np.random.default_rng(20261027)
    rows=manifest['dialogue']
    def at(prefix):return next(r['startFrame']/30 for r in rows if r['text'].startswith(prefix))
    def add(name,start,duration,gain,kind):
        t=np.arange(round(sr*duration))/sr
        noise=rng.normal(0,1,len(t))
        if kind=='bell':
            x=sum(np.sin(2*np.pi*freq*t)*np.exp(-t*decay)*amp for freq,decay,amp in [(1180,4,1),(2390,7,.35),(3210,10,.12)])
        elif kind=='beep':
            x=np.sin(2*np.pi*1046.5*t)*np.minimum(1,t/.008)*np.minimum(1,(duration-t)/.025)
        elif kind=='paper':
            smooth=np.convolve(noise,np.ones(9)/9,mode='same');x=(noise-smooth)*np.sin(np.pi*t/duration)**2*(.6+.4*np.sin(2*np.pi*8*t))
        elif kind=='tray':
            x=np.sin(2*np.pi*2100*t)*np.exp(-t*35)+.4*np.sin(2*np.pi*3270*t)*np.exp(-t*50)
        elif kind=='drop':
            x=np.sin(2*np.pi*(1400*t-800*t*t))*np.exp(-t*35)
        else:
            smooth=np.convolve(noise,np.ones(35)/35,mode='same');x=.7*np.sin(2*np.pi*83*t)+smooth*.5
            for hit in np.arange(.5,duration,.72):
                delta=t-hit;x+=np.where(delta>=0,np.exp(-np.maximum(delta,0)*60)*np.sin(2*np.pi*210*delta),0)*.9
            x*=np.minimum(1,t/1.5)*np.minimum(1,(duration-t)/2)
        x*=gain/max(1,float(np.max(np.abs(x))));i=round(start*sr);end=min(length,i+len(x))
        out[i:end,0]+=x[:end-i];out[i:end,1]+=x[:end-i]*.94
        events.append(dict(name=name,startSeconds=round(start,3),durationSeconds=duration,peakGain=gain,source='original procedural synthesis'))
    add('試料トレー',at('味、弾力')+.15,.25,.023,'tray')
    add('受付呼び鈴',at('事前に知らせれば')-.42,.65,.018,'bell')
    add('調査報告書をめくる',at('なお、霜重')-.48,.40,.014,'paper')
    add('空の皿と箸',manifest['cues']['isobeReveal']/30+.1,.20,.014,'tray')
    test=at('市販品から毒が')
    add('試薬滴下',test+2.4,.18,.012,'drop')
    for i in range(3):add('検査終了音 '+str(i+1),test+i*1.5,.14,.015,'beep')
    add('生産ライン・ローラーと駆動音',manifest['codaStartFrame']/30,manifest['codaDurationFrames']/30,.007,'conveyor')
    # Low-level band-limited tape hiss with brief tracking crackle; no jump-scare gain.
    start=round(manifest['codaStartFrame']/30*sr);size=length-start
    hiss=rng.normal(0,1,size);hiss=np.convolve(hiss,np.ones(5)/5,mode='same')-np.convolve(hiss,np.ones(45)/45,mode='same')
    env=np.minimum(1,np.arange(size)/(sr*.15))*np.minimum(1,(size-np.arange(size))/(sr*1.2))
    hiss*=.0035*env
    for frame in [3,208,417,537]:
        at=round(frame/30*sr);n=min(round(.07*sr),size-at)
        hiss[at:at+n]+=rng.normal(0,.006,n)*np.hanning(n)
    out[start:,0]+=hiss;out[start:,1]+=hiss*.92
    events.append(dict(name='VHS tape hiss and tracking crackle',startSeconds=manifest['codaStartFrame']/30,durationSeconds=size/sr,source='original seeded noise synthesis'))
    return out,events
