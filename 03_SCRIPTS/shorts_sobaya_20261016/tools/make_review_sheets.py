#!/usr/bin/env python3
"""Extract final-video frames at every caption midpoint plus picture/ending samples."""
import json,subprocess,sys,hashlib
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[1]
for row in json.loads((B/(sys.argv[1] if len(sys.argv)>1 else 'group-root.json')).read_text()):
 e=B/'episodes'/row['slug'];out=R/row['output'];p=R/row['manifest']
 if not out.exists() or not p.exists():continue
 m=json.loads(p.read_text());n=m['durationInFrames'];frames=sorted({0,n//4,n//2,n*3//4,n-1,*[(c['startFrame']+c['endFrame'])//2 for c in m['captions']]});sha=hashlib.file_digest(out.open('rb'),'sha256').hexdigest();record=e/'review-sheets.json'
 if record.exists() and json.loads(record.read_text())['sha256']==sha:continue
 sheets=[]
 for i in range(0,len(frames),9):
  fs=frames[i:i+9];dest=e/f'review-sheet-{i//9+1}.jpg';select='+'.join(f'eq(n,{x})' for x in fs)
  subprocess.run(['ffmpeg','-v','error','-threads','1','-i',str(out),'-vf',f"select='{select}',scale=360:640,tile=3x3",'-frames:v','1','-y',str(dest)],check=True)
  sheets.append({'path':str(dest.relative_to(R)),'frames':fs})
 record.write_text(json.dumps({'slug':row['slug'],'sha256':sha,'sheets':sheets},indent=2));print(row['slug'],len(sheets),flush=True)
