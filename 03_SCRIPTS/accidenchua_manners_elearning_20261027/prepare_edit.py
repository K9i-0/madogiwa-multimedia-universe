"""Build frame-accurate edit manifest, exact-text captions and reproducible PCM mix."""
import difflib,hashlib,json,math,re,shutil,subprocess,unicodedata,wave
from pathlib import Path
import numpy as np

EP=Path(__file__).resolve().parent;ROOT=EP.parents[1];PUB=EP/'remotion/public';FPS=24;SR=48000
for sub in ('audio','h3','stills','music'): (PUB/sub).mkdir(parents=True,exist_ok=True)
d=json.loads((EP/'content.json').read_text());voices=json.loads((EP/'voice-records.json').read_text())
overrides=json.loads((EP/'edit-overrides-r2.json').read_text())
sources=json.loads((EP/'scene-sources.json').read_text())
shutil.copy2(ROOT/'01_WORLD/props/accidenchua/logo-dark.png',PUB/'logo.png')
pending=[];segments=[];audio_cues=[];captions=[];cursor=0
def fr(t):return round(t*FPS)
def segment(id,type,duration,chapter=None):
 global cursor
 s={'id':id,'type':type,'start':cursor,'duration':duration}
 if chapter:s['chapter']=chapter
 segments.append(s);cursor+=duration;return s
def cue(line,start):
 r=voices[line['id']];audio_cues.append({'file':r['file'],'start':start,'speaker':line['speaker'],'id':line['id']})
 return fr(r['duration'])
def normalized(s):
 s=unicodedata.normalize('NFKC',s).replace('一日','1日').replace('三十分','30分').replace('そば屋','そばや')
 return ''.join(c for c in s if c.isalnum())
def wrap(s,maxlen=30):
 if len(s)<=maxlen:return s
 middle=len(s)//2
 candidates=[j if c in '『「' else j+1 for j,c in enumerate(s) if c in '、。『「' and abs(j-middle)<10]
 at=min(candidates,key=lambda j:abs(j-middle)) if candidates else middle
 if s[at:at+1] in '、。』」）':at+=1
 return s[:at]+'\n'+s[at:]
def sentence_caps(line,start):
 r=voices[line['id']];text=line['text'];sentences=re.findall(r'.+?[。！？](?:[』」])?|.+$',text)
 a=EP/'generated/asr'/f'{Path(r["file"]).stem}.json'
 if not a.exists():pending.append(line['id']+'_ASR')
 asr=json.loads(a.read_text()) if a.exists() else {'offsets':[]}
 offsets=asr.get('offsets',[])
 joined=''.join(x['text'] for x in offsets);source=normalized(text);target=normalized(joined)
 matcher=difflib.SequenceMatcher(None,source,target,autojunk=False)
 def index_map(n):
  for tag,a1,a2,b1,b2 in matcher.get_opcodes():
   if a1<=n<=a2:return b1+(n-a1)*(b2-b1)/max(1,a2-a1)
  return len(target)
 def time_at(n,end=False):
  pos=0
  for x in offsets:
   length=len(normalized(x['text']));lo,hi=x['timestamp'];hi=min(hi,r['duration'])
   if pos<=n<pos+length or (end and n==pos+length):return lo+(hi-lo)*(n-pos)/max(1,length)
   pos+=length
  return r['duration']*n/max(1,len(target))
 index=0
 for sentence in sentences:
  size=len(normalized(sentence));lo=time_at(index_map(index)) if offsets else r['duration']*index/max(1,len(source))
  index+=size;hi=time_at(index_map(index),end=True) if offsets else r['duration']*index/max(1,len(source))
  captions.append({'start':start+fr(lo),'end':start+max(fr(lo)+1,fr(hi)),'text':wrap(sentence),'speaker':'anchor','source':'canonical text; ASR segment alignment'})

def dialogue_bounds(ch,source,asr_path):
 """Combine transcript positions with audible-energy groups; avoid ASR silence spans."""
 spans=json.loads(asr_path.read_text()).get('offsets',[])
 full=normalized(''.join(line['text'] for line in ch['dialogue']))
 spoken=normalized(''.join(x['text'] for x in spans))
 matches=difflib.SequenceMatcher(None,full,spoken,autojunk=False).get_opcodes()
 def map_index(n):
  for tag,a1,a2,b1,b2 in matches:
   if a1<=n<=a2:return b1+(n-a1)*(b2-b1)/max(1,a2-a1)
  return len(spoken)
 def stamp(n,end=False):
  pos=0
  for x in spans:
   size=len(normalized(x['text']));lo,hi=x['timestamp']
   if pos<=n<pos+size or (end and n==pos+size):return lo+(hi-lo)*(n-pos)/max(1,size)
   pos+=size
  return spans[-1]['timestamp'][1] if spans else 12.95
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(source),'-af','highpass=f=100','-f','f32le','-ar','16000','-ac','1','-'])
 samples=np.frombuffer(raw,dtype='<f4');size=320
 rms=np.sqrt(np.mean(samples[:len(samples)//size*size].reshape(-1,size)**2,axis=1)+1e-12)
 db=20*np.log10(rms);threshold=max(-44,min(-34,float(db.max())-28));active=np.where(db>threshold)[0]
 groups=[]
 if len(active):
  begin=previous=int(active[0])
  for x in active[1:]:
   if x-previous>23:groups.append((begin*.02,(previous+1)*.02));begin=int(x)
   previous=int(x)
  groups.append((begin*.02,(previous+1)*.02))
 pos=0;result={}
 for line in ch['dialogue']:
  lo=stamp(map_index(pos));pos+=len(normalized(line['text']));hi=stamp(map_index(pos),True)
  candidates=[(a,b) for a,b in groups if max(0,min(b,hi)-max(a,lo))/max(.01,b-a)>.30]
  if candidates:lo=max(0,min(a for a,b in candidates)-.12);hi=min(len(samples)/16000,max(b for a,b in candidates)+.12)
  result[line['id']]=(lo,hi)
 return result

op_start=fr(1.0);op_cues=[]
for line in d['opening']:
 length=cue(line,op_start);op_cues.append(op_start);op_start+=length+fr(.55)
op=segment('opening','opening',op_start+fr(.85));opening_split=op_cues[1]

for ch in d['chapters']:
 number=ch['number'];key=ch['id']
 segment(key+'_title','title',fr(2.0),number)
 config=sources[key];source=EP/config['video']
 video=PUB/'h3'/source.name
 ready=source.exists()
 if ready:
  if not video.exists() or hashlib.sha256(video.read_bytes()).digest()!=hashlib.sha256(source.read_bytes()).digest():shutil.copy2(source,video)
 else:pending.append(key+'_H3')
 ch['video']='h3/'+source.name;ch['videoReady']=ready
 wf=json.loads((EP/config['workflow']).read_text());frames=wf['136']['inputs']['length']
 override=overrides.get(key,{})
 frames=min(frames,override.get('duration_frames',frames))
 reference_starts=override.get('dialogue_starts',{})
 ch['audioMode']='canonical WAV replacement' if reference_starts else 'H3 generated audio'
 clip=segment(key+'_clip','clip',frames,number)
 if ready and not reference_starts:audio_cues.append({'file':str(source.relative_to(EP)),'start':clip['start'],'speaker':'scene','id':key+'_scene','lengthFrames':frames})
 h3_asr=EP/config['asr']
 speech_times=dialogue_bounds(ch,source,h3_asr) if ready and h3_asr.exists() and not reference_starts else {}
 planned=1.3
 for line in ch['dialogue']:
  duration=voices[line['id']]['duration'];lo=planned;hi=planned+duration
  if line['id'] in reference_starts:
   lo=reference_starts[line['id']]/FPS;hi=lo+duration
   cue(line,clip['start']+reference_starts[line['id']])
  elif line['id'] in speech_times:
   lo,hi=speech_times[line['id']]
  else:pending.append(key+'_speech_alignment')
  captions.append({'start':clip['start']+fr(lo),'end':min(clip['start']+frames,clip['start']+fr(hi)),'text':wrap(line['text']),'speaker':line['speaker'],'source':'canonical WAV timing' if reference_starts else 'H3 ASR alignment plus energy bounds' if h3_asr.exists() else 'provisional reference timing'})
  planned+=duration+.65
 still=PUB/'stills'/f'{key}.png'
 if ready:subprocess.run(['ffmpeg','-y','-v','error','-ss',str(config.get('still_seconds',4.5)),'-i',str(source),'-frames:v','1',str(still)],check=True)
 ch['still']='stills/'+key+'.png';ch['stillReady']=ready and still.exists()
 qlen=fr(voices[ch['question']['id']]['duration'])
 q=segment(key+'_question','question',max(fr(9),qlen+fr(3)),number);cue(ch['question'],q['start']+fr(.35))
 segment(key+'_answer','answer',fr(1.7),number)
 for fi,feedback in enumerate(ch['feedback']):
  line=feedback['line'];elen=fr(voices[line['id']]['duration'])
  e=segment(key+'_feedback_'+'abc'[feedback['option']],'feedback',elen+fr(1.4),number)
  e.update(feedbackIndex=fi,option=feedback['option'],correct=feedback['correct'],lineId=line['id'])
  cue(line,e['start']+fr(.35));sentence_caps(line,e['start']+fr(.35))

end_start=cursor;offset=fr(.7)
for line in d['ending']:
 if line['id']=='end02':ending_thanks_offset=offset
 offset+=cue(line,end_start+offset)+fr(.55)
segment('ending','ending',offset+fr(1.2))

# Original corporate-training music: deterministic piano/mallet chords, no sampled recording.
samples=round(cursor/FPS*SR);mix=np.zeros((samples,2),np.float32)
rng=np.random.default_rng(20261027)
music=np.zeros((samples,2),np.float32)
def add_note(at,duration,midi,volume,pan=0.0):
 start=round(at*SR);n=min(round(duration*SR),samples-start)
 if n<=0:return
 t=np.arange(n)/SR;freq=440*2**((midi-69)/12)
 env=(1-np.exp(-t*90))*np.exp(-t*2.7)
 sound=(np.sin(2*np.pi*freq*t)+.25*np.sin(2*np.pi*freq*2*t)+.07*np.sin(2*np.pi*freq*3*t))*env*volume
 music[start:start+n,0]+=sound*(.75-.25*pan);music[start:start+n,1]+=sound*(.75+.25*pan)
beat=60/104;chords=[(60,64,67,71),(57,60,64,67),(53,57,60,64),(55,59,62,67)]
for bar in range(math.ceil(cursor/FPS/(4*beat))):
 chord=chords[(bar//2)%4];at=bar*4*beat
 for j,note in enumerate(chord):add_note(at+j*.012,2.2,note,.023,(j-1.5)/2)
 for k,idx in enumerate([0,2,1,3,2,1,3,2]):add_note(at+k*beat/2,1.1,chord[idx]+12,.014,(-1 if k%2 else 1)*.4)
 add_note(at,1.5,chord[0]-12,.025)
# Apply low music under speech, more presence during the corporate opening and thinking time.
gain=np.full(samples,.43,dtype=np.float32)
for s in segments:
 if s['type'] in ('opening','title','question','answer','ending'):
  gain[round(s['start']/FPS*SR):round((s['start']+s['duration'])/FPS*SR)]=.9
for s in segments:
 if s['type']=='clip':
  lo=round(s['start']/FPS*SR);hi=round((s['start']+s['duration'])/FPS*SR);ramp=round(.15*SR)
  gain[lo:hi]=0
  gain[max(0,lo-ramp):lo]*=np.linspace(1,0,min(ramp,lo))
  gain[hi:min(samples,hi+ramp)]*=np.linspace(0,1,min(ramp,samples-hi))
music*=gain[:,None];fade=np.minimum(1,np.arange(samples)/(SR*1.0))*np.minimum(1,np.arange(samples)[::-1]/(SR*1.2));music*=fade[:,None]
mix+=music

levels={}
for c in audio_cues:
 source=EP/c['file'];normalized_file=PUB/'audio'/f'{c["id"]}_mix.wav'
 cache_record=normalized_file.with_suffix('.json');digest=hashlib.sha256(source.read_bytes()).hexdigest()
 cached=json.loads(cache_record.read_text()) if cache_record.exists() else {}
 if not normalized_file.exists() or cached.get('source_sha256')!=digest:
  proc=subprocess.run(['ffmpeg','-hide_banner','-i',str(source),'-af','loudnorm=I=-18:TP=-1.8:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
  measurement=json.JSONDecoder().raw_decode(proc.stderr[proc.stderr.rfind('{'):])[0];integrated=float(measurement['input_i']);peak=float(measurement['input_tp'])
  volume=min(-18-integrated,-1.8-peak) if math.isfinite(integrated) else 0
  subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-vn','-af',f'volume={volume}dB','-ar',str(SR),'-ac','2','-c:a','pcm_s16le',str(normalized_file)],check=True)
  cached={'source_sha256':digest,'input_i':integrated,'input_tp':peak,'gain_db':volume}
  cache_record.write_text(json.dumps(cached,indent=2)+'\n')
 levels[c['id']]=cached
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(normalized_file),'-f','f32le','-ar',str(SR),'-ac','2','-'])
 audio=np.frombuffer(raw,dtype='<f4').reshape(-1,2);start=round(c['start']/FPS*SR);length=min(len(audio),samples-start,round(c.get('lengthFrames',cursor)/FPS*SR))
 mix[start:start+length]+=audio[:length]

def chime(at,frequencies):
 for k,freq in enumerate(frequencies):
  start=round((at+k*.11)*SR);n=min(round(.5*SR),samples-start)
  if n<=0:continue
  t=np.arange(n)/SR;waveform=.045*np.sin(2*np.pi*freq*t)*np.exp(-t*9)*(1-np.exp(-t*250))
  mix[start:start+n]+=waveform[:,None]
for s in segments:
 if s['type'] in ('title','answer'):chime(s['start']/FPS,[660,880] if s['type']=='answer' else [660])
 if s['type']=='question':
  for second in (3,2,1):chime((s['start']+s['duration'])/FPS-second,[770])
chime(end_start/FPS,[523.25,659.25,783.99])
peak=float(np.max(np.abs(mix)))
if peak>.95:mix*=.95/peak
premaster=EP/'generated/premaster.wav'
with wave.open(str(premaster),'wb') as w:
 w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(mix,-1,1)*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-y','-v','error','-i',str(premaster),'-af','loudnorm=I=-16:TP=-1.5:LRA=9','-ar',str(SR),'-c:a','pcm_s16le',str(PUB/'audio/master.wav')],check=True)
for s in segments:
 if s['type']=='clip':
  subprocess.run(['ffmpeg','-y','-v','error','-ss',str(s['start']/FPS),'-i',str(PUB/'audio/master.wav'),'-t',str(s['duration']/FPS),str(EP/'generated'/f'final_{s["id"]}_mix.wav')],check=True)
manifest={'composition':{'id':'AccidenchuaManners','width':1280,'height':720,'fps':FPS,'durationInFrames':cursor},'title':d['title'],'revision':d['revision'],'outputFile':d['outputFile'],'sourceClips':sources,'chapters':d['chapters'],'segments':segments,'captions':captions,'audioCues':audio_cues,'openingSplit':opening_split,'endingThanksOffset':ending_thanks_offset,'pending':sorted(set(pending)),'music':{'source':'original procedural score in prepare_edit.py','seed':20261027,'bpm':104},'voiceGain':levels}
(EP/'remotion/src/edit-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Duration',cursor,'frames =',cursor/FPS,'seconds; pending:',manifest['pending'])
