"""Caption pages preserve quoted phrases and Japanese line-breaking rules."""
OPEN='「『（【';CLOSE='」』）】';END='。！？';NO_START='、。？！）」』】'
def captions(text,frames):
 parts=[];part='';depth=0
 for char in text:
  part+=char
  if char in OPEN:depth+=1
  elif char in CLOSE:depth=max(0,depth-1)
  if char in END and depth==0:
   parts.append(part);part=''
 if part:parts.append(part)
 # Attach any terminal punctuation to the preceding part.
 merged=[]
 for part in parts:
  if merged and all(c in NO_START for c in part):merged[-1]+=part
  else:merged.append(part)
 pages=[]
 for part in merged:
  while len(part)>56:
   valid=[i for i in range(18,min(51,len(part)-1)+1) if part[i] not in NO_START and part[i-1] not in OPEN]
   preferred=[i for i in valid if part[i-1] in '、。？！'+CLOSE]
   cut=preferred[-1] if preferred else min(valid,key=lambda i:abs(i-28))
   pages.append(part[:cut]);part=part[cut:]
  if part:pages.append(part)
 result=[];offset=0;total=sum(map(len,pages))
 for i,page in enumerate(pages):
  raw=page
  if len(page)>28:
   choices=[j for j in range(max(1,len(page)-28),min(28,len(page)-1)+1) if page[j] not in NO_START and page[j-1] not in OPEN]
   preferred=[j for j in choices if page[j-1] in '、。？！'+CLOSE]
   cut=min(preferred or choices,key=lambda j:abs(j-len(page)/2));page=page[:cut]+'\n'+page[cut:]
  end=frames if i==len(pages)-1 else offset+round(frames*len(raw)/total)
  result.append(dict(fromFrame=offset,toFrame=end,text=page));offset=end
 return result
