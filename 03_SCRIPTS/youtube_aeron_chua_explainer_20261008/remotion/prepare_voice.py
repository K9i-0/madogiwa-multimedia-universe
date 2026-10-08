from pathlib import Path
import requests,json,wave,math,numpy as np,hashlib
P=Path(__file__).resolve().parent
rows=json.loads((P/'dialogue.json').read_text());out=[];clips=[];cursor=24
for i,r in enumerate(rows):
 speaker=2 if r['who']=='metan' else 3
 text=r['text'];spoken=text.replace('AERON CHUA','アーロンチュア').replace('DIY','ディーアイワイ')
 qres=requests.post('http://127.0.0.1:50021/audio_query',params={'speaker':speaker,'text':spoken},timeout=60);qres.raise_for_status();q=qres.json()
 q.update(speedScale=1.13 if speaker==2 else 1.15,prePhonemeLength=.09,postPhonemeLength=.12,outputSamplingRate=24000)
 key=hashlib.sha256(json.dumps(q,sort_keys=True).encode()).hexdigest()[:10];name=f'voice_{i:02}_{key}.wav';f=P/'public'/name
 if not f.exists():
  res=requests.post('http://127.0.0.1:50021/synthesis',params={'speaker':speaker},json=q,timeout=120);res.raise_for_status();f.write_bytes(res.content)
 with wave.open(str(f)) as w:samples=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float)/32768;rate=w.getframerate()
 frames=math.ceil(len(samples)/rate*30)
 envelope=[round(float(np.sqrt(np.mean(samples[int(j*rate/30):int((j+1)*rate/30)]**2))),4) for j in range(frames)]
 caption=r.get('captionText',text)
 if len(caption)>30:
  mid=len(caption)/2;candidates=[j+1 for j,c in enumerate(caption[:-1]) if c in '、。？']
  choices=[j for j in candidates if max(j,len(caption)-j)<=36]
  at=min(choices,key=lambda x:abs(x-mid)) if choices else round(mid)
  caption=caption[:at]+'\n'+caption[at:]
 assert max(map(len,caption.split('\n')))<=36,(i,caption)
 out.append(dict(r,caption=caption,startFrame=cursor,durationInFrames=frames,audio=name,speaker=speaker,kana=q['kana'],envelope=envelope))
 cursor+=frames+r['pause']
 if 'clipAfter' in r:
  clips.append(dict(r['clipAfter'],startFrame=cursor));cursor+=r['clipAfter']['durationInFrames']+15
 print(i,round(frames/30,2),q['kana'],flush=True)
main=next(d['startFrame'] for d in out if d['scene']=='origin')-6
ending=next(d['startFrame'] for d in out if d.get('endingStart'))
manifest={'endingStartFrame':ending,'composition':{'width':1280,'height':720,'fps':30,'durationInFrames':cursor+150},'mainStartFrame':main,'creditsStartFrame':cursor+15,'voicevoxVersion':requests.get('http://127.0.0.1:50021/version').json(),'dialogue':out,'clips':clips}
(P/'src/edit-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print('DURATION',manifest['composition']['durationInFrames']/30)
