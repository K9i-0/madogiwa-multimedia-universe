"""Rebuild public assets from the recorded sources, without copying outputs."""
from pathlib import Path
import json,os,shutil,hashlib
P=Path(__file__).resolve().parent;R=P.parents[2]
(P/'public').mkdir(exist_ok=True)
records=json.loads((P.parent/'asset_sources.json').read_text())
for row in records:
 src=R/row['source'];dst=P/'public'/row['file'];dst.parent.mkdir(parents=True,exist_ok=True)
 if not src.is_file():raise FileNotFoundError(f'Required original asset is missing: {src}')
 if not dst.exists():
  try:os.link(src,dst)
  except OSError:shutil.copy2(src,dst)
 row['sha256']=hashlib.sha256(src.read_bytes()).hexdigest()
(P.parent/'asset_sources.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
