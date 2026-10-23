"""Align approved caption text to ASR phrase timings, retaining authored spelling."""
import json,re,difflib
from pathlib import Path
EP=Path(__file__).resolve().parent;ROOT=EP.parents[1]
path=EP/'remotion/src/edit-manifest.json';m=json.loads(path.read_text())
rows={r['id']:r for r in json.loads((ROOT/'.local/mde-crosstech/asr.json').read_text())}
def norm(t):return re.sub(r'[\s、。，！？「」『』・,.!?ー—―]','',t).lower()
reports=[]
for scene in m['scenes']:
 if scene['id'] not in rows:continue
 row=rows[scene['id']]; chunks=row['result'].get('chunks',[])
 heard=''; times=[]
 for chunk in chunks:
  txt=norm(chunk['text']);a,b=chunk['timestamp']
  a=a or 0;b=b if b is not None else scene['audioFrames']/30
  heard+=txt
  times += [(a+(b-a)*i/max(1,len(txt)),a+(b-a)*(i+1)/max(1,len(txt))) for i in range(len(txt))]
 expected=norm(scene['text']);sm=difflib.SequenceMatcher(None,expected,heard,autojunk=False)
 mapping={}
 for a,b,size in sm.get_matching_blocks():
  for k in range(size):mapping[a+k]=times[b+k]
 def stamp(pos,end=False):
  if not mapping:return scene['audioFrames']/30*pos/max(1,len(expected))
  target=min(mapping,key=lambda x:abs(x-pos))
  return mapping[target][1 if end else 0]
 pos=0;caption_rows=[c for c in m['captions'] if c['lineId']==scene['id']]
 for c in caption_rows:
  n=len(norm(c['text']));a=stamp(pos);b=stamp(pos+n-1,True);pos+=n
  c['start']=scene['start']+max(0,round(a*30)-2)
  c['end']=scene['start']+min(scene['audioFrames'],max(round(b*30)+3,round(a*30)+12))
 for c,next_c in zip(caption_rows,caption_rows[1:]):
  if c['end']>next_c['start']:c['end']=next_c['start']
 reports.append(dict(id=scene['id'],ratio=round(sm.ratio(),3),expected=scene['text'],asr=row['result']['text']))
m['captionTimingMethod']='ASR phrase timestamps + character alignment; authored text retained; listening not performed'
path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
def srt_time(frame):
 ms=round(frame/30*1000);h,ms=divmod(ms,3600000);mi,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
 return f'{h:02}:{mi:02}:{s:02},{ms:03}'
(EP/'subtitles_ja.srt').write_text('\n\n'.join(f"{i}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n{c['text']}" for i,c in enumerate(m['captions'],1))+'\n')
(EP/'asr_text_audit.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
print('Aligned',len(reports),'lines')
for r in reports:
 if r['ratio']<.85:print(r['id'],r['ratio'],r['asr'])
