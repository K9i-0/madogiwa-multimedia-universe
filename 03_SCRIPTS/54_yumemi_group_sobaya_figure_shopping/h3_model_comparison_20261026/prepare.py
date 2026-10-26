"""Freeze original inputs and change only checkpoint/output prefix for comparison."""
from pathlib import Path
import hashlib,json,shutil,sys,zipfile
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
job=Path(sys.argv[1]).resolve();job.mkdir(parents=True,exist_ok=False)
source=ROOT/'.local/h3-shopping-768-20261026/job/inputs.zip'
models=[
 dict(id='singularity_v2',repo='WarmBloodAban/Minimax-h3_Singularity',revision='1259cf16cd0b655ba691a32fb46a409142762972',filename='Minimax-h3_Singularity_ref2va_v2_pruned_int8.safetensors',sha256='d7637c2c35cd30facd9e93778c491f6d82f91c4a441aecbdb4c384a62a5f3d9f'),
 dict(id='hybrid_b20',repo='smhfacct/Minimax-H3-fl2va-ref2va-hybrid-models',revision='a36feb17fbd1f20ff4bdd509ccd07e2b7b585a38',filename='minimax_h3_hybrid_fl2va_ref2va_b20-49-int8.safetensors',sha256='8320246da06e5aae94988dc1ab336b19ebf2491b4393a330fb33bafca39f9d9a')]
(P/'models.json').write_text(json.dumps(models,indent=2)+'\n')
with zipfile.ZipFile(source) as src,zipfile.ZipFile(job/'inputs.zip','w',zipfile.ZIP_DEFLATED) as dst:
 for n in src.namelist():
  if n!='colab_remote.py':dst.writestr(n,src.read(n))
 dst.write(P/'remote.py','colab_remote.py');dst.write(P/'models.json','models.json')
 for ch in ['ch01','ch02']:
  g=json.loads(src.read(ch+'.json'));assert g['136']['inputs']['length']==362 and g['124']['inputs']['steps']==20
  (P/(ch+'_baseline.json')).write_text(json.dumps(g,indent=2)+'\n')
(job/'job.json').write_text(json.dumps(dict(status='prepared',bundle_sha256=hashlib.sha256((job/'inputs.zip').read_bytes()).hexdigest()),indent=2))
print(job)
