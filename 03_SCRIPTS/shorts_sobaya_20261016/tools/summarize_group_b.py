from pathlib import Path
import json,hashlib
base=Path(__file__).resolve().parents[1];root=base.parents[1]
rows=json.loads((base/'group-b.json').read_text());technical=[];visual=[]
for row in rows:
 d=(root/row['manifest']).parent;p=d/'audit.json'
 if not p.exists():continue
 a=json.loads(p.read_text());mhash=hashlib.sha256((root/row['manifest']).read_bytes()).hexdigest();passed=a.get('manifestSha256')==mhash and a['fullDecodeExitCode']==0 and a['audioBitstreamIdentical'] and a['sourceFrames']==a['outputFrames'] and a['dimensions']==[720,1280] and a['fps']=='24/1'
 technical.append({'slug':row['slug'],'passed':passed,'sha256':a['outputSha256'],'manifestSha256':mhash,'duration':a['durationSeconds'],'width':a['dimensions'][0],'height':a['dimensions'][1],'fps':24,'frames':a['outputFrames'],'expectedFrames':a['sourceFrames'],'audioBitstreamIdentical':a['audioBitstreamIdentical'],'sourceAudioBitstreamHash':a['sourceAudioBitstreamHash'],'outputAudioBitstreamHash':a['outputAudioBitstreamHash'],'fullDecodeExitCode':a['fullDecodeExitCode'],'audit':str(p.relative_to(root))})
 visualpassed=a['visualReview']=='passed' and passed
 visual.append({'slug':row['slug'],'passed':visualpassed,'sha256':a['outputSha256'],'manifestSha256':mhash,'contactSheets':a['contactSheets'],'sampleFrames':a['sampleFrames'],'captionCount':a['captionCount'],'notes':a.get('visualReviewNotes','Pending visual review'),'method':a['reviewMethod']})
 if visualpassed:row['status']='ready';row['audit']=str(p.relative_to(root))
 else:row['status']='editing'
(base/'technical-audit-group-b.json').write_text(json.dumps({'videos':technical},ensure_ascii=False,indent=2)+'\n');(base/'visual-audit-group-b.json').write_text(json.dumps({'videos':visual},ensure_ascii=False,indent=2)+'\n');(base/'group-b.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('Group B technical:',sum(v['passed'] for v in technical),'/',len(rows),'visual:',sum(v['passed'] for v in visual),'/',len(rows))
