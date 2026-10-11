"""Apply reviewed thumbnails, backing up old images; resume skips successes."""
import json,hashlib,urllib.request,urllib.error,datetime
from pathlib import Path
root=Path(__file__).resolve().parent
records=root/'results.json';results=json.loads(records.read_text()) if records.exists() else []
token=json.loads((Path.home()/'.config/mmu-youtube/access-token.json').read_text())['access_token']
backup=root/'out'/'before';backup.mkdir(parents=True,exist_ok=True)
for t in json.loads((root/'selections.json').read_text()):
 if any(x['id']==t['id'] and x.get('success') for x in results):continue
 vid=t['id'];before=backup/f'{vid}.jpg'
 if not before.exists():
  for size in ['maxresdefault','hqdefault']:
   try:
    with urllib.request.urlopen(f'https://i.ytimg.com/vi/{vid}/{size}.jpg',timeout=30) as resp:before.write_bytes(resp.read())
    break
   except urllib.error.HTTPError:continue
  if not before.exists():raise RuntimeError('Unable to back up '+vid)
 data=(root/t['thumbnail']).read_bytes()
 req=urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId='+vid+'&uploadType=media',data=data,headers={'Authorization':'Bearer '+token,'Content-Type':'image/jpeg'},method='POST')
 try:
  with urllib.request.urlopen(req,timeout=60) as resp:result=json.load(resp)
  row={'id':vid,'slug':t['slug'],'success':True,'applied_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(data).hexdigest(),'before_sha256':hashlib.sha256(before.read_bytes()).hexdigest(),'youtube_response':result}
 except urllib.error.HTTPError as e:
  err=json.loads(e.read());row={'id':vid,'slug':t['slug'],'success':False,'http_status':e.code,'error':err.get('error',{}).get('message','')}
 results.append(row);records.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print(vid,'OK' if row['success'] else row['error'],flush=True)
 if not row['success']:break
