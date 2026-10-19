from pathlib import Path
import json,shutil
P=Path(__file__).resolve().parent;E=P.parent;m=json.loads((P/'src/edit-manifest.json').read_text())
used={d['audio'] for d in m['dialogue']}
for f in E.glob('voice_*.wav'):
 if f.name not in used:shutil.move(f,P/'out'/f.name)
queries={Path(d['queryFile']).name for d in m['dialogue']}
for f in (P/'voice_queries').glob('*.json'):
 if f.name not in queries:shutil.move(f,P/'out'/f.name)
def ts(f):
 ms=round(f/30*1000);h,ms=divmod(ms,3600000);mi,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{mi:02}:{s:02},{ms:03}'
srt=[];index=1
for d in m['dialogue']:
 for c in d['captions']:
  srt += [str(index),f"{ts(d['startFrame']+c['fromFrame'])} --> {ts(d['startFrame']+c['toFrame'])}",c['text'],''];index+=1
(E/'captions_ja.srt').write_text('\n'.join(srt))
s=(E/'script.md').read_text();import re
s=re.sub(r'完成予定：.*',f"完成初稿：1280×720 / 30fps / {m['composition']['durationInFrames']}フレーム（{m['composition']['durationInFrames']/30:.3f}秒）。",s);(E/'script.md').write_text(s)
(E/'voice_generation_record.json').write_text(json.dumps([{k:v for k,v in row.items() if k not in ['envelope','captions']} for row in m['dialogue']],ensure_ascii=False,indent=2))
(E/'youtube_metadata.json').write_text(json.dumps(dict(title='漫画から動画、ゲームまで！ AIで広がる「窓際族物語」とは？',description=(E/'youtube_description.txt').read_text(),publication='not_requested'),ensure_ascii=False,indent=2))
print('Exported',len(used),'adopted WAVs;',index-1,'captions')
