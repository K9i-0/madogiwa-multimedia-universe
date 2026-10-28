"""Frame timeline, original period-style MIDI-like score, and PCM master."""
import difflib, hashlib, json, math, re, shutil, subprocess, unicodedata, wave
from pathlib import Path
import numpy as np

EP=Path(__file__).resolve().parent
PUB=EP/'remotion/public'
PUB.mkdir(parents=True,exist_ok=True)
FPS=24;SR=48000
data=json.loads((EP/'content.json').read_text())
voices=json.loads((EP/'voice-records.json').read_text())
segments=[];captions=[];cues=[];pending=[];cursor=0
def segment(id,type,frames):
    global cursor
    s={'id':id,'type':type,'start':cursor,'duration':frames};segments.append(s);cursor+=frames;return s
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKC',s) if c.isalnum())
def wrap(s,width=27):
    if len(s)<=width:return s
    options=[i+1 for i,c in enumerate(s) if c in '、。' and abs(i-len(s)/2)<9]
    cut=min(options,key=lambda i:abs(i-len(s)/2)) if options else len(s)//2
    return s[:cut]+'\n'+s[cut:]
def add_captions(line,start):
    r=voices[line['id']];path=EP/'generated/asr'/(line['id']+'.json')
    spans=json.loads(path.read_text()).get('offsets',[]) if path.exists() else []
    if not spans:pending.append('ASR '+line['id'])
    source=norm(line['text']);target=norm(''.join(x['text'] for x in spans))
    matcher=difflib.SequenceMatcher(None,source,target,autojunk=False)
    def stamp(n):
        targetn=len(target)
        for _,a,b,c,d in matcher.get_opcodes():
            if a<=n<=b:targetn=c+(n-a)*(d-c)/max(1,b-a);break
        pos=0
        for span in spans:
            size=len(norm(span['text']));lo,hi=span['timestamp'];hi=min(hi,r['duration'])
            if pos<=targetn<=pos+size:return lo+(hi-lo)*(targetn-pos)/max(1,size)
            pos+=size
        return r['duration']*n/max(1,len(source))
    pos=0
    for sentence in re.findall(r'.+?[。！？]|.+$',line['text']):
        lo=stamp(pos);pos+=len(norm(sentence));hi=stamp(pos)
        captions.append({'start':start+round(lo*FPS),'end':start+max(round(lo*FPS)+1,round(hi*FPS)),'text':wrap(sentence),'source':'canonical script, ASR-assisted timing'})

segment('opening','opening',140)
sources=json.loads((EP/'scene-sources.json').read_text())
workflow=json.loads((EP/sources['workflow']).read_text())
cond=next(n['inputs'] for n in workflow.values() if n['class_type']=='MiniMaxH3ReferenceToVideo')
scene=segment('scene','scene',cond['length'])
video=EP/sources['video']
if video.exists():
    shutil.copy2(video,PUB/'scene.mp4')
    subprocess.run(['ffmpeg','-y','-v','error','-ss',str(sources['still_seconds']),'-i',str(video),'-frames:v','1',str(PUB/'still.png')],check=True)
    cues.append({'file':str(video),'start':scene['start'],'length':scene['duration'],'id':'scene','target_lufs':-19})
else:pending.append('H3')
segment('chapter','chapter',36)
for line in data['narration']:
    duration=math.ceil(voices[line['id']]['duration']*FPS)
    s=segment(line['id'],'explanation',duration+30)
    start=s['start']+10
    cues.append({'file':str(EP/voices[line['id']]['file']),'start':start,'length':duration,'id':line['id'],'target_lufs':-18})
    add_captions(line,start)
ending=segment('ending','ending',96)

manifest={'composition':{'id':'MegaMugDVD','width':960,'height':720,'fps':FPS,'durationInFrames':cursor},'segments':segments,'captions':captions,'pending':pending,'audio':{'master':'master.wav','scene':'H3 embedded audio','narrator':'original Irodori voice design','music':'original deterministic synthesis, score in prepare_edit.py'},'style':{'reference':data['reference'],'aspect':'4:3','softness_px':0.45,'contrast':0.94,'saturation':0.80,'master_size':'960x720'}}
(EP/'remotion/src/edit-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')

samples=round(cursor/FPS*SR)
mix=np.zeros((samples,2),np.float32)
music=np.zeros_like(mix)
rng=np.random.default_rng(2026102805)
def note(at,midi,length,gain,kind='ep',pan=0):
    i=round(at*SR);n=min(round(length*SR),samples-i)
    if n<=0:return
    t=np.arange(n,dtype=np.float64)/SR;hz=440*2**((midi-69)/12)
    if kind=='ep':
        env=(1-np.exp(-t*200))*np.exp(-t*3)
        sound=np.sin(2*np.pi*hz*t+1.4*np.sin(2*np.pi*hz*2*t)*np.exp(-t*6))*env
    elif kind=='lead':
        env=(1-np.exp(-t*65))*np.exp(-t*3.5)
        sound=(np.sin(2*np.pi*hz*t)+.2*np.sin(4*np.pi*hz*t)+.08*np.sin(6*np.pi*hz*t))*env
    elif kind=='pad':
        env=np.minimum(1,t/.23)*np.minimum(1,(length-t)/.5)
        sound=(np.sin(2*np.pi*hz*t)+.35*np.sin(2*np.pi*hz*1.003*t)+.1*np.sin(4*np.pi*hz*t))*env
    elif kind=='bass':sound=(np.sin(2*np.pi*hz*t)+.17*np.sin(4*np.pi*hz*t))*(1-np.exp(-t*100))*np.exp(-t*5)
    elif kind=='hat':sound=rng.normal(0,1,n)*np.exp(-t*60)*.22
    else:sound=np.sin(2*np.pi*(45*t+1.8*(1-np.exp(-t*35))))*np.exp(-t*20)
    sound=np.asarray(sound*gain,np.float32)
    music[i:i+n,0]+=sound*(.8-.2*pan);music[i:i+n,1]+=sound*(.8+.2*pan)

def theme(at,gain=1):
    beat=.6
    chords=[(60,64,67,71),(57,60,64,67),(53,57,60,64),(55,59,62,65)]
    for k,chord in enumerate(chords):
        time=at+k*1.2
        for j,n in enumerate(chord):
            note(time+j*.013,n,1.8,.035*gain,'ep',(j-1.5)/2)
            note(time,n-12,1.5,.009*gain,'pad')
        note(time,chord[0]-24,.7,.06*gain,'bass')
        note(time,0,.25,.035*gain,'kick');note(time+.6,0,.12,.021*gain,'hat')
    melody=[(0,76),(.6,79),(.9,81),(1.2,79),(1.8,76),(2.4,77),(3.0,76),(3.6,74),(4.2,71),(4.8,72)]
    for time,n in melody:note(at+time,n,1.0,.055*gain,'lead',.2)
    for n in (48,60,64,67,72):note(at+4.8,n,1.5,.028*gain,'ep')

theme(.12,2.5)
explain_start=next(s['start'] for s in segments if s['id']=='explain01')/FPS
for start in np.arange(explain_start,cursor/FPS,6.0):theme(float(start),.20)
for time,n in [(0,64),(.2,67),(.4,72),(.7,76)]:note(ending['start']/FPS+time,n,2.1,.08,'ep')
# Short clean instructional chime; no sampled source soundtrack.
chapter=next(s for s in segments if s['type']=='chapter')
note(chapter['start']/FPS,79,.7,.05,'ep');note(chapter['start']/FPS+.15,84,.9,.038,'ep')
# Music ends before the dialogue, with a short natural fade.
scene_a=round(scene['start']/FPS*SR);scene_b=round((scene['start']+scene['duration'])/FPS*SR)
fade_samples=round(.25*SR)
music[scene_a-fade_samples:scene_a]*=np.linspace(1,0,fade_samples)[:,None]
music[scene_a:scene_b]=0
# A subtle short stereo reverb evokes a stock ROMpler track.
dry=music.copy()
for seconds,level in [(.065,.17),(.13,.11),(.21,.06)]:
    n=round(seconds*SR);music[n:]+=dry[:-n,::-1]*level
music[scene_a:scene_b]=0
mix+=music

levels={}
for cue in cues:
    path=Path(cue['file'])
    measure=subprocess.run(['ffmpeg','-hide_banner','-i',str(path),'-af','loudnorm=I=-18:TP=-2:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    measured=json.JSONDecoder().raw_decode(measure.stderr[measure.stderr.rfind('{'):])[0]
    loud=float(measured['input_i']);peak=float(measured['input_tp']);gain=min(cue['target_lufs']-loud,-2-peak) if math.isfinite(loud) else 0
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vn','-af',f'highpass=f=85,lowpass=f=9000,volume={gain}dB','-f','f32le','-ar',str(SR),'-ac','2','-'])
    sound=np.frombuffer(raw,dtype='<f4').reshape(-1,2).copy();length=min(len(sound),round(cue['length']/FPS*SR));sound=sound[:length]
    edge=min(round(.008*SR),length//2)
    sound[:edge]*=np.linspace(0,1,edge)[:,None];sound[-edge:]*=np.linspace(1,0,edge)[:,None]
    start=round(cue['start']/FPS*SR);mix[start:start+length]+=sound
    levels[cue['id']]={'input_lufs':loud,'input_peak':peak,'gain_db':gain,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

fade=np.minimum(1,np.arange(samples)/(SR*.08))*np.minimum(1,np.arange(samples)[::-1]/(SR*.9))
mix*=fade[:,None]
peak=float(np.max(np.abs(mix)))
if peak>.94:mix*=.94/peak
def write_wav(path,sound):
    with wave.open(str(path),'wb') as f:
        f.setparams((2,2,SR,0,'NONE','not compressed'));f.writeframes((np.clip(sound,-1,1)*32767).astype('<i2').tobytes())
write_wav(PUB/'master.wav',mix)
write_wav(EP/'generated/original_music.wav',music)
(EP/'audio-mix-record.json').write_text(json.dumps({'sample_rate':SR,'frames':cursor,'duration':cursor/FPS,'levels':levels,'original_music':'prepare_edit.py deterministic synthesized score','reference_audio_used':False,'master_sha256':hashlib.sha256((PUB/'master.wav').read_bytes()).hexdigest(),'listening_audit':'not performed'},ensure_ascii=False,indent=2)+'\n')
print('Prepared',cursor,'frames',cursor/FPS,'seconds; pending:',pending)
