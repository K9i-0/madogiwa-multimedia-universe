"""Extract revised measurement, ancient civilization, and space sections."""
from pathlib import Path
import json,subprocess
p=Path(__file__).resolve().parent
m=json.loads((p/'src/edit-manifest.json').read_text())
views=['height','cryptids','ritual_dark','secrecy_compare']
filters=[];inputs=[];cuts=[]
for i,view in enumerate(views):
 rows=[d for d in m['dialogue'] if d['view']==view]
 start=rows[0]['startFrame'];end=rows[-1]['startFrame']+rows[-1]['durationInFrames']+rows[-1]['pause']
 filters.extend([f'[0:v]trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS[v{i}]',f'[0:a]atrim=start={start/30}:end={end/30},asetpts=PTS-STARTPTS[a{i}]'])
 inputs.append(f'[v{i}][a{i}]');cuts.append({'view':view,'startFrame':start,'endFrameExclusive':end})
filters.append(''.join(inputs)+f'concat=n={len(views)}:v=1:a=1[v][a]')
subprocess.run(['ffmpeg','-v','error','-y','-i',str(p.parent/'final_remotion_sobaya_mystery_v9.mp4'),'-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-c:v','libx264','-crf','19','-preset','fast','-c:a','aac','-b:a','192k','-movflags','+faststart',str(p.parent/'preview_changes_v9.mp4')],check=True)
record={'source':'final_remotion_sobaya_mystery_v9.mp4','output':'preview_changes_v9.mp4','cuts':cuts,'durationSeconds':sum(c['endFrameExclusive']-c['startFrame'] for c in cuts)/30}
(p.parent/'preview_changes_v9.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(record)
