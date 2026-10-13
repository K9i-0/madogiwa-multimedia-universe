"""Stage the canonical, already-adopted commentary exports without editing them."""
from pathlib import Path
import os,hashlib,json
P=Path(__file__).resolve().parent;source=P.parents[1]/'00_TEMPLATES/characters/commentary_duo_v1/exports';target=P/'public/expressions';target.mkdir(exist_ok=True)
rows=[]
for src in sorted(source.glob('*.png')):
 dst=target/src.name
 if not dst.exists():os.link(src,dst)
 sha=hashlib.sha256(src.read_bytes()).hexdigest();assert hashlib.sha256(dst.read_bytes()).hexdigest()==sha
 rows.append({'file':src.name,'sha256':sha})
assert len(rows)==32
(P/'out/expression_asset_checks.json').write_text(json.dumps(rows,indent=2));print('PASS 32 canonical expression exports')
