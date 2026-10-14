from pathlib import Path
import json,re,math
P=Path(__file__).resolve().parent
source=P/'src/edit-manifest.json'
if source.exists():m=json.loads(source.read_text())
else:
 rows=json.loads((P/'out/voice_progress.json').read_text());cursor=60
 for d in rows:d['startFrame']=cursor;cursor+=d['durationInFrames']+d.get('pause',12)
 m={'composition':{'width':1280,'height':720,'fps':30,'durationInFrames':cursor+75},'dialogue':rows,'mainStartFrame':60,'endingStartFrame':cursor,'voiceModel':'canonical','clips':[]}
def wrap(s):
 if len(s)<=25:return s
 options=[i for i in range(max(1,len(s)-25),min(26,len(s))) if s[i-1] in '、。？！ ']
 i=min(options,key=lambda i:abs(i-len(s)/2)) if options else min(25,math.ceil(len(s)/2))

 for term in ['Claude Code','Flutter Scene','MiniMax H3','Three.js']:
  j=s.find(term)
  if j>=0 and j<i<j+len(term):i=j if j>0 else j+len(term)
 return s[:i].strip()+'\n'+s[i:].strip()
for d in m['dialogue']:
 text=d['text'];parts=re.findall(r'[^。？！]+[。？！]?|[。？！]',text);pages=[]
 for part in parts:
  if pages and len(pages[-1])+len(part)<=45:pages[-1]+=part
  else:
   while len(part)>48:
    cuts=[i+1 for i,c in enumerate(part[:46]) if c=='、'];cut=cuts[-1] if cuts else 24
    pages.append(part[:cut]);part=part[cut:]
   if part:pages.append(part)
 total=sum(len(x) for x in pages);cursor=0;segments=[]
 for i,part in enumerate(pages):
  end=d['durationInFrames'] if i==len(pages)-1 else round(d['durationInFrames']*sum(len(x) for x in pages[:i+1])/total)
  segments.append({'startFrame':cursor,'endFrame':end,'text':wrap(part)});cursor=end
 d['captionSegments']=segments
source.write_text(json.dumps(m,ensure_ascii=False,indent=2))
print('seconds',m['composition']['durationInFrames']/30)
