from pathlib import Path
import requests,json,wave,math,numpy as np,hashlib
P=Path(__file__).resolve().parent
version=requests.get('http://127.0.0.1:50021/version').json()
rows=json.loads((P/'dialogue.json').read_text());out=[];cursor=18*30+15
replacements={'Codex':'コーデックス','Claude Code':'クロードコード','VOICEVOX':'ボイスボックス','Remotion':'リモーション','Irodori':'イロドリ','Qwen Cloud':'クウェンクラウド','Wan 3.0':'ワン、スリーポイントゼロ','Wan':'ワン','API':'エーピーアイ','AI':'エーアイ','480p':'480ピー','720p':'720ピー','1080p':'1080ピー','h3':'エイチスリー'}
for i,r in enumerate(rows):
 speaker=2 if r['who']=='metan' else 3
 spoken=r['text']
 for a,b in replacements.items():spoken=spoken.replace(a,b)
 res=requests.post('http://127.0.0.1:50021/audio_query',params={'speaker':speaker,'text':spoken},timeout=60);res.raise_for_status();q=res.json()
 q.update(speedScale=1.13 if speaker==2 else 1.15,prePhonemeLength=.09,postPhonemeLength=.12,outputSamplingRate=24000)
 key=hashlib.sha256(json.dumps([speaker,version,q],sort_keys=True).encode()).hexdigest()[:12];name=f'voice_{i:03}_{key}.wav';f=P/'public'/name
 if not f.exists():
  res=requests.post('http://127.0.0.1:50021/synthesis',params={'speaker':speaker},json=q,timeout=120);res.raise_for_status();f.write_bytes(res.content)
 with wave.open(str(f)) as w:samples=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float)/32768;rate=w.getframerate()
 frames=math.ceil(len(samples)/rate*30)
 env=[round(float(np.sqrt(np.mean(samples[int(j*rate/30):min(len(samples),int((j+1)*rate/30))]**2))),4) for j in range(frames)]
 out.append(dict(r,startFrame=cursor,durationInFrames=frames,audio=name,speaker=speaker,spoken=spoken,kana=q['kana'],envelope=env))
 cursor+=frames+r['pause'];print(i,frames,q['kana'],flush=True)
clips=[dict(startFrame=0,durationInFrames=117,src='comedy.mp4',sourceStartFrame=60,label='会話コント｜第85話「パクられた」'),dict(startFrame=117,durationInFrames=258,src='news.mp4',sourceStartFrame=0,label='架空ニュース｜第53話「替え玉出社」'),dict(startFrame=375,durationInFrames=165,src='cm.mp4',sourceStartFrame=90,label='架空CM｜第69話「窓際スーパーつらい」')]
m={'composition':{'width':1280,'height':720,'fps':30,'durationInFrames':cursor+300},'mainStartFrame':next(d['startFrame'] for d in out if d['view']=='agent'),'endingStartFrame':next(d['startFrame'] for d in out if d['view']=='h3'),'creditsStartFrame':cursor+15,'voicevoxVersion':version,'dialogue':out,'clips':clips}
(P/'src/edit-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));print('DURATION',m['composition']['durationInFrames']/30)
