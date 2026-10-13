"""Compare every caption page in the final MP4 against the audited Remotion still."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent/'out'
points=json.loads((P/'v10_stills/points.json').read_text());rows=[]
for point in points:
 name=point['name']
 if 'caption' not in name and name!='opening':continue
 a=P/'v10_stills'/f'{name}.png';b=P/'audit_v10'/f'{name}.jpg'
 if not a.exists() or not b.exists():raise FileNotFoundError(name)
 d=float(np.abs(np.asarray(Image.open(a).convert('RGB'),dtype=float)-np.asarray(Image.open(b).convert('RGB'),dtype=float)).mean());rows.append((name,d))
report={'count':len(rows),'maxMAE':max(v for k,v in rows),'meanMAE':sum(v for k,v in rows)/len(rows),'worst':sorted(rows,key=lambda x:-x[1])[:10]}
print(report);assert len(rows)==166;assert report['maxMAE']<3
(P/'v10_frame_comparison.json').write_text(json.dumps(report,indent=2))
