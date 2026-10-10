"""Restore licensed local BGM from official distribution pages; do not commit audio."""
from pathlib import Path
import hashlib,json,re,requests
P=Path(__file__).resolve().parent
for item in json.loads((P.parent/'bgm_sources.json').read_text()):
 target=P/'public'/item['file']
 if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256']:continue
 session=requests.Session()
 if 'page' in item:
  page=item['page'];r=session.get(page,timeout=60);r.raise_for_status()
  token=re.search('name="csrfmiddlewaretoken" value="([^"]+)',r.text)[1]
  r=session.post(page,data={'csrfmiddlewaretoken':token,'track':'1'},headers={'Referer':page},timeout=60)
 else:r=session.get(item['source']['download'],timeout=60)
 r.raise_for_status();assert hashlib.sha256(r.content).hexdigest()==item['sha256'], 'Source changed; inspect before adopting'
 target.write_bytes(r.content)
