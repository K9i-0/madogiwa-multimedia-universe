"""Rerender two reviewed scene ranges; retain exact narration and frame count."""
from pathlib import Path
import json,subprocess,hashlib
P=Path(__file__).resolve().parent
changes={'u031':'fuku_sheet','u032':'fuku_sheet','u033':'sheet_identity','u034':'sheet_identity','u103':'first_step'}
for name,key in [('dialogue.json',None),('src/edit-manifest.json','dialogue'),('../voice_record_v5.json','lines')]:
 p=P/name;obj=json.loads(p.read_text());rows=obj[key] if key else obj
 for d in rows:
  if d['id'] in changes:d['view']=changes[d['id']]
 p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
m=json.loads((P/'src/edit-manifest.json').read_text());d={x['id']:x for x in m['dialogue']};n=m['composition']['durationInFrames']
ranges=[(d['u031']['startFrame'],d['u035']['startFrame']),(d['u103']['startFrame'],d['u106']['startFrame'])]
patches=[]
for i,(start,end) in enumerate(ranges):
 output=P/'out'/f'v5_visual_patch_{i}.mp4';patches.append(output)
 subprocess.run(['npx','remotion','render','src/index.ts','Explainer',str(output),'--muted','--concurrency=4','--crf=16',f'--frames={start}-{end-1}','--log=error'],cwd=P,check=True)
 print('PATCH',start,end,flush=True)
base=P/'out/review_v5_01.mp4';out=P/'out/review_v5_02.mp4'
(a,b),(c,e)=ranges
filters=f'[0:v]trim=start_frame=0:end_frame={a},setpts=PTS-STARTPTS[v0];[1:v]setpts=PTS-STARTPTS[v1];[0:v]trim=start_frame={b}:end_frame={c},setpts=PTS-STARTPTS[v2];[2:v]setpts=PTS-STARTPTS[v3];[0:v]trim=start_frame={e}:end_frame={n},setpts=PTS-STARTPTS[v4];[v0][v1][v2][v3][v4]concat=n=5:v=1:a=0[v]'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(base),'-i',str(patches[0]),'-i',str(patches[1]),'-filter_complex',filters,'-map','[v]','-map','0:a:0','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p','-r','30','-c:a','copy','-movflags','+faststart',str(out)],check=True)
(P.parent/'visual_revision_v5.json').write_text(json.dumps({'baseSha256':hashlib.sha256(base.read_bytes()).hexdigest(),'changes':changes,'rangesExclusiveEnd':ranges,'totalFrames':n,'audio':'AAC stream copy from reviewed full mix','output':str(out.relative_to(P))},ensure_ascii=False,indent=2)+'\n')
print('PATCHED',out,flush=True)
