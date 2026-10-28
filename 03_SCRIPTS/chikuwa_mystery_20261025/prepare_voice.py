from pathlib import Path
import os,json,sys,hashlib,wave,math,urllib.request,urllib.parse,numpy as np
P=Path(__file__).resolve().parent; R=P.parents[1];sys.path.insert(0,str(R/'.claude/skills/voicevox-control/scripts'))
from prepare_readings import load_dictionary,prepare_row
terms={'使う分':'ツカウブン','猥褻物陳列罪':'ワイセツブツチンレツザイ','酒癖':'サケグセ','魚で鳩':'魚でハト','鳩には':'ハトには','別の種':'別のシュ','疑問を抱いた':'疑問をイダイタ','止まれる':'トマレル','その間、周囲':'そのアイダ、周囲','管状動物門':'カンジョードーブツモン','真管綱':'シンカンコー','チクワ目':'チクワモク','チクワ科':'チクワカ','通水腔':'ツースイコー','中口':'ナカグチ','霜重':'シモジュウ','狭間文明':'ハザマブンメー','T社':'ティーシャ','人工物説':'ジンコーブツセツ','魚肉':'ギョニク','対ソバヤ':'タイソバヤ','原料魚':'ゲンリョーギョ','再現性':'サイゲンセー','一食品':'イチショクヒン'}
local={'schema_version':1,'replacements':[{'id':'chikuwa.'+str(i),'surface':s,'reading':v,'source':'dialogue.json','note':'生物学用語・作品用語の読み'} for i,(s,v) in enumerate(terms.items())]}
(P/'readings.json').write_text(json.dumps(local,ensure_ascii=False,indent=2));dictionary=load_dictionary(local_path=P/'readings.json')
def request(route,params=None,body=None):
 url='http://127.0.0.1:50021/'+route+('?' + urllib.parse.urlencode(params) if params else '')
 req=urllib.request.Request(url,data=json.dumps(body).encode() if body is not None else b'' if params else None,headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=180) as r:return r.read()
version=json.loads(request('version'));rows=json.loads((P/'dialogue.json').read_text());out=[]
# Snapshot query cache before sequential IDs move after an insertion.
query_cache={}
for source in (P/'audio_queries').glob('*_source.json'):
 query=source.with_name(source.name.replace('_source.json','.json'))
 if query.exists():query_cache[json.dumps(json.loads(source.read_text()),sort_keys=True)]=json.loads(query.read_text())
for i,r in enumerate(rows):
 reading_row=dict(r)
 if '工場の規模で行って' in r['text']:reading_row['speech_override']=r['text'].replace('工場の規模で行って','工場の規模でおこなって')
 d=prepare_row(reading_row,dictionary,scopes=['mmu']);sp=2 if r['who']=='metan' else 3
 qp=P/'audio_queries'/f"{r['id']}.json"; cache=P/'audio_queries'/f"{r['id']}_source.json"
 settings={'speech':d['speech'],'speaker':sp,'version':version,'speed':1.13 if sp==2 else 1.15}
 # Selected performances; unmodified lines retain the existing voice cache.
 performance={}
 text=r['text']
 if text.startswith('研究員の報告では、味'):performance={'speedScale':1.08,'intonationScale':1.12}
 elif text in ['一番大事なところが残っているのだ。','通報の電話線なのだ。','お帰りください、なのだ。']:performance={'speedScale':1.10,'intonationScale':.78,'postPhonemeLength':.18}
 elif r['view']=='additional_charge' and sp==2:performance={'speedScale':1.08,'intonationScale':.82}
 elif text.startswith('市販品から毒が'):performance={'speedScale':1.08,'intonationScale':1.12}
 elif r['view'] in ['leap','education'] and sp==2:performance={'speedScale':1.16,'intonationScale':1.18}
 elif text.startswith('……昨日'):performance={'speedScale':.94,'intonationScale':.72,'volumeScale':.86,'prePhonemeLength':.20}
 elif text.startswith(('その一本が','あなたが昨日')):performance={'speedScale':1.04,'intonationScale':.83,'volumeScale':.92}
 if text=='ええ。何も入っていなかったわ。':performance={'speedScale':1.08,'intonationScale':.82}
 if text.startswith('ええ。比較が不公平'):performance={'speedScale':1.08,'intonationScale':.9}
 if r['view']=='missing':performance={'speedScale':1.08,'intonationScale':1.05}
 if r['view']=='isobe' and sp==3:performance={'speedScale':1.1,'intonationScale':.82}
 if r['view']=='isobe' and sp==2:performance={'speedScale':1.04,'intonationScale':.78,'prePhonemeLength':.25}
 if performance:settings['performance']=performance
 cached=query_cache.get(json.dumps(settings,sort_keys=True))
 if cached is not None:q=cached
 else:
  q=json.loads(request('audio_query',{'speaker':sp,'text':d['speech']}));q.update(speedScale=settings['speed'],prePhonemeLength=.09,postPhonemeLength=.12,outputSamplingRate=24000)
 if performance:q.update(performance)
 if text.startswith('研究員の報告では、味'):
  for phrase in q['accent_phrases']:
   if ''.join(m['text'] for m in phrase['moras'])=='ソオイテンワ' and phrase.get('pause_mora'):phrase['pause_mora']['vowel_length']=.58
 if text.startswith('……昨日'):
  for phrase in q['accent_phrases']:
   if ''.join(m['text'] for m in phrase['moras'])=='ノダ' and phrase.get('pause_mora'):phrase['pause_mora']['vowel_length']=.58
 qp.write_text(json.dumps(q,ensure_ascii=False,indent=2));cache.write_text(json.dumps(settings,ensure_ascii=False))
 key=hashlib.sha256(json.dumps({'query':q,'speaker':sp,'version':version},sort_keys=True).encode()).hexdigest()[:12];name=f"voice_{i:03}_{key}.wav";fp=P/name
 if not fp.exists():
  reusable=next(P.glob(f'voice_*_{key}.wav'),None)
  if reusable:fp=reusable;name=fp.name
  else:fp.write_bytes(request('synthesis',{'speaker':sp},q))
 with wave.open(str(fp)) as w:rate=w.getframerate();samples=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
 frames=math.ceil(len(samples)/rate*30);envelope=[round(float(np.sqrt(np.mean(samples[int(j*rate/30):min(len(samples),int((j+1)*rate/30))]**2))),4) for j in range(frames)]
 out.append(dict(d,audio=name,durationInFrames=frames,kana=q['kana'],envelope=envelope,speaker=sp,querySHA=key))
 (P/'voices.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
 print(i+1,len(rows),round(frames/30,2),q['kana'],flush=True)
print('Speech duration',sum(x['durationInFrames'] for x in out)/30)
