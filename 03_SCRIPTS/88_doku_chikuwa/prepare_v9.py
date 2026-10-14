from pathlib import Path
import json,shutil
P=Path(__file__).resolve().parent;pub=P/'remotion/public'
m=json.loads((P/'remotion/src/edit-manifest-v7.json').read_text())
replace={0:'crime_scene_outline_v9.png',107:'oden_marker1_v9.png',228:'blood_overhead_v9.png',730:'fukugyun_oden_rear_v9.png',1409:'oden_marker1_v9.png'}
for s in m['shots']:
 if s['from'] in replace:
  s['kind']='image';s['file']=replace[s['from']];s['sourceStart']=0
for name in set(replace.values()):shutil.copy2(P/name,pub/name)
(P/'remotion/src/edit-manifest-v9.json').write_text(json.dumps(m,indent=2)+'\n')
