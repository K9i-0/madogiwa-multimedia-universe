from pathlib import Path
import re,json,urllib.request,urllib.parse,hashlib,wave,concurrent.futures,time
P=Path(__file__).resolve().parent
body=(P.parent/'script.md').read_text().split('## 本文\n',1)[1]
rows=[];chapter=0
for line in body.splitlines():
 line=line.strip()
 if line.startswith('### '): chapter=int(line[4:6]);continue
 if not line or line.startswith('［'):continue
 text=line
 speech=text.replace('Y村','ワイむら').replace('Mさん','エムさん').replace('Yさん','ワイさん').replace('F先生','エフ先生').replace('中口','なかぐち').replace('祠','ほこら').replace('空席','くうせき').replace('空き缶','あきかん')
 rows.append({'id':f'n{len(rows):04d}','chapter':chapter,'text':text,'speech':speech})
(P/'dialogue.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
BASE='http://127.0.0.1:50021'
def post(endpoint,params,data=None):
 req=urllib.request.Request(BASE+'/'+endpoint+'?'+urllib.parse.urlencode(params),data=json.dumps(data).encode() if data else b'',headers={'Content-Type':'application/json'})
 return urllib.request.urlopen(req,timeout=180).read()
version=json.load(urllib.request.urlopen(BASE+'/version'))
settings={'speaker':13,'speedScale':1.0,'pitchScale':0.0,'intonationScale':0.85,'volumeScale':1.0,'prePhonemeLength':0.15,'postPhonemeLength':0.35,'outputSamplingRate':24000,'outputStereo':False}
def gen(r):
 dest=P/'public/voice_aoyama'/f"{r['id']}.wav"; dest.parent.mkdir(parents=True,exist_ok=True); meta=dest.with_suffix('.json')
 sig=hashlib.sha256(json.dumps([r['speech'],settings,version],ensure_ascii=False,sort_keys=True).encode()).hexdigest()
 if not(dest.exists() and meta.exists() and json.loads(meta.read_text()).get('key')==sig):
  q=json.loads(post('audio_query',{'speaker':settings['speaker'],'text':r['speech']}));q.update({k:v for k,v in settings.items() if k!='speaker'})
  dest.write_bytes(post('synthesis',{'speaker':settings['speaker']},q));meta.write_text(json.dumps({'key':sig,'engine':version,'settings':settings,'kana':q['kana'],'speech':r['speech']},ensure_ascii=False,indent=2))
 with wave.open(str(dest)) as w: seconds=w.getnframes()/w.getframerate()
 return {**r,'file':f"voice_aoyama/{r['id']}.wav",'seconds':seconds}
print('Generating',len(rows),'segments',flush=True)
res={}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
 for i,r in enumerate(ex.map(gen,rows)):
  res[r['id']]=r
  if i%20==0: print(i+1,'/',len(rows),flush=True)
(P/'voice-manifest.json').write_text(json.dumps({'engine':version,'speaker':'VOICEVOX:青山龍星','settings':settings,'rows':[res[x['id']] for x in rows]},ensure_ascii=False,indent=2))
print('DONE speech seconds',sum(x['seconds'] for x in res.values()),flush=True)
