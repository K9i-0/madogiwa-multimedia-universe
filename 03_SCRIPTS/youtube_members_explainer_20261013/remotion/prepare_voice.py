from pathlib import Path
import requests,json,wave,math,numpy as np,hashlib,re
P=Path(__file__).resolve().parent
version=requests.get('http://127.0.0.1:50021/version').json()
clips=json.loads((P/'clips.json').read_text());out=[];placed=[];cursor=24;scene='intro';chapter=[]
def caption(t):
 if len(t)<=31:return t
 assert len(t)<=62, t
 lo=max(1,len(t)-31);hi=min(31,len(t)-1)
 choices=[i for i in range(lo,hi+1) if t[i] not in '、。？！）」』' and t[i-1] not in '（「『']
 preferred=[i for i in choices if t[i-1] in '、。？！']
 cut=min(preferred or choices,key=lambda i:abs(i-len(t)/2))
 return t[:cut]+'\n'+t[cut:]
for line in (P/'dialogue.txt').read_text().splitlines():
 if line.startswith('# '):
  scene=line[2:];chapter.append({'id':scene,'startFrame':cursor});continue
 if line.startswith('@'):
  c=clips[line[1:]];placed.append(dict(c,id=line[1:],startFrame=cursor));cursor+=c['durationInFrames']+18;continue
 if not line:continue
 who,view,text=line.split('|',2);who='metan' if who=='M' else 'zunda';speaker=2 if who=='metan' else 3
 spoken=text
 for a,b in [('CCO','シーシーオー'),('CEO','シーイーオー'),('CTO','シーティーオー'),('福ギュン','ふくぎゅん'),('そば屋','そばや'),('窓際力','まどぎわりょく'),('ゆめみ','ユメミ')]:spoken=spoken.replace(a,b)
 key=hashlib.sha256(json.dumps([version,speaker,spoken,1.13 if speaker==2 else 1.15],ensure_ascii=False).encode()).hexdigest()[:16];f=P.parent/f'voice_{key}.wav';qpath=P/'out'/f'query_{key}.json'
 if not f.exists() or not qpath.exists():
  res=requests.post('http://127.0.0.1:50021/audio_query',params={'speaker':speaker,'text':spoken},timeout=60);res.raise_for_status();q=res.json();q.update(speedScale=1.13 if speaker==2 else 1.15,prePhonemeLength=.09,postPhonemeLength=.12,outputSamplingRate=24000)
  res=requests.post('http://127.0.0.1:50021/synthesis',params={'speaker':speaker},json=q,timeout=120);res.raise_for_status();f.write_bytes(res.content);qpath.write_text(json.dumps(q,ensure_ascii=False))
 else:q=json.loads(qpath.read_text())
 with wave.open(str(f)) as w:samples=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float)/32768;rate=w.getframerate()
 frames=math.ceil(len(samples)/rate*30);env=[round(float(np.sqrt(np.mean(samples[int(j*rate/30):min(len(samples),int((j+1)*rate/30))]**2))),4) for j in range(frames)]
 # Captions are paged by accent phrase duration below, so each screen stays within two lines.
 phrases=q['accent_phrases'];bounds=[];at=0.09/q['speedScale']
 for a in phrases:
  for mora in a['moras']:at+=(mora.get('consonant_length') or 0)+mora['vowel_length']
  if a.get('pause_mora'):at+=a['pause_mora']['vowel_length']
 # Split natural sentences into short pages, then allocate their durations by kana/character weight.
 parts=re.findall(r'[^。！？]+[。！？]*',text);pages=[];buf=''
 for part in parts:
  if len(buf+part)>55 and buf:pages.append(buf);buf=''
  buf+=part
 if buf:pages.append(buf)
 if any(len(x)>62 for x in pages):
  pages=[chunk for p in pages for chunk in ([p] if len(p)<=62 else [p[:p.rfind('、',18,48)+1],p[p.rfind('、',18,48)+1:]]) if chunk]
 caps=[];offset=0
 for j,p in enumerate(pages):
  end=frames
  if j<len(pages)-1:
   prefix=''.join(pages[:j+1])
   for aa,bb in [('CCO','シーシーオー'),('CEO','シーイーオー'),('CTO','シーティーオー'),('福ギュン','ふくぎゅん'),('そば屋','そばや'),('窓際力','まどぎわりょく'),('ゆめみ','ユメミ')]:prefix=prefix.replace(aa,bb)
   pr=requests.post('http://127.0.0.1:50021/audio_query',params={'speaker':speaker,'text':prefix},timeout=60);pr.raise_for_status()
   count=sum(len(a['moras']) for a in pr.json()['accent_phrases']);seen=0;elapsed=q['prePhonemeLength']
   for ap in q['accent_phrases']:
    for mora in ap['moras']:
     if seen<count:elapsed+=(mora.get('consonant_length') or 0)+mora['vowel_length'];seen+=1
    if seen<=count and ap.get('pause_mora'):elapsed+=ap['pause_mora']['vowel_length']
    if seen>=count:break
   end=min(frames-1,round(elapsed/q['speedScale']*30))
  caps.append({'from':offset,'to':end,'text':caption(p)});offset=end
 out.append(dict(id=f'{len(out):03}',scene=scene,who=who,text=text,spoken=spoken,view=view,caption="\n".join(c["text"] for c in caps),captions=caps,startFrame=cursor,durationInFrames=frames,audio=f.name,speaker=speaker,kana=q['kana'],envelope=env))
 pause=12 if who=='metan' else 18
 if '……' in text or text=='そういうこともあるわね。':pause=27
 cursor+=frames+pause
 print(len(out),scene,round(cursor/30,2),flush=True)
manifest={'composition':{'width':1280,'height':720,'fps':30,'durationInFrames':cursor+180},'mainStartFrame':chapter[1]['startFrame'],'endingStartFrame':chapter[-1]['startFrame'],'creditsStartFrame':cursor+15,'voicevoxVersion':version,'chapters':chapter,'dialogue':out,'clips':placed}
(P/'src/edit-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));(P/'dialogue.json').write_text(json.dumps([{k:v for k,v in d.items() if k not in ['envelope','startFrame','durationInFrames']} for d in out],ensure_ascii=False,indent=2));print('DURATION',manifest['composition']['durationInFrames']/30)
