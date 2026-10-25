from pathlib import Path
import json,sys,hashlib,wave,math,urllib.request,urllib.parse,numpy as np
P=Path(__file__).resolve().parent; R=P.parents[1];sys.path.insert(0,str(R/'.claude/skills/voicevox-control/scripts'))
from prepare_readings import load_dictionary,prepare_row
terms={'魚で鳩':'魚でハト','鳩には':'ハトには','別の種':'別のシュ','疑問を抱いた':'疑問をイダイタ','止まれる':'トマレル','その間、周囲':'そのアイダ、周囲','管状動物門':'カンジョードーブツモン','真管綱':'シンカンコー','チクワ目':'チクワモク','チクワ科':'チクワカ','通水腔':'ツースイコー','中口':'ナカグチ','霜重':'シモジュウ','狭間文明':'ハザマブンメー','T社':'ティーシャ','人工物説':'ジンコーブツセツ','魚肉':'ギョニク','対ソバヤ':'タイソバヤ','原料魚':'ゲンリョーギョ','再現性':'サイゲンセー','一食品':'イチショクヒン'}
local={'schema_version':1,'replacements':[{'id':'chikuwa.'+str(i),'surface':s,'reading':v,'source':'dialogue.json','note':'生物学用語・作品用語の読み'} for i,(s,v) in enumerate(terms.items())]}
(P/'readings.json').write_text(json.dumps(local,ensure_ascii=False,indent=2));dictionary=load_dictionary(local_path=P/'readings.json')
def request(route,params=None,body=None):
 url='http://127.0.0.1:50021/'+route+('?' + urllib.parse.urlencode(params) if params else '')
 req=urllib.request.Request(url,data=json.dumps(body).encode() if body is not None else b'' if params else None,headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=180) as r:return r.read()
version=json.loads(request('version'));rows=json.loads((P/'dialogue.json').read_text());out=[]
for i,r in enumerate(rows):
 d=prepare_row(r,dictionary,scopes=['mmu']);sp=2 if r['who']=='metan' else 3
 qp=P/'audio_queries'/f"{r['id']}.json"; cache=P/'audio_queries'/f"{r['id']}_source.json"
 settings={'speech':d['speech'],'speaker':sp,'version':version,'speed':1.13 if sp==2 else 1.15}
 if qp.exists() and cache.exists() and json.loads(cache.read_text())==settings:q=json.loads(qp.read_text())
 else:
  q=json.loads(request('audio_query',{'speaker':sp,'text':d['speech']}));q.update(speedScale=settings['speed'],prePhonemeLength=.09,postPhonemeLength=.12,outputSamplingRate=24000)
  qp.write_text(json.dumps(q,ensure_ascii=False,indent=2));cache.write_text(json.dumps(settings,ensure_ascii=False))
 key=hashlib.sha256(json.dumps({'query':q,'speaker':sp,'version':version},sort_keys=True).encode()).hexdigest()[:12];name=f"voice_{i:03}_{key}.wav";fp=P/name
 if not fp.exists():fp.write_bytes(request('synthesis',{'speaker':sp},q))
 with wave.open(str(fp)) as w:rate=w.getframerate();samples=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
 frames=math.ceil(len(samples)/rate*30);envelope=[round(float(np.sqrt(np.mean(samples[int(j*rate/30):min(len(samples),int((j+1)*rate/30))]**2))),4) for j in range(frames)]
 out.append(dict(d,audio=name,durationInFrames=frames,kana=q['kana'],envelope=envelope,speaker=sp,querySHA=key))
 (P/'voices.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
 print(i+1,len(rows),round(frames/30,2),q['kana'],flush=True)
print('Speech duration',sum(x['durationInFrames'] for x in out)/30)
