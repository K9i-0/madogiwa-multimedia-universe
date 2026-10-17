"""Build the sole frame timeline from measured, un-stretched VOICEVOX clips."""
import json, math, re, wave
from pathlib import Path
P=Path(__file__).resolve().parent
FPS=30
rows=json.loads((P/'voice-manifest.json').read_text())['rows']
with wave.open(str(P.parent/'sobaya_beer.wav')) as w:
    growl_seconds=w.getnframes()/w.getframerate()
growl_frames=math.ceil(growl_seconds*FPS)
with wave.open(str(P.parent/'sobaya_early_murmur_v4.wav')) as w:
    early_frames=math.ceil(w.getnframes()/w.getframerate()*FPS)
cursor=90
clips=[];captions=[];chapters=[]
def lines(text):
    # Meaning-oriented line breaking, never start with closing punctuation.
    if len(text)<=30:return text
    candidates=[m.end() for m in re.finditer('[、。？！]',text) if 12<=m.end()<=30]
    cut=candidates[-1] if candidates else 28
    while cut<len(text) and text[cut] in '、。？！）」』':cut+=1
    return text[:cut]+'\n'+lines(text[cut:])
for i,r in enumerate(rows):
    if i==0 or r['chapter']!=rows[i-1]['chapter']:
        if i:cursor+=60
        chapters.append({'chapter':r['chapter'],'from':cursor})
    duration=math.ceil(r['seconds']*FPS)
    c={**r,'from':cursor,'duration':duration}
    clips.append(c)
    wrapped=lines(r['text']).split('\n')
    blocks=['\n'.join(wrapped[j:j+2]) for j in range(0,len(wrapped),2)]
    at=cursor;total=sum(len(b.replace('\n','')) for b in blocks)
    for k,b in enumerate(blocks):
        end=cursor+duration if k==len(blocks)-1 else at+round(duration*len(b.replace('\n',''))/total)
        captions.append({'from':at,'to':end,'text':b,'lineId':r['id'],'speaker':'narrator'});at=end
    pause=27 if r['text'].endswith(('。','」')) else 15
    if r['text'] in ['私にも見えました。','ごちそうさまでした','「ごちそうさまでした」','その夜の記憶は、そこまでです。']:pause=60
    if r['id']=='n0317':pause=60+15+growl_frames+36
    if r['id']=='n0073':pause=15+early_frames+24
    cursor+=duration+pause
duration=cursor+120
byid={r['id']:r for r in clips}
def frame(id):
    return next(r['from'] for r in clips if int(r['id'][1:5])>=id)
reveal=frame(317)+byid['n0317']['duration']+60
growl={'from':reveal+15,'duration':growl_frames,'file':'sobaya_beer.wav','text':'ビール……','speaker':'sobaya'}
captions.append({'from':growl['from'],'to':growl['from']+growl_frames,'text':'「ビール……」','lineId':'sobaya_beer','speaker':'sobaya'})
early={'from':frame(73)+byid['n0073']['duration']+15,'duration':early_frames,'file':'sobaya_early_murmur_v4.wav','speaker':'sobaya','intelligible':'partly','gain':0.85}
captions.sort(key=lambda c:c['from'])
def shotframe(n):return reveal if n==318 else frame(n)
# Authored shots are tied to exact spoken lines, never change randomly with captions.
keys=[
 (0,'office',None),(3,'office','m_photo'),(5,'office','y_guitar'),(9,'village',None),
 (14,'office','m_photo'),(19,'village',None),(27,'shrine',None),(31,'village',None),
 (37,'village','duo'),(47,'village','duo'),(50,'shrine',None),(54,'shrine','y_guitar'),
 (59,'broken',None),(66,'broken','m_photo'),(70,'broken',None),
 (79,'hall',None),(82,'broken',None),(87,'hall',None),(97,'office',None),
 (102,'morning',None),(108,'home_product',None),(117,'morning',None),(122,'home_product',None),(131,'home_product',None),
 (160,'office',None),(173,'office','y_photo'),(183,'office','m_photo'),
 (196,'home_product',None),(200,'home_product','m_photo'),(207,'office','y_photo'),(214,'office','sobaya_shadow_v4'),
 (220,'office','f_photo'),(226,'f_hakama',None),(230,'temple','f_photo'),(256,'shrine',None),(262,'shrine','note'),(268,'office','f_photo'),
 (275,'home_product',None),(280,'office','f_photo'),(289,'office','f_photo'),
 (295,'hall',None),(302,'village',None),(304,'hall',None),
 (318,'reveal',None),(339,'reveal',None),(346,'hall',None),(349,'reveal',None),
 (356,'reveal','y_photo'),(360,'reveal','m_photo'),(366,'reveal',None),
 (370,'reveal',None),(382,'reveal','m_photo'),(390,'reveal',None),
 (398,'reveal','y_photo'),(408,'reveal',None),(425,'asleep',None),
 (430,'hall_morning',None),(449,'shrine',None),(452,'morning',None),
 (468,'morning',None),(473,'office','f_photo'),(480,'morning',None)]
# Before the ritual, avoid showing four mugs, which are a later discovery.
keys=[(n,'village' if n in (79,87) else bg,person) for n,bg,person in keys]
keys=[(n,'temple' if person=='f_photo' else bg,person) for n,bg,person in keys]
shots=[]
for i,(n,bg,person) in enumerate(keys):
    start=0 if i==0 else shotframe(n)
    end=shotframe(keys[i+1][0]) if i+1<len(keys) else duration
    if end<=start:continue
    shots.append({'from':start,'to':end,'background':bg,'person':person,'crop':i%3})
events=[]
for phrase,kind,delay in [('一度目で屋根が割れました。','wood',1),('二度目で扉が外れました。','wood',1),('それから、向かいの空席へ缶を差し出しました。','can',0),('四つのジョッキが当たりました。','glass',1),('空になったジョッキが、机に当たりました。','glass',1),('冷蔵庫が鳴りました。','hum',0),('どこかで、窓枠がきしみました。','creak',0)]:
    c=next(c for c in clips if c['text']==phrase)
    events.append({'frame':c['from']+round(delay*FPS),'kind':kind})
manifest={'composition':{'id':'YVillage','width':1280,'height':720,'fps':FPS,'durationInFrames':duration},'narration':clips,'captions':captions,'chapters':chapters,'shots':shots,'sfx':events,'characterAudio':[growl,early],'revealFrame':reveal,'audio':'mix.wav'}
(P/'src/edit-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
def srt_time(frame):
    ms=round(frame/FPS*1000);h,ms=divmod(ms,3600000);mi,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{mi:02}:{s:02},{ms:03}'
(P.parent/'subtitles_ja.srt').write_text('\n\n'.join(f"{i+1}\n{srt_time(c['from'])} --> {srt_time(c['to'])}\n{c['text']}" for i,c in enumerate(captions))+'\n')
assert sum('中口' in c['text'] for c in clips)==2
assert all(s['background'] not in ('reveal','asleep') for s in shots if s['from']<reveal)
assert all(len(c['text'].splitlines())<=2 for c in captions)
assert all(captions[i]['to']<=captions[i+1]['from'] for i in range(len(captions)-1))
print(json.dumps({'frames':duration,'seconds':duration/FPS,'revealSeconds':reveal/FPS,'clips':len(clips),'captions':len(captions),'shots':len(shots)}))
