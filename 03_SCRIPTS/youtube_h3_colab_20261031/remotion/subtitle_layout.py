"""Two-line Japanese captions, preserving ASCII words, katakana and numbers."""
import re,unicodedata
OPEN='「『（【';NO_START='、。？！）」』】';END='。！？'
LIMIT=24
def width(s):return sum(1 if unicodedata.east_asian_width(c) in 'WF' else .55 for c in s)
def valid_cuts(s):
 protected=[(m.start(),m.end()) for m in re.finditer(r'[A-Za-z0-9]+(?:[ .×,/][A-Za-z0-9]+)*|[ァ-ヴー]+|[0-9]+(?:\.[0-9]+)?(?:円|本|秒|分|倍|月|日|万円|クレジット)',s)]
 return [i for i in range(1,len(s)) if s[i] not in NO_START and s[i-1] not in OPEN and not any(a<i<b for a,b in protected)]
def quality(s,i):
 before=s[:i]
 if before[-1] in '、。？！':return 0
 if before.endswith(('は','が','を','に','で','と','も','へ','から','ので','なら','など','より','だけ','する','した')):return 3
 return 10
def captions(text,frames):
 sentences=[];part='';depth=0
 for c in text:
  part+=c
  if c in OPEN:depth+=1
  elif c in '」』）】':depth=max(0,depth-1)
  if c in END and not part.strip(END) and sentences:sentences[-1]+=part;part=''
  elif c in END and depth==0:sentences.append(part);part=''
 if part:sentences.append(part)
 pages=[]
 for s in sentences:
  while width(s)>LIMIT*2:
   choices=[i for i in valid_cuts(s) if 18<=width(s[:i])<=LIMIT*2-2]
   cut=min(choices,key=lambda i:quality(s,i)*3+abs(width(s[:i])-40)) if choices else len(s)//2
   pages.append(s[:cut]);s=s[cut:]
  s=s.strip()
  if s:pages.append(s)
 result=[];offset=0;total=sum(width(p) for p in pages)
 for k,page in enumerate(pages):
  raw=page
  if width(page)>LIMIT:
   choices=[i for i in valid_cuts(page) if width(page[:i])<=LIMIT and width(page[i:])<=LIMIT]
   if not choices:choices=valid_cuts(page)
   cut=min(choices,key=lambda i:quality(page,i)*2+abs(width(page[:i])-width(page[i:])))
   page=page[:cut]+'\n'+page[cut:]
  end=frames if k==len(pages)-1 else offset+round(frames*width(raw)/total)
  result.append(dict(fromFrame=offset,toFrame=end,text=page));offset=end
 return result
