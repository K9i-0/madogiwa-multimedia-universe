import json, math, re, os, subprocess, hashlib
from pathlib import Path

EP=Path(__file__).resolve().parent
ROOT=EP.parents[1]
PUB=EP/'remotion/public'; PUB.mkdir(exist_ok=True)
assets={
 'professional.mp4':ROOT/'03_SCRIPTS/59_sobaya_professional_window_side/wan3_professional_window_side_seed590831_480p.mp4',
 'chair.mp4':ROOT/'03_SCRIPTS/51_aronchia_makers_vlog/wan3_result_seed510030_480p.mp4',
 'kit.mp4':ROOT/'03_SCRIPTS/chuagostini_20261003/wan3_cm_v2_seed310003_480p_28s.mp4',
 'interview.png':EP/'interview_clean.png',
}
for name,src in assets.items():
 if not (PUB/name).exists():os.link(src,PUB/name)
for name,src,t in [('portrait.jpg','professional.mp4',26),('desk.jpg','professional.mp4',18),('chair.jpg','chair.mp4',27),('room.jpg','kit.mp4',16)]:
 if not (PUB/name).exists():subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(PUB/src),'-frames:v','1',str(PUB/name)],check=True)

lines=json.loads((EP/'dialogue.json').read_text())
voices={r['id']:r for r in json.loads((EP/'voice_generation_record.json').read_text())} if (EP/'voice_generation_record.json').exists() else {}
chapters=['','エクセル操作してるフリの終焉','切り札は「MDE」','FDEとMDE 何が違う？','育成現場に潜入','窓際を、再現可能に','AI時代に残る人間の価値','全社展開への課題']
visuals=['excel','ai','interview','definition','interview','deployment','fde','compare','interview','question','interview','archiveIntro','archive','workshop','workshop','team','workshopQuote','chairResult','kit','scale','question','invest','question','human','question','philosophy','recap','interview','interview','question','windows','ending']
highlights={3:'持続可能ではない',5:'左遷ではなく、\n戦略的配置',9:'窓際に、深く入り込む',11:'導入して\n終わりじゃない',17:'座るために、何でもやる',20:'新人でも、初日から座れる',22:'人罪への投資です',24:'最後に席を埋めるのは、人間',26:'何もしなくていい状態を、作る',29:'この取り組みを\n全社へ',31:'次の経営課題：窓不足'}
cursor=0; scenes=[]; caps=[]
scenes.append(dict(id='opening',start=0,duration=90,kind='opening',chapter=0,title='',speaker='',text=''))
cursor=90
prev=0
for i,line in enumerate(lines,1):
 ch=line['chapter']
 if ch!=prev and ch>1:
  scenes.append(dict(id=f'chapter{ch}',start=cursor,duration=42,kind='chapter',chapter=ch,title=chapters[ch],speaker='',text=''))
  cursor+=42
 prev=ch
 rec=voices.get(line['id'])
 seconds=rec['duration'] if rec else max(2,len(line['text'])/6)
 n=math.ceil(seconds*30)
 gap=24 if i in [13,22,26,31] else 12
 scene=dict(line,start=cursor,duration=n+gap,audioFrames=n,kind=visuals[i-1],title=chapters[ch],highlight=highlights.get(i,''),audio=rec['path'] if rec else None)
 scenes.append(scene)
 if rec:
  dst=PUB/rec['path']
  if not dst.exists():os.link(EP/rec['path'],dst)
 # Phrase-sized cards; replaced with ASR-aligned boundaries when available.
 phrases=re.findall(r'[^。！？]+[。！？]?',line['text'])
 chunks=[]
 for phrase in phrases:
  if len(phrase)<=44: chunks.append(phrase)
  else:
   parts=re.findall(r'[^、]+、?',phrase); buf=''
   for part in parts:
    if len(buf+part)>40 and buf:chunks.append(buf);buf=''
    buf+=part
   if buf:chunks.append(buf)
 total=sum(len(x) for x in chunks); pos=0
 for chunk in chunks:
  a=round(n*pos/total);pos+=len(chunk);b=round(n*pos/total)
  if len(chunk)>25:
   options=[m.end() for m in re.finditer('、|。',chunk) if 4<=m.end()<=len(chunk)-4]
   split=min(options,key=lambda x:abs(x-len(chunk)/2)) if options else len(chunk)//2
   display=chunk[:split]+'\n'+chunk[split:]
  else:display=chunk
  caps.append(dict(lineId=line['id'],start=cursor+a,end=cursor+b,text=display,speaker=line['speaker']))
 cursor+=n+gap
 # Original chair test, pause the narration rather than talking over the source.
 if i==17:
  scenes.append(dict(id='chairTest',start=cursor,duration=105,kind='chairTest',chapter=4,title=chapters[4],speaker='sobaya',text='快適です！'))
  caps.append(dict(lineId='chairTest',start=cursor+32,end=cursor+98,text='快適です！',speaker='sobaya'))
  cursor+=105
scenes.append(dict(id='endHold',start=cursor,duration=54,kind='endHold',chapter=7,title=chapters[7],speaker='',text=''))
cursor+=54
manifest=dict(composition=dict(id='MDECrosstech',width=1280,height=720,fps=30,durationInFrames=cursor),chapters=chapters,scenes=scenes,captions=caps,voiceComplete=len(voices)==len(lines))
(EP/'remotion/src/edit-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Frames',cursor,'seconds',cursor/30,'voices',len(voices),'/',len(lines))

for name in json.loads((EP/'scene_images/adopted.json').read_text()):
 dst=PUB/'scenes'/f'{name}.png';dst.parent.mkdir(exist_ok=True)
 if not dst.exists():os.link(EP/'scene_images'/f'{name}.png',dst)
