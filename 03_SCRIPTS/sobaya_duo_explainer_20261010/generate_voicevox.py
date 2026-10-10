"""Generate a local comparison; candidate WAVs stay in remotion/out."""
from pathlib import Path
import json,time,urllib.request,urllib.parse,wave
p=Path(__file__).resolve().parent
out=p/'remotion/out/voicevox';out.mkdir(parents=True,exist_ok=True)
base='http://127.0.0.1:50021/'
def post(endpoint,params,body=b''):
 req=urllib.request.Request(base+endpoint+'?'+urllib.parse.urlencode(params),data=body,headers={'Content-Type':'application/json'},method='POST')
 return urllib.request.urlopen(req,timeout=120).read()
version=json.loads(urllib.request.urlopen(base+'version').read())
records=[]
for r in json.loads((p/'dialogue.json').read_text()):
 if r['who']!='takosan':continue
 text=r.get('reading',r['text']).replace('そば屋','そばや').replace('窓際族物語','まどぎわぞくものがたり').replace('立ち飲み処','たちのみどころ')
 start=time.perf_counter()
 q=json.loads(post('audio_query',{'speaker':89,'text':text}));q['speedScale']=1.0
 data=post('synthesis',{'speaker':89},json.dumps(q).encode())
 elapsed=time.perf_counter()-start
 dest=out/r['audio'];dest.write_bytes(data)
 with wave.open(str(dest)) as w:seconds=w.getnframes()/w.getframerate()
 records.append({'audio':r['audio'],'text':text,'query':q,'generationSeconds':elapsed,'audioSeconds':seconds})
 print(r['audio'],round(elapsed,2),'sec',q['kana'],flush=True)
(p/'voicevox_record.json').write_text(json.dumps({'engineVersion':version,'speaker':'VOICEVOX:Voidoll','style':89,'speedScale':1.0,'generationSeconds':sum(r['generationSeconds'] for r in records),'audioSeconds':sum(r['audioSeconds'] for r in records),'clips':records},ensure_ascii=False,indent=2))
