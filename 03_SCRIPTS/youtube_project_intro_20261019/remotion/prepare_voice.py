from pathlib import Path
import requests,json,wave,math,numpy as np,hashlib,re,sys
P=Path(__file__).resolve().parent;R=P.parents[2]
sys.path.insert(0,str(R/'.claude/skills/voicevox-control/scripts'))
from prepare_readings import load_dictionary,prepare_row
(P/'voice_queries').mkdir(exist_ok=True)
D=load_dictionary();version=requests.get('http://127.0.0.1:50021/version').json()
rows=[];chapter=[];clips=[];cursor=180;scene='intro'
from subtitle_layout import captions
for line in (P/'dialogue.txt').read_text().splitlines():
 if line.startswith('# '):scene=line[2:];chapter.append(dict(id=scene,startFrame=0 if scene=='intro' else cursor));continue
 if line.startswith('@'):
  clips.append(dict(id='proxy',src='proxy.mp4',startFrame=cursor,sourceStartFrame=0,durationInFrames=900,label='替え玉出社',audible=True));cursor+=918;continue
 if not line:continue
 who,view,text=line.split('|',2);who='metan' if who=='M' else 'zunda';speaker=2 if who=='metan' else 3
 row=dict(id=f'{len(rows):03}',text=text)
 if '動きや間が' in text:row['speech_override']=text.replace('動きや間が','動きやマが')
 if '@sobaya15' in text:row['speech_override']='エックスでは、そば屋が、アットマーク、そばや、いちごー。たこさんが、アットマーク、ケーナインアイ、アンダーバー、アップス。画面と概要欄にリンクを載せておくわ。'
 if 'madogiwa.work' in text:row['speech_override']=text.replace('madogiwa.work','まどぎわドットワーク')
 prepared=prepare_row(row,D,scopes=['mmu','tech']);spoken=prepared['speech']
 requestkey=hashlib.sha256(json.dumps([version,speaker,spoken],ensure_ascii=False).encode()).hexdigest()[:16]
 rq=P/'out'/f'request_{requestkey}.json'
 if rq.exists():q=json.loads(rq.read_text())
 else:
  res=requests.post('http://127.0.0.1:50021/audio_query',params=dict(speaker=speaker,text=spoken),timeout=60);res.raise_for_status();q=res.json();rq.write_text(json.dumps(q,ensure_ascii=False))
 q.update(speedScale=1.13 if speaker==2 else 1.15,prePhonemeLength=.09,postPhonemeLength=.12,outputSamplingRate=24000)
 key=hashlib.sha256(json.dumps([version,speaker,q],ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:16];f=P.parent/f'voice_{key}.wav'
 (P/'voice_queries'/f'query_{key}.json').write_text(json.dumps(q,ensure_ascii=False,indent=2))
 if not f.exists():
  res=requests.post('http://127.0.0.1:50021/synthesis',params=dict(speaker=speaker),json=q,timeout=120);res.raise_for_status();f.write_bytes(res.content)
 with wave.open(str(f)) as w:samples=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float)/32768;rate=w.getframerate()
 frames=math.ceil(len(samples)/rate*30);env=[round(float(np.sqrt(np.mean(samples[int(j*rate/30):min(len(samples),int((j+1)*rate/30))]**2))),4) for j in range(frames)]
 rows.append(dict(**prepared,who=who,scene=scene,view=view,startFrame=cursor,durationInFrames=frames,audio=f.name,speaker=speaker,kana=q['kana'],queryFile=f'voice_queries/query_{key}.json',envelope=env,captions=captions(text,frames)))
 cursor+=frames+(18 if who=='zunda' else 12)
 print(len(rows),scene,round(cursor/30,1),flush=True)
m=dict(composition=dict(width=1280,height=720,fps=30,durationInFrames=cursor+120),mainStartFrame=chapter[1]['startFrame'],endingStartFrame=chapter[-1]['startFrame'],voicevoxVersion=version,chapters=chapter,dialogue=rows,clips=clips)
(P/'src/edit-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
(P.parent/'voice_generation_record.json').write_text(json.dumps([ {k:v for k,v in row.items() if k not in ['envelope','captions']} for row in rows],ensure_ascii=False,indent=2))
print('DURATION',m['composition']['durationInFrames']/30)
