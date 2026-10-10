from pathlib import Path
import requests,json,wave,math,numpy as np,hashlib,os
P=Path(__file__).resolve().parent
version=requests.get('http://127.0.0.1:50021/version',timeout=10).json()
rows=json.loads((P/'dialogue.json').read_text());out=[];cursor=30;visual_cues={}
for i,r in enumerate(rows):
 speaker=2 if r['who']=='metan' else 3
 spoken=r['text'].replace('通って','トオッテ').replace('福ギュン','フクギュン').replace('人型','ヒトガタ').replace('原個体','ゲンコタイ').replace('霜重','シモジュウ').replace('中口','ナカグチ').replace('北原','キタハラ').replace('江本','エモト')
 res=requests.post('http://127.0.0.1:50021/audio_query',params={'speaker':speaker,'text':spoken},timeout=60);res.raise_for_status();q=res.json()
 q.update(speedScale=1.08 if speaker==2 else 1.13,prePhonemeLength=.09,postPhonemeLength=.12,outputSamplingRate=24000)
 key=hashlib.sha256(json.dumps({'query':q,'speaker':speaker,'engine':version},sort_keys=True).encode()).hexdigest()[:12];name=f'voice_{i:03}_{key}.wav';f=P/'public'/name
 if not f.exists():
  cached=next((P/'public').glob(f'voice_*_{key}.wav'),None)
  if cached is not None:os.link(cached,f)
 if not f.exists():
  res=requests.post('http://127.0.0.1:50021/synthesis',params={'speaker':speaker},json=q,timeout=120);res.raise_for_status();f.write_bytes(res.content)
 with wave.open(str(f)) as w:samples=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float)/32768;rate=w.getframerate()
 frames=math.ceil(len(samples)/rate*30)
 envelope=[round(float(np.sqrt(np.mean(samples[int(j*rate/30):int((j+1)*rate/30)]**2))),4) if len(samples[int(j*rate/30):int((j+1)*rate/30)]) else 0 for j in range(frames)]
 caption=r['text']
 if len(caption)>30:
  candidates=[j+1 for j,c in enumerate(caption[:-1]) if c in '、。？']
  choices=[j for j in candidates if max(j,len(caption)-j)<=38]
  at=min(choices,key=lambda x:abs(x-len(caption)/2)) if choices else round(len(caption)/2)
  caption=caption[:at]+'\n'+caption[at:]
 assert max(map(len,caption.split('\n')))<=38,(i,caption)
 # Align graphics to the synthesized mora timeline, scaled to measured WAV duration.
 moras=[];clock=q['prePhonemeLength'];flat=''
 for phrase in q['accent_phrases']:
  for mora in phrase['moras']:
   moras.append((len(flat),clock));flat+=mora['text'];clock+=(mora.get('consonant_length') or 0)+mora['vowel_length']
  if phrase.get('pause_mora'):clock+=phrase['pause_mora']['vowel_length']
 clock+=q['postPhonemeLength']
 for cue in r.get('visualCues',[]):
  pos=flat.find(cue['kana']);assert pos>=0,(i,cue,flat)
  seconds=next(t for char,t in moras if char==pos)/clock*(len(samples)/rate)
  assert cue['id'] not in visual_cues
  visual_cues[cue['id']]={'frame':cursor+round(seconds*30),'dialogueIndex':i,'kana':cue['kana']}
 out.append(dict(r,caption=caption,startFrame=cursor,durationInFrames=frames,audio=name,speaker=speaker,kana=q['kana'],envelope=envelope));cursor+=frames+r['pause']
 print(i,round(cursor/30,1),flush=True)
manifest={'composition':{'width':1280,'height':720,'fps':30,'durationInFrames':cursor+240},'visualCues':visual_cues,'creditsStartFrame':cursor+30,'voicevoxVersion':version,'dialogue':out}
(P/'src/edit-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print('DURATION',manifest['composition']['durationInFrames']/30)

def stamp(frame):
 ms=round(frame/30*1000);return f"{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}"
(P.parent/'subtitles_ja.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(d['startFrame'])} --> {stamp(d['startFrame']+d['durationInFrames'])}\n{d['caption']}" for i,d in enumerate(out))+'\n')
