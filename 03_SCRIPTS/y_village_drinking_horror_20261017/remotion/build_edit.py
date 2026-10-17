"""v7: two-stage entity reveal and three intentionally silly monkey calls."""
import json, math, re, wave
from pathlib import Path
P=Path(__file__).resolve().parent
FPS=30
rows=json.loads((P/'voice-manifest.json').read_text())['rows']
def wav_frames(path):
    with wave.open(str(path)) as w:return math.ceil(w.getnframes()/w.getframerate()*FPS)
growl_frames=wav_frames(P.parent/'sobaya_beer.wav')
early_frames=wav_frames(P.parent/'sobaya_early_murmur_v4.wav')
# Added silence is separate from the .15/.35 seconds already inside each WAV.
# Only discoveries, unanswered questions and deliberate visual inspection wait.
pauses={
 'n0010':24,'n0013b':21,'n0027':21,'n0044':24,
 'n0053v5a0':18,'n0062':21,
 'n0073':15+early_frames+24,'n0073v5a0':24,'n0075v7a0':36,'n0076':30,'n0078':42,
 'n0086':30,'n0093':42,'n0101':30,'n0110':27,'n0117':27,'n0121':36,'n0126':30,
 'n0134':48,'n0135':36,'n0143':48,'n0150':36,'n0153':42,'n0155v6a0':30,
 'n0166v6a0':27,'n0179':42,'n0192':36,'n0194':30,
 'n0202':66,'n0203':27,'n0219':30,
 'n0219v6a3':30,'n0219v6a4':30,'n0219v6a5':36,'n0219v6a6':48,'n0219v6a7':15,'n0219v6a8':42,
 'n0255v5a3':18,'n0237':24,'n0238':48,'n0243':24,'n0245':30,'n0248':36,'n0248v6a0':36,
 'n0265':30,'n0280':24,'n0288v6a0':36,
 'n0307':36,'n0311':24,'n0312':30,'n0313':30,'n0314':36,'n0316':42,
 'n0317':54+15+growl_frames+30,'n0324':42,'n0328':30,
 'n0332':36,'n0333':48,'n0338':30,
 'n0344':30,'n0359':36,'n0366':30,'n0367':18,'n0368':36,
 'n0375':42,'n0380':24,'n0385v6a0':30,'n0393':42,'n0396':30,
 'n0408':36,'n0411':30,'n0415':42,'n0417':30,'n0417v6a0':36,
 'n0421':30,'n0422':45,'n0424':42,'n0427':36,'n0429':48,
 'n0437':27,'n0438':42,'n0441':27,'n0456':30,'n0457':36,'n0464':30,
 'n0479':42,'n0486':48,'n0487':60,
}
recorded={'n0134','n0143','n0153','n0273','n0274'}
clips=[];captions=[];chapters=[];cursor=90
def wrap(text):
    if len(text)<=30:return [text]
    choices=[m.end() for m in re.finditer('[、。？！]',text) if 12<=m.end()<=30]
    cut=choices[-1] if choices else 28
    while cut<len(text) and text[cut] in '、。？！）」』':cut+=1
    return [text[:cut]]+wrap(text[cut:])
for i,r in enumerate(rows):
    newchapter=i==0 or r['chapter']!=rows[i-1]['chapter']
    if newchapter:
        if i:cursor+=30 if r['chapter'] not in (5,9,11,16,17) else 42
        chapters.append({'chapter':r['chapter'],'from':cursor})
    dur=math.ceil(r['seconds']*FPS)
    c={**r,'from':cursor,'duration':dur,'audioStyle':'recording' if r['id'] in recorded else 'narration'}
    clips.append(c)
    lines=wrap(r['text']);blocks=['\n'.join(lines[j:j+2]) for j in range(0,len(lines),2)]
    at=cursor+3;total=sum(len(b.replace('\n','')) for b in blocks)
    for j,b in enumerate(blocks):
        end=cursor+dur-3 if j==len(blocks)-1 else at+round((dur-6)*len(b.replace('\n',''))/total)
        captions.append({'from':at,'to':end,'text':b,'lineId':r['id'],'speaker':'narrator'});at=end
    pause=pauses.get(r['id'],9 if r['text'].endswith(('、','。','」')) else 6)
    cursor+=dur+pause
end=cursor+120
by={r['id']:r for r in clips}
def at(id):return by[id]['from']
def after(id):return at(id)+by[id]['duration']
reveal=after('n0317')+54
glimpse=at('n0075v7a0')
growl={'from':reveal+15,'duration':growl_frames,'file':'sobaya_beer.wav','text':'ビール……','speaker':'sobaya','gain':.9}
early={'from':after('n0073')+15,'duration':early_frames,'file':'sobaya_early_murmur_v4.wav','speaker':'sobaya','intelligible':'partly','gain':.85}
captions.append({'from':growl['from'],'to':growl['from']+growl_frames,'text':'「ビール……」','lineId':'sobaya_beer','speaker':'sobaya'})
captions.sort(key=lambda c:c['from'])
# Every cut is attached to a surviving exact anchor; reordered F dialogue is safe.
shots=[]
def shot(id,bg,person=None,zoom=1.02,x=50,y=50,view='plain',move=0,brightness=.69):
    f=id if isinstance(id,int) else at(id)
    shots.append({'from':f,'background':bg,'person':person,'zoom':zoom,'focusX':x,'focusY':y,'view':view,'move':move,'brightness':brightness})
shot(0,'office',move=.015)
shot('n0003','office','m_photo',brightness=.78)
shot('n0005','office','y_guitar',brightness=.78)
shot('n0009','village',move=.018,brightness=.74)
shot('n0013','village','duo',brightness=.78)
shot('n0019','village',zoom=1.12,x=45,y=50,brightness=.77)
shot('n0024a','village','duo',brightness=.78)
shot('n0025','shrine',brightness=.76)
shot('n0027','shrine',zoom=1.14,x=65,y=65,move=.012,brightness=.74)
shot('n0032','village',brightness=.73)
shot('n0037','village','duo',brightness=.70)
shot('n0038','village','m_photo',brightness=.70)
shot('n0047','village','duo',brightness=.49)
shot('n0050','shrine',brightness=.67)
shot('n0052','shrine',zoom=1.65,x=71,y=74,brightness=.73)
shot('n0054','shrine','y_guitar',brightness=.70)
shot('n0056a','shrine',zoom=1.06,brightness=.64)
shot('n0059','broken',zoom=1.08,brightness=.67)
shot('n0060','broken','duo',brightness=.65)
shot('n0062','broken',zoom=1.40,x=58,y=74,brightness=.70)
shot('n0064','broken','m_photo',brightness=.67)
shot('n0069','broken','y_guitar',brightness=.67)
shot('n0073','broken',zoom=1.16,x=42,y=46,brightness=.48)
shot(glimpse,'sobaya_moonlit_v7',zoom=1,view='cursed-pov',brightness=.93)
shot('n0076','broken',zoom=1.12,view='recording',brightness=.57)
shot('n0079','village',brightness=.77)
shot('n0084','broken',brightness=.73)
shot('n0086','shrine',zoom=1.15,x=65,y=64,brightness=.66)
shot('n0088','village',brightness=.47)
shot('n0091','broken',zoom=1.25,x=53,y=68,brightness=.70)
shot('n0096','office',brightness=.72)
shot('n0102','morning',brightness=.72)
shot('n0105','home_product',zoom=1.10,x=50,y=40,brightness=.56)
shot('n0109','home_product',zoom=1.55,x=12,y=76,brightness=.72)
shot('n0111','home_product',zoom=1.05,x=50,y=44,brightness=.66)
shot('n0118','morning',zoom=1.12,x=35,y=70,brightness=.60)
shot('n0121','home_product',zoom=1.5,x=13,y=30,brightness=.48)
shot('n0122','home_product',brightness=.65)
shot('n0127','home_empty_v6',zoom=1.03,view='recording',brightness=.67)
shot('n0133','home_toast_v6',zoom=1.03,view='recording',brightness=.71)
shot('n0136','home_empty_v6',zoom=1.03,view='recording',brightness=.67)
shot('n0147','home_empty_v6',zoom=1.12,x=55,y=40,view='recording',brightness=.67)
shot('n0153','home_empty_v6',zoom=1.12,x=55,y=40,view='recording',brightness=.67)
shot('n0155','home_empty_v6',zoom=1.08,brightness=.59)
shot('n0160','office',brightness=.61)
shot('n0163','home_product',zoom=1.1,brightness=.55)
shot('n0167','office','m_photo',brightness=.72)
shot('n0168','office',brightness=.65)
shot('n0173','office','y_photo',brightness=.65)
shot('n0179','office','y_photo',zoom=1.12,brightness=.60)
shot('n0180','office','m_photo',brightness=.63)
shot('n0189','home_product',zoom=1.12,view='witness',brightness=.58)
shot('n0192','home_product',zoom=1.42,x=55,y=40,view='witness',brightness=.65)
shot('n0196','home_product',zoom=1.12,view='recording',brightness=.66)
shot('n0200','home_product','m_photo',view='recording',brightness=.66)
shot('n0202','home_product',zoom=1.42,x=55,y=40,view='recording',brightness=.69)
shot('n0204','office','m_photo',brightness=.65)
shot('n0207','office','y_photo',brightness=.63)
shot('n0214','sobaya_moonlit_v7',zoom=1,view='cursed-memory',brightness=.93)
shot('n0219v6a0','home_empty_v6',zoom=1.12,x=55,y=40,brightness=.59)
shot('n0219v6a4','hand_can_sealed_v6',zoom=1,brightness=.72)
shot(after('n0219v6a5')+6,'hand_can_open_v6',zoom=1,brightness=.72)
shot('n0219v6a9','morning',zoom=1.07,brightness=.64)
shot('n0220','temple','f_photo',brightness=.73)
shot('n0226','f_hakama',zoom=1,brightness=.95)
shot('n0230','temple','f_photo',brightness=.73)
shot('n0255v5a6','temple','y_photo',brightness=.70)
shot('n0233','temple','f_photo',brightness=.71)
shot('n0237','temple','f_photo',brightness=.63)
shot('n0245','temple','f_photo',zoom=1.08,x=40,y=55,brightness=.63)
shot('n0248v6a0','temple','f_photo',brightness=.61)
shot('n0251','shrine',zoom=1.15,x=63,y=60,brightness=.64)
shot('n0255','temple','f_photo',brightness=.65)
shot('n0256','shrine',brightness=.71)
shot('n0264','shrine','note',brightness=.67)
shot('n0271','temple','f_photo',brightness=.67)
shot('n0272','broken',zoom=1.12,view='recording',brightness=.64)
shot('n0275','temple','f_photo',brightness=.65)
shot('n0278','home_toast_v6',zoom=1.03,view='recording',brightness=.71)
shot('n0280','temple','f_photo',brightness=.65)
shot('n0296','hall',brightness=.72)
shot('n0298','hall',zoom=1.28,x=50,y=61,brightness=.70)
shot('n0301','shrine',brightness=.64)
shot('n0303','village',brightness=.49)
shot('n0305','hall',brightness=.67)
shot('n0307','hall',zoom=1.28,x=50,y=48,brightness=.69)
shot('n0308','hall','f_photo',brightness=.67)
shot('n0311','hall',zoom=1.14,x=50,y=51,brightness=.64)
shot('n0312','hall',zoom=1.05,x=50,y=42,brightness=.61)
shot(reveal,'reveal',zoom=1.05,x=50,y=40,brightness=.70)
shot('n0320','reveal',zoom=1.65,x=43,y=72,brightness=.72)
shot('n0322','reveal',zoom=1.34,x=50,y=35,brightness=.68)
shot('n0325','hall','f_photo',brightness=.65)
shot('n0331','reveal',zoom=2.12,x=49,y=76,brightness=.73)
shot('n0339','hall',zoom=1.35,x=50,y=80,brightness=.70)
shot('n0341','reveal',zoom=1.08,x=50,y=42,brightness=.69)
shot('n0346','hall',zoom=1.1,x=50,y=45,view='f-perspective',brightness=.63)
shot('n0349','hall',zoom=1.50,x=25,y=88,brightness=.66)
shot('n0352','reveal',zoom=1.46,x=50,y=34,brightness=.66)
shot('n0356','hall','y_photo',brightness=.68)
shot('n0359','reveal',zoom=1.30,x=52,y=35,brightness=.66)
shot('n0360','hall','m_photo',brightness=.68)
shot('n0366','reveal',zoom=1.08,x=50,y=40,brightness=.68)
shot('n0367','sobaya_clap_v6',zoom=1,brightness=.70)
shot('n0368','hall','m_photo',brightness=.67)
shot('n0370','hall',zoom=1.12,x=50,y=49,brightness=.60)
shot('n0371','hall','m_photo',brightness=.65)
shot('n0373','sobaya_mug_v6',zoom=1,brightness=.70)
shot('n0376','hall','m_photo',brightness=.66)
shot('n0377','hall','f_photo',brightness=.64)
shot('n0381','hall','m_photo',brightness=.65)
shot('n0385','reveal',zoom=1.74,x=65,y=74,brightness=.70)
shot('n0385v6a0','hall','m_photo',brightness=.63)
shot('n0390','hall',zoom=1.50,x=25,y=85,brightness=.63)
shot('n0392','reveal',zoom=1.4,x=50,y=35,brightness=.67)
shot('n0393','hall','f_photo',brightness=.62)
shot('n0395','hall',zoom=1.17,x=18,y=48,brightness=.62)
shot('n0405','hall','y_photo',brightness=.65)
shot('n0408','hall',zoom=1.18,x=50,y=80,brightness=.61)
shot('n0408v6a0','hall','f_photo',brightness=.60)
shot('n0408v6a1','reveal',zoom=2.12,x=49,y=76,brightness=.70)
shot('n0409','reveal',zoom=1.03,x=50,y=42,brightness=.64)
shot('n0411','reveal',zoom=2.12,x=49,y=76,brightness=.69)
shot('n0415','reveal',zoom=1.34,x=50,y=34,brightness=.65)
shot('n0417v6a0','reveal',zoom=2.12,x=49,y=76,brightness=.70)
shot('n0419','reveal',zoom=1.06,x=50,y=42,brightness=.65)
shot('n0421','hall_morning',zoom=2.18,x=49,y=85,brightness=.30)
shot('n0424','asleep',zoom=1.04,x=50,y=55,brightness=.68)
shot('n0430','hall_morning',brightness=.84)
shot('n0438','hall_morning',zoom=1.25,x=50,y=37,brightness=.80)
shot('n0448','shrine',brightness=.75)
shot('n0451','morning',zoom=1.08,brightness=.64)
shot('n0456','morning',brightness=.92)
shot('n0459','morning',zoom=1.35,x=24,y=79,brightness=.92)
shot('n0468','office',brightness=.79)
shot('n0473','temple','f_photo',brightness=.68)
shot('n0481','morning',brightness=.77)
shot('n0483v6a1','home_empty_v6',zoom=1.12,x=55,y=40,view='memory',brightness=.63)
shots.sort(key=lambda s:s['from'])
assert len({s['from'] for s in shots})==len(shots)
for i,s in enumerate(shots):s['to']=shots[i+1]['from'] if i+1<len(shots) else end
inserts=[{'kind':'excel','from':at('n0002v5a1'),'to':after('n0002v5a2')+9,'changeFrame':at('n0002v5a2')},
         {'kind':'excel-return','from':at('n0471v6a0'),'to':after('n0471v6a0')+9,'changeFrame':at('n0471v6a0')+65}]
# Music is absent for evidence scenes; a room tone keeps the space real.
sound_regions=[]
def sound(first,last,music=0,ambient=.004,silence=False,fade=12):
    a=first if isinstance(first,int) else at(first)
    b=last if isinstance(last,int) else after(last)+pauses.get(last,9)
    sound_regions.append({'from':a,'to':b,'music':music,'ambient':ambient,'silence':silence,'fade':fade})
sound('n0073','n0078',0,.002)
sound('n0109','n0110',.25,.003)
sound('n0127','n0155v6a0',0,.004)
sound('n0177','n0195',.18,.002)
sound('n0196','n0203',0,.004)
sound('n0219v6a0','n0219v6a9',0,.004)
sound('n0237','n0248v6a1',0,.002)
sound('n0272','n0274',0,.003)
sound('n0278','n0279',0,.004)
sound('n0304','n0338',0,.003)
sound('n0371','n0380',0,.003)
sound('n0392','n0394',0,.002)
sound('n0408','n0429',.15,.002)
sound('n0456','n0464',.2,.003)
sound('n0483v6a1',end,0,.002)
# Short true silences are reserved, not a constant effect.
sound(after('n0143'),at('n0147'),0,0,True,3)
sound(after('n0202'),at('n0203'),0,0,True,3)
sound(after('n0219v6a6'),at('n0219v6a7'),0,0,True,3)
sound(reveal-24,reveal+15,0,0,True,3)
sound(after('n0487'),end,0,0,True,12)
# Events follow the action or a cue; no horror sting at every cut.
events=[]
def effect(id,kind,offset=0,gain=1):events.append({'frame':at(id)+offset,'kind':kind,'gain':gain})
effect('n0059','wood',30,.8);effect('n0061','wood',32,1)
effect('n0062','wood',70,.6)
effect('n0151','can',12,.65)
effect('n0219v6a5','can',by['n0219v6a5']['duration']+6,.9)
effect('n0245','chair',by['n0245']['duration']-12,.65)
effect('n0313','hum',by['n0313']['duration']+6,.85)
effect('n0314','creak',by['n0314']['duration']+4,.75)
effect('n0340','glass',by['n0340']['duration']-12,.8)
effect('n0367','clap',max(0,by['n0367']['duration']-18),.8)
effect('n0375','mug-drag',by['n0375']['duration']-15,.75)
effect('n0411','glass',35,.6)
effect('n0421','mug-set',by['n0421']['duration']-12,.75)
environmental=[]
for first,offset,sound_file,pan,role in [('n0048a',39,'monkey_call_y_v7.wav',.35,'Y'),('n0048a',90,'monkey_call_m_v7.wav',-.35,'M'),('n0048b',9,'monkey_call_n_v7.wav',0,'narrator')]:
 file='sfx/'+sound_file
 environmental.append({'from':at(first)+offset,'duration':wav_frames(P/'public'/file),'file':file,'rms':.055,'peakLimit':.23,'fadeFrames':2,'pan':pan,'kind':'performed-monkey-imitation','role':role,'overlapNarration':True})
manifest={'version':7,'composition':{'id':'YVillage','width':1280,'height':720,'fps':FPS,'durationInFrames':end},'narration':clips,'captions':captions,'chapters':chapters,'shots':shots,'inserts':inserts,'soundRegions':sound_regions,'environmentalAudio':environmental,'sfx':events,'characterAudio':[growl,early],'glimpseFrame':glimpse,'revealFrame':reveal,'audio':'mix.wav'}
(P/'src/edit-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
def stamp(f):
    ms=round(f/FPS*1000);h,ms=divmod(ms,3600000);mi,ms=divmod(ms,60000);sec,ms=divmod(ms,1000)
    return f'{h:02}:{mi:02}:{sec:02},{ms:03}'
(P.parent/'subtitles_ja.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(c['from'])} --> {stamp(c['to'])}\n{c['text']}" for i,c in enumerate(captions))+'\n')
assert sum('中口' in c['text'] for c in clips)==2
entity_backgrounds=('reveal','asleep','sobaya_clap_v6','sobaya_mug_v6','sobaya_moonlit_v7')
assert glimpse<at('n0208')<reveal
assert all(s['background'] not in entity_backgrounds for s in shots if s['from']<glimpse)
assert all(s['background']=='sobaya_moonlit_v7' for s in shots if s['from']<reveal and s['background'] in entity_backgrounds)
assert all(s['person']!='sobaya_shadow_v4' for s in shots if s['from']>=glimpse)
assert all(s['background'] not in entity_backgrounds and s['person']!='sobaya_shadow_v4' for s in shots if s['view']=='recording')
assert all(len(c['text'].splitlines())<=2 for c in captions)
assert all(a['to']<=b['from'] for a,b in zip(captions,captions[1:]))
assert all(by[r['id']]['duration']/FPS>=r['seconds'] for r in clips)
assert all(not any(e['from']<c['from']+c['duration'] and e['from']+e['duration']>c['from'] for c in clips) for e in [early,growl])
print(json.dumps({'frames':end,'seconds':end/FPS,'revealSeconds':reveal/FPS,'clips':len(clips),'captions':len(captions),'shots':len(shots)},ensure_ascii=False))
