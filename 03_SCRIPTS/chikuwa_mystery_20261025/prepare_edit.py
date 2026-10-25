from pathlib import Path
import json,os,re,budoux
P=Path(__file__).resolve().parent;D=P/'remotion';rows=json.loads((P/'voices.json').read_text());parser=budoux.load_default_japanese_parser()
clipdefs={'escape':dict(src='fishing.mp4',sourceStartFrame=26*30,durationInFrames=120,label='資料映像：天然ちくわの一本釣りとそばシャークのビール'),'grill':dict(src='autumn.mp4',sourceStartFrame=204,durationInFrames=132,label='資料映像：秋のちくわ狩りが最盛期'),'expert':dict(src='autumn.mp4',sourceStartFrame=1017,durationInFrames=176,label='おかやまん准教授 ／ ちくわ生物学'),'theft':dict(src='autumn.mp4',sourceStartFrame=1424,durationInFrames=242,label='資料映像：秋のちくわ狩りが最盛期')}
def wrap(text,limit=30):
 parts=parser.parse(text); lines=[];line=''
 for part in parts:
  if len(line)+len(part)>limit and line:lines.append(line);line=''
  line+=part
 if line:lines.append(line)
 return lines
cursor=18;clips=[];caps=[];views=[]
for r in rows:
 fp=D/'public'/r['audio']
 if not fp.exists():os.link(P/r['audio'],fp)
 r['startFrame']=cursor
 # Caption groups at punctuation and BudouX phrase boundaries, maximum 2 x 32 characters.
 lines=wrap(r['text']);groups=[''.join(lines[i:i+2]) for i in range(0,len(lines),2)]
 balanced=[]
 for g in groups:
  if len(g)<=30:balanced.append(g);continue
  parts=parser.parse(g);cuts=[];pos=0
  for part in parts[:-1]:
   pos+=len(part)
   if pos<=32 and len(g)-pos<=32:cuts.append(pos)
  cut=min(cuts,key=lambda n:abs(len(g)/2-n)) if cuts else len(g)//2
  balanced.append(g[:cut]+'\n'+g[cut:])
 groups=balanced
 # No inherited per-line overrides.
 total=sum(len(g.replace('\n','')) for g in groups);pos=0
 for g in groups:
  count=len(g.replace('\n',''));a=cursor+round(pos/total*r['durationInFrames']);pos+=count;b=cursor+round(pos/total*r['durationInFrames']);caps.append(dict(startFrame=a,endFrame=b,text=g,lineId=r['id']))
 if not views or views[-1]['view']!=r['view']:views.append(dict(view=r['view'],startFrame=0 if not views else cursor,endFrame=0))
 cursor+=r['durationInFrames']+r['pause']
 if r.get('clipAfter'):
  c=dict(clipdefs[r['clipAfter']],id=r['clipAfter'],startFrame=cursor);clips.append(c);cursor+=c['durationInFrames']+15
for i,v in enumerate(views):v['endFrame']=views[i+1]['startFrame'] if i+1<len(views) else cursor+90
m=dict(composition=dict(width=1280,height=720,fps=30,durationInFrames=cursor+90),dialogue=rows,captions=caps,clips=clips,views=views,mainStartFrame=next(r['startFrame'] for r in rows if r['text'].startswith('めたんのミステリー研究所へ、ようこそ。'))-18,endingStartFrame=next(r['startFrame'] for r in rows if r['scene']=='ending'),voicevoxVersion='0.25.1')
(D/'src/edit-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));print('DURATION',m['composition']['durationInFrames']/30,'views',len(views))
# Exact dialogue-only subtitles, same integer frame timing as manifest.
def tc(f):
 ms=round(f/30*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
(P/'subtitles.srt').write_text('\n\n'.join(f"{i+1}\n{tc(c['startFrame'])} --> {tc(c['endFrame'])}\n{c['text']}" for i,c in enumerate(caps))+'\n')
