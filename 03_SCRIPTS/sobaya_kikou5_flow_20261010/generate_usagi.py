"""Generate only Takosan; preserve adopted historical speech and Yametaro."""
from pathlib import Path
import json, hashlib, urllib.request, urllib.parse
p=Path(__file__).resolve().parent
base='http://127.0.0.1:50021/'
def post(endpoint,params,body=b''):
 req=urllib.request.Request(base+endpoint+'?'+urllib.parse.urlencode(params),data=body,headers={'Content-Type':'application/json'})
 return urllib.request.urlopen(req,timeout=120).read()
version=json.loads(urllib.request.urlopen(base+'version').read())
record={'engineVersion':version,'speaker':61,'style':'中国うさぎ・ノーマル','speedScale':1.1,'pitchScale':0,'lines':[]}
for r in json.loads((p/'dialogue.json').read_text()):
 if r['who']!='takosan':continue
 q=json.loads(post('audio_query',{'speaker':61,'text':r['reading']}))
 q.update(speedScale=1.1,pitchScale=0,prePhonemeLength=.15,postPhonemeLength=.55,outputSamplingRate=48000,outputStereo=False)
 key=hashlib.sha256(json.dumps([version,61,q],sort_keys=True).encode()).hexdigest()
 out=p/r['audio'];meta=out.with_suffix('.key')
 if not out.exists() or not meta.exists() or meta.read_text()!=key:
  out.write_bytes(post('synthesis',{'speaker':61},json.dumps(q).encode()));meta.write_text(key)
 record['lines'].append({'audio':r['audio'],'text':r['text'],'reading':r['reading'],'query':q,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
 print(r['audio'],q['kana'],flush=True)
(p/'voice_usagi_record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
