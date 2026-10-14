"""Link original assets into public; never modify the shared source models."""
from pathlib import Path
import json,os,hashlib
P=Path(__file__).resolve().parent;R=P.parents[2]
records=json.loads((P.parent/'asset_sources.json').read_text())
if (P.parent/'asset_sources_v2.json').exists():records+=json.loads((P.parent/'asset_sources_v2.json').read_text())
if (P.parent/'web_refs_v3.json').exists():records+=json.loads((P.parent/'web_refs_v3.json').read_text())['assets']
if (P.parent/'asset_sources_v4.json').exists():records+=json.loads((P.parent/'asset_sources_v4.json').read_text())
for a in records:
 src=R/a['source'];dst=P/'public'/a['target']
 if not src.exists():raise FileNotFoundError(f"Restore the recorded local asset: {src}")
 if a.get('sha256') and hashlib.sha256(src.read_bytes()).hexdigest()!=a['sha256']:raise ValueError(f"Asset changed: {src}")
 dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists():dst.symlink_to(os.path.relpath(src,dst.parent))
for src in list(P.parent.glob('clip*_line1_*.wav'))+list(P.parent.glob('clip_v2_*.wav'))+list(P.parent.glob('clip_v3_*.wav'))+list(P.parent.glob('clip_v4_*.wav'))+list(P.parent.glob('clip_v5_*.wav'))+list(P.parent.glob('clip_v6_*.wav')):
 dst=P/'public'/src.name
 if not dst.exists():dst.symlink_to(os.path.relpath(src,dst.parent))
print('All source assets linked and verified.')
