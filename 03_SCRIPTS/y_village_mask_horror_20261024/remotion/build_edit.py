"""Frame-accurate short mask story. Speech duration is never time-stretched."""
from pathlib import Path
import json, math, re, shutil, subprocess
P=Path(__file__).resolve().parent;E=P.parent;fps=30
rows=json.loads((P/'voice-manifest.json').read_text())
def probe(f):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(f)]))
gaps={4:1.2,8:1.25,11:.8,15:1,18:.7,20:.2,21:1.6,24:.7,25:2.4,26:1.6,
      27:1.3,28:1.3,29:1.8,32:1.2,33:.9,35:1.7,36:.7,37:1,38:1.4,39:1.3,
      40:1.2,41:1.2,42:2.1,43:1.0,44:1.4,45:1.5,47:1.7,50:1.3,52:1,
      54:.8,56:1.0,58:1.7,60:.9,61:1.8,63:2.4,64:1,65:1.2,68:.8,70:1.2,
      71:.7,72:1.2,74:1.0,75:1.8,76:1.2,78:1.2,79:.8,80:1.2,81:1.8,
      82:1.2,83:2.7,84:1.9,85:2.8,86:1,87:1.1,88:2.8,89:.8,90:1.3,
      91:1.4,92:1.3,93:1.6,94:1.5,95:2.4,96:1.6,97:1.5,98:1.6,99:2.2,
      100:1.5,101:1.0,102:1.6,103:3.2,104:1.9,105:1.9,106:1.2,107:1.8,
      108:1.2,109:.7,110:.8,111:1.4,112:1.1,114:1.8,115:1.4,116:1.5,117:4.0}
cursor=100;events=[]
for r in rows:
    i=int(r['id'][1:]);source=E/r['file'] if r['engine']=='voicevox' else E/Path(r['file']).name
    seconds=r.get('seconds') or probe(source)
    target=P/'public/voice'/source.name;target.parent.mkdir(exist_ok=True)
    if not target.exists():shutil.copy2(source,target)
    n=math.ceil(seconds*fps)
    events.append({**r,'file':'voice/'+target.name,'from':cursor,'to':cursor+n,'duration':n,'seconds':seconds})
    cursor+=n+round(gaps.get(i,.45)*fps)
duration=cursor+30
assert duration <= 600*fps, f'Over ten-minute limit: {duration/fps}'
by={r['id']:r for r in events}
def at(i):return by[f'n{i:03d}']['from']
def end(i):return by[f'n{i:03d}']['to']
captions=[]
def wrap(text,maxlen=32):
    if len(text)<=maxlen:return text
    candidates=[i+1 for i,c in enumerate(text) if c in '、。！？』」' and 0<i<len(text)-1]
    candidates=[i for i in candidates if i<=maxlen and len(text)-i<=maxlen]
    k=min(candidates,key=lambda x:abs(x-len(text)/2)) if candidates else len(text)//2
    assert max(k,len(text)-k)<=maxlen,(text,k)
    return text[:k]+'\n'+text[k:]
for r in events:
    text=r['text']
    # The two long sentences are split at the actual AudioQuery pause.
    if r['id'] in ['n002','n072']:
        split=text.index('。')+1
        q=json.loads((E/'queries'/f"{r['id']}.json").read_text())
        # The first full stop is the first long pause in these lines.
        t=q['prePhonemeLength'];boundary=None
        for phrase in q['accent_phrases']:
            t+=sum(m.get('consonant_length',0) or 0 for m in phrase['moras'])
            t+=sum(m['vowel_length'] for m in phrase['moras'])
            if phrase.get('pause_mora'):
                t+=phrase['pause_mora']['vowel_length']
                # n002 has a comma before the sentence break; use expected proportional position,
                # selecting the closest synthesis pause to the first sentence's character share.
        wanted=split/len(text)*r['seconds'];time=q['prePhonemeLength'];pauses=[]
        for phrase in q['accent_phrases']:
            for mora in phrase['moras']:time+=(mora.get('consonant_length') or 0)+mora['vowel_length']
            if phrase.get('pause_mora'):
                time+=phrase['pause_mora']['vowel_length'];pauses.append(time)
        boundary=min(pauses,key=lambda x:abs(x-wanted))
        cut=r['from']+round(boundary*fps)
        for a,b,tx in [(r['from']+2,cut,text[:split]),(cut,r['to']+5,text[split:])]:
            captions.append({'id':r['id']+str(a),'from':a,'to':b,'text':wrap(tx),'speaker':r['speaker']})
    else:captions.append({'id':r['id'],'from':r['from']+2,'to':r['to']+min(8,round(gaps.get(int(r['id'][1:]),.45)*fps)-1),'text':wrap(text),'speaker':r['speaker']})
shots=[]
def shot(a,b,image,zoom=1,move=.035,fx=50,fy=42,brightness=1,person='',mode='normal',fade=0):
    start=at(a) if isinstance(a,int) and a>=0 else 0
    stop=at(b) if b is not None else duration
    shots.append({'from':start,'to':stop,'image':image,'zoom':zoom,'move':move,'focusX':fx,'focusY':fy,'brightness':brightness,'person':person,'mode':mode,'fade':fade})
shot(-1,2,'village',1.04,.035,55,38,.88)
shot(2,3,'office',1.01,.015,50,40,.86,'duo')
shot(3,5,'village',1.12,.02,65,42,.91)
shot(5,9,'forbidden_corridor',1,.045,58,44,.9)
shot(9,12,'forbidden_corridor',1.18,.03,58,44,.83)
shot(12,13,'forbidden_room',1,.025,52,40,.95)
shot(13,16,'mask_intact',1,.055,50,42,.83)
shot(16,19,'mask_intact',1.12,.025,48,44,.85)
shot(19,21,'mask_intact',1.08,.0,50,45,.8)
shot(21,24,'mask_broken_v2',1.0,.04,45,40,.82)
shot(24,25,'forbidden_room',1.12,.015,52,39,.74)
shot(25,27,'forbidden_room',1.12,0,52,39,.61)
shot(27,29,'lodge_door_empty',1,0,62,33,1)
shot(29,31,'lodge_door_entity_v2',1,0,62,33,1)
shot(31,34,'lodge_door_entity_v2',1.17,.015,62,33,1)
shot(34,36,'mask_press',1,0,61,36,.96)
shot(36,39,'lodge_door_empty',1,0,62,33,1)
shot(39,40,'home_empty',1,0,64,38,1.1)
shot(40,42,'home_door_entity_v2',1,0,64,38,1)
shot(42,45,'under_blanket',1,.035,59,38,.84)
shot(45,48,'under_blanket',1.15,.0,58,40,.62)
shot(48,50,'cheek_mark',1,.025,52,45,.94,fade=10)
shot(50,51,'mask_broken_v2',1.35,0,45,50,.70)
shot(51,53,'home_empty',1.07,.02,62,42,1.1)
shot(53,57,'home_empty',1.0,.018,56,42,1.15,'y_photo',mode='phone')
shot(57,60,'home_empty',1.0,0,56,42,1.15,'m_photo',mode='phone')
shot(60,62,'towel_hand',1,.02,62,35,.84)
shot(62,66,'forbidden_corridor',1.22,0,58,43,.7,mode='phone')
shot(66,71,'consultation_room',1.55,.015,15,40,.88,'f_photo')
shot(71,73,'mask_press',1.12,0,61,36,.83)
shot(73,75,'consultation_room',1.55,.01,15,42,.88,'y_photo')
shot(75,76,'consultation_room',1.30,.045,80,42,.84)
shot(76,77,'village',1.12,.01,58,43,.70)
shot(77,79,'mask_broken_v2',1.07,.01,50,43,.65)
shot(79,80,'mask_repaired',1,.01,50,40,.85)
shot(80,83,'ritual_room',1.0,0,50,40,1.06,'f_photo')
shot(83,84,'mask_repaired',1.07,.012,50,40,.83)
shot(84,89,'ritual_room',1,0,50,40,.8,mode='eyes-closed')
shot(89,93,'face_pressure',1,.02,50,38,.72,mode='pressure',fade=8)
shot(93,97,'mask_repaired',1.10,0,50,40,.50,mode='false-voice')
shot(97,100,'face_pressure',1.12,0,50,38,.46,mode='pressure')
shot(100,103,'neck_grip',1,.03,55,42,.72,mode='turn')
shot(103,104,'face_pressure',1.05,0,50,38,.42,mode='pressure')
shot(104,108,'forbidden_room',1,0,50,40,.9,mode='dawn')
shot(108,110,'forbidden_room',1.20,.0,51,37,.95,fade=18)
shot(110,112,'door_locked',1,.018,65,48,.95)
shot(112,115,'office',1.01,.02,51,41,1.02)
shot(115,None,'home_empty',1,0,63,36,1,mode='ending')
regions=[]
def region(a,b,music,room=.002,fade=20):regions.append({'from':at(a),'to':at(b) if b is not None else duration,'music':music,'ambient':room,'fade':fade})
region(19,24,.10,.002,5)
region(25,27,0,.002,8)
region(27,29,.3,.0018,12)
region(29,39,.10,.0018,5)
region(40,48,0,.0015,10)
region(50,51,.15,.0016,5)
region(60,62,0,.0018,8)
region(63,66,.12,.0015,8)
region(75,76,.15,.0015,6)
region(81,84,.18,.002,12)
region(84,108,0,.002,20)
region(108,112,.24,.002,30)
region(115,None,0,.001,24)
sfx=[]
def sound(kind,frame,gain=1,pan=0):sfx.append({'kind':kind,'frame':round(frame),'gain':gain,'pan':pan})
sound('slide',at(9)+8,.5,-.25)
sound('crack',at(21)+45,.8)
sound('breath',end(25)+4,.30,-.45)
sound('step',at(27)+20,.5,.1);sound('step',at(27)+57,.6,.15)
sound('breath',end(29)+8,.35,.3)
sound('fabric',at(35)+10,.35)
sound('breath',end(42)+3,1.2,.65)
sound('fabric',at(44)-5,.50,.3)
sound('fabric',at(60)+115,.25,.3)
sound('wood',at(75)+90,.4,.4)
sound('cloth',at(79)+60,.45)
sound('slide',end(84)+3,.7,0)
for offset,gain in [(10,.35),(61,.45),(116,.58),(171,.70)]:sound('step',at(85)+offset,gain,0)
sound('breath',end(86),.38,.7);sound('cloth',end(87),.35,-.65)
sound('fabric',end(89)+3,.50,0)
sound('fabric',at(91)+12,.38,-.35);sound('fabric',at(91)+65,.40,.4)
sound('breath',end(94)+5,.5,.85)
sound('fabric',at(100)+18,.50,.6)
sound('bird',end(105)+8,.4,-.2)
sound('bird',end(106)+5,.30,.35)
sound('wood',end(108)-15,.35)
sound('lock',at(111)+45,.40)
sound('cloth',at(115)+100,.23,0)
result={'composition':{'id':'YVillageMask','width':1280,'height':720,'fps':fps,'durationInFrames':duration},
 'title':'廃村Y村の怪異S','audio':'mix.wav','narration':events,'captions':captions,'shots':shots,'soundRegions':regions,'sfx':sfx,
 'ritual':{'start':end(83)-20,'end':at(105),'surge':at(101)},
 'metadata':{'version':'mask-v1','normalSpeed':True,'referenceMusic':'KK — 不安、恐怖、戦慄','story':'forbidden room / broken mask / returning the face'}}
(P/'src/edit-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
chapters=[(0,'Y村の研修所'),(9,'入ってはいけない部屋'),(27,'戸の隙間'),(39,'自宅まで'),(53,'三人とも'),(66,'F先生'),(76,'面を返す'),(84,'目を開けてはいけない'),(108,'朝')]
(E/'timing.md').write_text('# 編集時刻\n\n'+ '\n'.join(f'- {int(at(i)/fps)//60}:{int(at(i)/fps)%60:02d} {label}' for i,label in chapters)+f'\n\n完成尺：{duration/fps:.3f}秒。朗読は標準速度、早回しなし。\n')
print('duration',duration/fps,'seconds; frames',duration,'captions',len(captions),'shots',len(shots))
for i,label in chapters:print(f'{at(i)/fps:7.2f}',label)
