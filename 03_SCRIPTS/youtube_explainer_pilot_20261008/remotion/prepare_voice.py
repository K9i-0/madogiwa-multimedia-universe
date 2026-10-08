from pathlib import Path
import requests,json,wave,math,numpy as np
P=Path(__file__).resolve().parent
rows=json.loads((P/'dialogue.json').read_text());out=[];cursor=24
for i,r in enumerate(rows):
 if i==4:cursor+=45
 speaker=2 if r['who']=='metan' else 3
 q=requests.post('http://127.0.0.1:50021/audio_query',params={'speaker':speaker,'text':r['text']}).json()
 q.update(speedScale=1.13 if speaker==2 else 1.15,prePhonemeLength=.09,postPhonemeLength=.12,outputSamplingRate=24000)
 name=f'voice_{i:02}.wav';f=P/'public'/name
 if not f.exists():
  res=requests.post('http://127.0.0.1:50021/synthesis',params={'speaker':speaker},json=q);res.raise_for_status();f.write_bytes(res.content)
 with wave.open(str(f)) as w:
  samples=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float)/32768;rate=w.getframerate()
 frames=math.ceil(len(samples)/rate*30)
 envelope=[round(float(np.sqrt(np.mean(samples[int(j*rate/30):int((j+1)*rate/30)]**2))),4) for j in range(frames)]
 out.append(dict(r,startFrame=cursor,durationInFrames=frames,audio=name,speaker=speaker,kana=q['kana'],envelope=envelope))
 cursor+=frames+9
 print(i,round(frames/30,2),q['kana'],flush=True)
main=out[4]['startFrame']-12
manifest={'composition':{'width':1280,'height':720,'fps':30,'durationInFrames':cursor+120},'mainStartFrame':main,'creditsStartFrame':cursor+15,'voicevoxVersion':requests.get('http://127.0.0.1:50021/version').json(),'dialogue':out}
(P/'src/edit-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('DURATION',manifest['composition']['durationInFrames']/30)
