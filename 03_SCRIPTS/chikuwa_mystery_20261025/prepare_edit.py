from pathlib import Path
import json,os,re,budoux
P=Path(__file__).resolve().parent;D=P/'remotion';rows=json.loads((P/'voices.json').read_text());parser=budoux.load_default_japanese_parser()
clipdefs={'escape':dict(src='fishing_archive_v7.mp4',sourceStartFrame=0,durationInFrames=60,muteSource=True,label='研究所収集資料 ／ 天然ちくわの移動記録' ),'grill':dict(src='autumn.mp4',sourceStartFrame=204,durationInFrames=132,label='資料映像：秋のちくわ狩りが最盛期'),'expert':dict(src='autumn.mp4',sourceStartFrame=1017,durationInFrames=176,label='おかやまん准教授 ／ ちくわ生物学'),'theft':dict(src='autumn.mp4',sourceStartFrame=1424,durationInFrames=242,label='資料映像：秋のちくわ狩りが最盛期')}
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
coda=cursor+66
# Resolve reveals to actual VOICEVOX mora timing, not proportional text length.
def spoken_cue(row,word):
 q=json.loads((P/'audio_queries'/f"{row['id']}.json").read_text());t=q['prePhonemeLength']/q['speedScale'];joined='';starts=[]
 for phrase in q['accent_phrases']:
  for mora in phrase['moras']:
   joined+=mora['text'];starts.extend([t]*len(mora['text']));t+=(mora.get('consonant_length') or 0)/q['speedScale']+mora['vowel_length']/q['speedScale']
  pause=phrase.get('pause_mora')
  if pause:t+=pause['vowel_length']/q['speedScale']
 pos=joined.find(word)
 assert pos>=0,(word,joined)
 return row['startFrame']+round(starts[pos]*30)
charge=next(r for r in rows if r['view']=='additional_charge' and r['who']=='metan')
logic=next(r for r in rows if r['text'].startswith('毒ちくわを、一匹'))
absence=next(r for r in rows if r['view']=='poison_absence')
cues={'chargeReveal':spoken_cue(charge,'ワイセツ'),'logicReveal':spoken_cue(logic,'サイショカラ'),'absenceReveal':spoken_cue(absence,'イッサイ'),'horrorStart':next(r['startFrame'] for r in rows if r['view']=='poison_absence'),'silenceStart':logic['startFrame']-24,'silenceEnd':logic['startFrame']+logic['durationInFrames']+logic['pause'],'codaRecord':coda+210,'codaApproval':coda+420}
# Keep the late charge out of the subtitle until it is spoken.
caps=[c for c in caps if c['lineId']!=charge['id']]
for a,b,text in [(charge['startFrame'],cues['chargeReveal'],'なお、霜重研究員は、\n不法侵入に加えて、'),(cues['chargeReveal'],charge['startFrame']+charge['durationInFrames'],'猥褻物陳列罪の容疑でも\n逮捕されているわ。')]:caps.append(dict(startFrame=a,endFrame=b,text=text,lineId=charge['id']))
caps=[c for c in caps if c['lineId']!=logic['id']]
for a,b,text in [(logic['startFrame'],cues['logicReveal'],'毒ちくわを、一匹残らず\n取り除いているのではない。'),(cues['logicReveal'],logic['startFrame']+logic['durationInFrames'],'最初から、生きたちくわを一匹も\n使っていないのではないか。')]:caps.append(dict(startFrame=a,endFrame=b,text=text,lineId=logic['id']))
# Punchlines reveal with the spoken word, not the earlier caption page.
for prefix,word,key,left,right in [
 ('味、弾力','セエメエ','lifeReveal','味、弾力、焼き色まで再現できたわ。\n残る相違点は、','生命活動だけだった。')]:
 row=next(r for r in rows if r['text'].startswith(prefix));cut=spoken_cue(row,word);cues[key]=cut
 caps=[c for c in caps if c['lineId']!=row['id']]
 for a,b,text in [(row['startFrame'],cut,left),(cut,row['startFrame']+row['durationInFrames'],right)]:caps.append(dict(startFrame=a,endFrame=b,text=text,lineId=row['id']))
isobe=next(r for r in rows if r['view']=='isobe')
cues['isobeReveal']=spoken_cue(isobe,'イソベアゲ')
verdict=next(r for r in rows if r['text'].startswith('ただ、研究員は'))
cues['verdictReveal']=spoken_cue(verdict,'アゲタテ')
for row,key,left,right in [
 (isobe,'isobeReveal','中口研究員、昨日それを','磯辺揚げにしていたのだ。'),
 (verdict,'verdictReveal','ただ、研究員は最後まで比較を続けたそうよ。\n市販品も、天然物も、','揚げたてがおいしかったと。')]:
 caps=[c for c in caps if c['lineId']!=row['id']]
 cut=cues[key]
 for a,b,text in [(row['startFrame'],cut,left),(cut,row['startFrame']+row['durationInFrames'],right)]:caps.append(dict(startFrame=a,endFrame=b,text=text,lineId=row['id']))
caps.sort(key=lambda c:c['startFrame'])
m=dict(cues=cues,codaDurationFrames=600,codaStartFrame=coda,composition=dict(width=1280,height=720,fps=30,durationInFrames=coda+600),dialogue=rows,captions=caps,clips=clips,views=views,mainStartFrame=next(r['startFrame'] for r in rows if r['text'].startswith('めたんのミステリー研究所へ、ようこそ。'))-18,endingStartFrame=next(r['startFrame'] for r in rows if r['view']=='callback'),voicevoxVersion='0.25.1')
(D/'src/edit-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));print('DURATION',m['composition']['durationInFrames']/30,'views',len(views))
# Exact dialogue-only subtitles, same integer frame timing as manifest.
def tc(f):
 ms=round(f/30*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
(P/'subtitles.srt').write_text('\n\n'.join(f"{i+1}\n{tc(c['startFrame'])} --> {tc(c['endFrame'])}\n{c['text']}" for i,c in enumerate(caps))+'\n')
