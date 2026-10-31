"""Build v3 from dialogue.txt with five chapter cards and cached AudioQueries."""
from pathlib import Path
import requests,json,wave,math,numpy as np,hashlib,sys,concurrent.futures
P=Path(__file__).resolve().parent; R=P.parents[2]
sys.path.insert(0,str(R/'.claude/skills/voicevox-control/scripts'))
from prepare_readings import load_dictionary,prepare_row
from subtitle_layout import captions
for folder in ['out','voice_queries','public','src']:(P/folder).mkdir(exist_ok=True)
D=load_dictionary(local_path=P/'readings.json')
chapter_specs={c['id']:c for c in json.loads((P/'chapters.json').read_text())}
version=requests.get('http://127.0.0.1:50021/version',timeout=10).json()
events=[];scene='intro';index=0
for line in (P/'dialogue.txt').read_text().splitlines():
 if not line:continue
 if line.startswith('# '):scene=line[2:];events.append(dict(type='chapter',id=scene));continue
 if line.startswith('@clip|'):
  _,src,start,duration,label=line.split('|');events.append(dict(type='clip',src=src,sourceStartFrame=round(float(start)*30),durationInFrames=round(float(duration)*30),label=label,audible=True));continue
 who,view,text=line.split('|',2)
 events.append(dict(type='dialogue',id=f'{index:03}',who='metan' if who=='M' else 'zunda',view=view,text=text,scene=scene));index+=1

def generate(row):
 speaker=2 if row['who']=='metan' else 3
 prepared=prepare_row(row,D,scopes=['mmu','tech'])
 requestkey=hashlib.sha256(json.dumps([version,speaker,prepared['speech']],ensure_ascii=False).encode()).hexdigest()[:16]
 rq=P/'out'/f'request_{requestkey}.json'
 if rq.exists():q=json.loads(rq.read_text())
 else:
  res=requests.post('http://127.0.0.1:50021/audio_query',params=dict(speaker=speaker,text=prepared['speech']),timeout=120);res.raise_for_status();q=res.json();rq.write_text(json.dumps(q,ensure_ascii=False))
 q.update(speedScale=1.13 if speaker==2 else 1.15,prePhonemeLength=.09,postPhonemeLength=.12,outputSamplingRate=24000)
 key=hashlib.sha256(json.dumps([version,speaker,q],ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:16]
 path=P.parent/f'voice_{key}.wav';qfile=f'voice_queries/query_{key}.json'
 (P/qfile).write_text(json.dumps(q,ensure_ascii=False,indent=2))
 if not path.exists():
  res=requests.post('http://127.0.0.1:50021/synthesis',params=dict(speaker=speaker),json=q,timeout=240);res.raise_for_status();path.write_bytes(res.content)
 with wave.open(str(path)) as w:
  assert w.getnchannels()==1 and w.getsampwidth()==2
  samples=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float)/32768;rate=w.getframerate()
 assert len(samples)>rate*.2 and np.max(np.abs(samples))>.01
 frames=math.ceil(len(samples)/rate*30)
 env=[round(float(np.sqrt(np.mean(samples[int(j*rate/30):min(len(samples),int((j+1)*rate/30))]**2))),4) for j in range(frames)]
 prepared.update(durationInFrames=frames,audio=path.name,speaker=speaker,kana=q['kana'],queryFile=qfile,envelope=env,captions=captions(row['text'],frames),audioSha256=hashlib.sha256(path.read_bytes()).hexdigest())
 print(row['id'],row['view'],round(frames/30,2),flush=True)
 return prepared

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 generated={r['id']:r for r in pool.map(generate,[r for r in events if r['type']=='dialogue'])}
cursor=45;rows=[];chapters=[];clips=[]
for event in events:
 if event['type']=='chapter':
  spec=chapter_specs[event['id']]
  chapters.append(dict(**spec,startFrame=0 if event['id']=='intro' else cursor))
  cursor+=spec['cardFrames']
 elif event['type']=='clip':
  clips.append(dict(**event,id=f'clip-{len(clips)}',startFrame=cursor));cursor+=event['durationInFrames']+21
 else:
  row=generated[event['id']];row['startFrame']=cursor;rows.append(row)
  gap=18 if row['who']=='zunda' else 12
  if row['text']=='そうね！':gap=30
  cursor+=row['durationInFrames']+gap
m=dict(revision='v3',audience='AIツールは使うが、動画モデルの自力実行・Colab・Hugging Face・GPU運用は未経験の人',composition=dict(width=1280,height=720,fps=30,durationInFrames=cursor+120),mainStartFrame=chapters[1]['startFrame'],endingStartFrame=chapters[-1]['startFrame'],voicevoxVersion=version,chapters=chapters,dialogue=rows,clips=clips)
(P/'src/edit-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
(P.parent/'voice_generation_record_v3.json').write_text(json.dumps([{k:v for k,v in row.items() if k not in ['envelope','captions']} for row in rows],ensure_ascii=False,indent=2))
print('DURATION',m['composition']['durationInFrames']/30,flush=True)
