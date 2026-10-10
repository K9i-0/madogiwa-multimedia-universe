from pathlib import Path
import os,json,subprocess,hashlib,time,urllib.request,urllib.parse,sys
root=Path(__file__).resolve().parents[2];ep=Path(__file__).resolve().parent
logs=root/'.local/kikou5/voice';logs.mkdir(parents=True,exist_ok=True)
rows=json.loads((ep/'dialogue.json').read_text());selected=set(sys.argv[1:])
def post(endpoint,params,body=b''):
 req=urllib.request.Request('http://127.0.0.1:50021/'+endpoint+'?'+urllib.parse.urlencode(params),data=body,headers={'Content-Type':'application/json'},method='POST')
 return urllib.request.urlopen(req,timeout=120).read()
for r in rows:
 if selected and r['who'] not in selected:continue
 out=ep/r['audio'];key=hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest();meta=out.with_suffix('.key')
 if out.exists() and meta.exists() and meta.read_text()==key:continue
 start=time.perf_counter()
 if r['who']=='takosan':
  q=json.loads(post('audio_query',{'speaker':89,'text':r['reading']}));q['speedScale']=1.0
  out.write_bytes(post('synthesis',{'speaker':89},json.dumps(q).encode()))
  (logs/(out.stem+'.query.json')).write_text(json.dumps(q,ensure_ascii=False,indent=2))
 else:
  env=dict(os.environ,IRODORI_UNCUT='1',IRODORI_CFG_SCALE_TEXT='5',IRODORI_DURATION_SCALE=str(r['durationScale']))
  with (logs/(out.stem+'.log')).open('w') as log:subprocess.run([str(root/'tools/irodori_speak.sh'),r['reading'],str(out),str(root/r['reference']),str(r['seed'])],cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 meta.write_text(key)
 print(out.name,round(time.perf_counter()-start,2),'seconds',flush=True)
