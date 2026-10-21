"""BudouX phrase boundaries, protected technical terms and Japanese kinsoku."""
import re
import budoux
PARSER=budoux.load_default_japanese_parser()
OPEN='「『（【';CLOSE='」』）】';END='。！？';NO_START='、。？！）」』】'
TERMS=['Chief Ticket Officer','CTOおだてつ','Dart MCP','Marionette MCP','mobile MCP','Dart Tooling Daemon','Dart VM Service','WebDriverAgent','hot reload','Widgetツリー','Flutter Scene','Flutter GPU','FlutterKaigi 2026','Claude Code','Pixel 7a','iPhone 14','窓際族物語','毎フレーム','テクスチャ','共同著者表記','ライフサイクル','パフォーマンス','キャラクター','シミュレーション']
def width(s):return sum(.56 if ord(c)<128 else 1 for c in s)
def legal(s,i):
 if i<=0 or i>=len(s):return False
 if s[i] in NO_START or s[i-1] in OPEN:return False
 if re.match(r'[A-Za-z0-9_.]',s[i-1]) and re.match(r'[A-Za-z0-9_.]',s[i]):return False
 for term in TERMS:
  for m in re.finditer(re.escape(term),s):
   if m.start()<i<m.end():return False
 return True
def cuts(s):
 n=0;out=[]
 for part in PARSER.parse(s):
  n+=len(part)
  if legal(s,n):out.append(n)
 return out
def captions(text,frames):
 parts=[];part='';depth=0
 for c in text:
  part+=c
  if c in OPEN:depth+=1
  elif c in CLOSE:depth=max(0,depth-1)
  if c in END and depth==0:parts.append(part);part=''
 if part:parts.append(part)
 pages=[]
 for s in parts:
  while width(s)>54:
   options=[i for i in cuts(s) if 21<=width(s[:i])<=46]
   if not options:options=[i for i in range(1,len(s)) if legal(s,i) and width(s[:i])<=46]
   i=max(options,key=lambda x:(s[x-1] in '、。！？',width(s[:x])))
   pages.append(s[:i]);s=s[i:]
  if s:pages.append(s)
 out=[];offset=0;total=sum(map(len,pages))
 for n,s in enumerate(pages):
  raw=s
  if width(s)>27:
   options=[i for i in cuts(s) if width(s[:i])<=28 and width(s[i:])<=28]
   if not options:options=[i for i in range(1,len(s)) if legal(s,i)]
   i=min(options,key=lambda i:abs(width(s[:i])-width(s[i:]))-(3 if s[i-1] in '、。！？'+CLOSE else 0))
   s=s[:i]+'\n'+s[i:]
  end=frames if n==len(pages)-1 else offset+round(frames*len(raw)/total)
  out.append(dict(fromFrame=offset,toFrame=end,text=s));offset=end
 return out
