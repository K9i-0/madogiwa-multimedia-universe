"""Build frame-accurate H3 edit using adopted Irodori performances, unmodified speed."""
from pathlib import Path
import hashlib,json,math,os,subprocess
import numpy as np
P=Path(__file__).resolve().parent; EP=P.parent; ROOT=EP.parents[1]
PUBLIC=EP/'remotion/public'; OUT=PUBLIC/'h3';OUT.mkdir(exist_ok=True)
results=ROOT/'.local/h3-keynote-20261026/colab-job/results'
chapters=json.loads((P/'chapter_plan.json').read_text()); rows={r['id']:r for r in json.loads((P/'audio_manifest.json').read_text())};dialogue={r['id']:r for r in json.loads((EP/'remotion/src/dialogue.json').read_text())}
shots=[];lines=[];offset=0
for ch in chapters:
 src=results/(ch['id']+'_480p.mp4');dest=OUT/src.name
 if not dest.exists():os.link(src,dest)
 length=ch['frames']-(36 if ch['id']=='ch13' else 0); shot=dict(id=ch['id'],start=offset,end=offset+length,video='h3/'+src.name,scene=ch['scene'],trimStart=0)
 if ch['id']=='ch13':
  shots.extend([{**shot,'id':'ch13a','end':offset+174},{**shot,'id':'ch13b','start':offset+174,'trimStart':210}])
 else:shots.append(shot)
 durations=[math.ceil(rows[i]['speech_seconds']*24) for i in ch['lines']]
 pauses=[dialogue[i]['pauseFrames'] for i in ch['lines']]
 if ch['id']=='ch13':pauses[-1]-=36
 # Give each shot a short settling beat; preserve all original speech and reaction pauses.
 spare=length-sum(durations)-sum(pauses); lead=min(12,max(0,spare));cursor=offset+lead
 for idx,duration,pause in zip(ch['lines'],durations,pauses):
  row=rows[idx]; source=ROOT/row['source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==row['source_sha256']
  lines.append(dict(id=idx,speaker='sobaya',text=row['text'],start=cursor,end=cursor+duration,audio=source.name,pauseFrames=pause,shot=ch['id'],source_sha256=row['source_sha256']))
  cursor+=duration+pause
 assert lines[-1]['end']<=shot['end'],ch['id']
 offset+=length
m=dict(fps=24,width=1280,height=720,durationInFrames=offset,shots=shots,lines=lines,audio='audio/master-h3.wav',audioPolicy='Mute H3 audio; adopted Irodori original dialogue without speed change',screenPolicy='H3 original screen retained; no replacement',soundEvents=[])
SR=48000;N=offset*2000;master=np.zeros((N,2),np.float32);voice=np.zeros(N,np.float32)
def decode(path,filters):
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-af',filters,'-ar',str(SR),'-ac','2','-f','f32le','-'])
 return np.frombuffer(raw,dtype='<f4').reshape(-1,2).copy()
def add(a,start):
 n=min(len(a),N-start)
 if n>0:master[start:start+n]+=a[:n]
for l in lines:
 a=decode(EP/l['audio'],'loudnorm=I=-18:TP=-2:LRA=7');start=l['start']*2000
 assert len(a)<= (l['end']-l['start'])*2000+1
 add(a,start);voice[start:start+len(a)]=1
ap=decode(EP/'audio_sources/applause_cc0.ogg','loudnorm=I=-20:TP=-3:LRA=7');la=decode(EP/'audio_sources/laughter_ccby4.mp3','loudnorm=I=-23:TP=-3:LRA=7')
def reaction(source,start,frames,source_offset,gain,kind):
 n=frames*2000;pos=start*2000;n=min(n,N-pos)
 if n<=0:return
 a=source[int(source_offset*SR):int(source_offset*SR)+n].copy()
 if len(a)<n:a=np.pad(a,((0,n-len(a)),(0,0)))
 fi=min(7200,n//4);fo=min(31200,n//3);a[:fi]*=np.linspace(0,1,fi)[:,None];a[-fo:]*=np.linspace(1,0,fo)[:,None]
 a*=(1-.82*voice[pos:pos+n,None])*gain;add(a,pos)
 m['soundEvents'].append(dict(kind=kind,start=start,durationInFrames=frames,sourceOffsetSeconds=source_offset,gain=gain))
for i,l in enumerate(lines):
 if l['id'] in ['three','first','second','third','understand','reveal','arms','wear','today','all']:
  reaction(ap,l['end']+3,max(1,l['pauseFrames']-1),(i*3)%38,1.2 if l['id'] in ['reveal','third'] else .8,'applause')
 if l['id'] in ['repeat2','nobody']:reaction(la,l['end']+2,50,0,1,'laughter')
# Continuous low reflection, final fade; do not invent an additional voice.
echo=int(.075*SR);master[echo:]+=master[:-echo]*.045
fade=SR;master[-fade:]*=np.linspace(1,0,fade)[:,None]
peak=float(abs(master).max());gain=min(1,.94/peak);master*=gain
wav=PUBLIC/m['audio'];subprocess.run(['ffmpeg','-y','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-c:a','pcm_s16le',str(wav)],input=master.astype('<f4').tobytes(),check=True)
(EP/'remotion/src/edit-manifest-h3.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
(P/'audio-mix.json').write_text(json.dumps(dict(sampleRate=SR,channels=2,dialogueCount=len(lines),sourceHashesVerified=True,peakBeforeLimiter=peak,masterGain=gain,masterSha256=hashlib.sha256(wav.read_bytes()).hexdigest(),auditoryReview='Not performed by this tool; adopted source performances reused'),indent=2)+'\n')
print('Prepared',len(shots),'shots',len(lines),'lines',offset,'frames')
