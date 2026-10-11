"""Compare public YouTube thumbnails with adopted frames after upload."""
import json,urllib.request,time,concurrent.futures,io,datetime
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
root=Path(__file__).resolve().parent
out=root/'out'/'after';out.mkdir(parents=True,exist_ok=True)
def check(t):
 url=f'https://i.ytimg.com/vi/{t["id"]}/maxresdefault.jpg?mmu_thumbnail_refresh={int(time.time())}'
 with urllib.request.urlopen(url,timeout=30) as resp:data=resp.read()
 (out/f'{t["id"]}.jpg').write_bytes(data)
 a=Image.open(root/t['thumbnail']).convert('RGB').resize((320,180));b=Image.open(io.BytesIO(data)).convert('RGB').resize((320,180))
 mae=sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3
 return {'id':t['id'],'slug':t['slug'],'public_image_matches':mae<8,'mean_absolute_rgb_error':round(mae,4),'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:rows=list(ex.map(check,json.loads((root/'selections.json').read_text())))
(root/'verification.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('Public image matches:',sum(t['public_image_matches'] for t in rows),'/',len(rows))
for t in rows:
 if not t['public_image_matches']:print(t['id'],t['mean_absolute_rgb_error'])
