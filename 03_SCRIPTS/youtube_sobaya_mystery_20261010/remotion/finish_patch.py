"""Splice the final-QA ruins correction; normal full render already includes it."""
from pathlib import Path
import json,subprocess
P=Path(__file__).resolve().parent;m=json.loads((P/'src/edit-manifest.json').read_text())
start=next(d['startFrame'] for d in m['dialogue'] if d['view']=='ruins');end=next(d['startFrame'] for d in m['dialogue'] if d['view']=='sleepers')
f=P.parent/'final_remotion_sobaya_mystery_v2.mp4';before=P/'out/v2_before_ruins_patch.mp4'
if not before.exists():f.rename(before)
filters=f'[0:v]split=2[a][b];[a]trim=end_frame={start},setpts=PTS-STARTPTS[first];[1:v]setpts=PTS-STARTPTS[patch];[b]trim=start_frame={end},setpts=PTS-STARTPTS[last];[first][patch][last]concat=n=3:v=1:a=0[v]'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(before),'-i',str(P/'out/ruins_patch.mp4'),'-filter_complex',filters,'-map','[v]','-map','0:a:0','-c:v','libx264','-preset','veryfast','-crf','18','-r','30','-c:a','copy','-movflags','+faststart',str(f)],check=True)
(P.parent/'final_patch_record.json').write_text(json.dumps({'startFrame':start,'endFrameExclusive':end,'reason':'The moving ruins source crossed a shot containing an unrelated character; fixed archival tank frame replaces this interval.','audio':'Original AAC stream copied unchanged','reproduction':'Full render.py includes the corrected Panel.tsx and does not require this splice.','patchRenderCommand':f'npx remotion render src/index.ts Explainer out/ruins_patch.mp4 --frames={start}-{end-1} --muted --concurrency=4 --crf=18'},indent=2)+'\n')
