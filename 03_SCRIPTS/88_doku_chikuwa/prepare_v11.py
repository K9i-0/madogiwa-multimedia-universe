from pathlib import Path
import json,shutil
P=Path(__file__).resolve().parent;pub=P/'remotion/public'
m=json.loads((P/'remotion/src/edit-manifest-v10.json').read_text())
shots=m['shots'][:4]
def video(file,start,duration,source):return dict(kind='video',file=file,from_=start,duration=duration,sourceStart=source)
def still(file,start,duration):return dict(kind='image',file=file,from_=start,duration=duration,sourceStart=0)
shots += [
 video('wan3_interior_v11_480p.mp4',597,133,132),
 video('wan3_rear_v11_480p.mp4',730,170,0),
 video('wan3_interior_v11_480p.mp4',900,73,230),
 video('wan3_entrance_inserts_v4_480p.mp4',973,20,340),
 video('wan3_interior_v11_480p.mp4',993,207,374),
 video('wan3_interior_v11_480p.mp4',1200,96,581),
 video('wan3_collapse_v11_480p.mp4',1296,18,60),
 still('empty_table_hold_v11.png',1314,110),
]
for s in shots:
 if 'from_' in s:s['from']=s.pop('from_')
shots.append(m['shots'][-1]);m['shots']=shots
for a,b in zip(shots,shots[1:]):assert a['from']+a['duration']==b['from']
assert shots[-1]['from']+shots[-1]['duration']==m['durationInFrames']
for n in ['wan3_interior_v11_480p.mp4','wan3_rear_v11_480p.mp4','wan3_collapse_v11_480p.mp4','empty_table_hold_v11.png']:shutil.copy2(P/n,pub/n)
(P/'remotion/src/edit-manifest-v11.json').write_text(json.dumps(m,indent=2)+'\n')
print('All indoor acting shots replaced; intro and entrance retained; audio unchanged; frames:',m['durationInFrames'])
