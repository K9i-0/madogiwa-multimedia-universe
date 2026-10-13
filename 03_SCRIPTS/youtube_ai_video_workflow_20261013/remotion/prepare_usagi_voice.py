"""v4: user-selected VOICEVOX Chugoku Usagi; retain adopted Yametaro audio."""
from pathlib import Path
from collections import defaultdict
import json,hashlib,math,os,urllib.request,urllib.parse,wave
import numpy as np
P=Path(__file__).resolve().parent
rows=json.loads((P/'dialogue.json').read_text())
old={d['id']:d for d in json.loads((P.parent/'duo_voice_record.json').read_text())['lines']}
base='http://127.0.0.1:50021';engine=json.load(urllib.request.urlopen(base+'/version'))
speaker=next(x for x in json.load(urllib.request.urlopen(base+'/speakers')) if x['name']=='中国うさぎ')
def post(path,params,data=None):
 req=urllib.request.Request(base+'/'+path+'?'+urllib.parse.urlencode(params),data=b'' if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method='POST')
 return urllib.request.urlopen(req,timeout=120).read()
prepared=[];queries={}
for row in rows:
 previous=old[row['id']];assert row['text']==previous['text']
 if row['who']=='takosan':
  spoken=previous['spoken'].replace('普段使ってる方なら','普段使ってるかたなら')
  spoken=row.get('voicevoxReading',spoken)
  q=json.loads(post('audio_query',{'speaker':61,'text':spoken}));q.update(speedScale=1.1,pitchScale=-.04,outputSamplingRate=48000,outputStereo=False,prePhonemeLength=.15,postPhonemeLength=.55)
  if row.get('voicevoxClarifyIrai'):
   matches=[a for a in q['accent_phrases'] if ''.join(m['text'] for m in a['moras']).startswith('イライ')]
   assert len(matches)==1
   for mora in matches[0]['moras'][:3]:mora['vowel_length']*=1.3
   matches[0]['moras'][1]['consonant_length']=max(.055,matches[0]['moras'][1]['consonant_length'])
  moras=''.join(x['text'] for a in q['accent_phrases'] for x in a['moras'])
  if row['id']=='u004':assert 'カタナラ' in moras
  settings={'model':'VOICEVOX:中国うさぎ','engineVersion':engine,'speakerVersion':speaker['version'],'style':'ノーマル','speakerId':61,'speedScale':1.1,'pitchScale':-.04,'text':spoken,'query':q}
  key=hashlib.sha256(json.dumps(settings,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:12];name=f'usagi_v4_{row["id"]}_{key}.wav';path=P/'public'/name
  if not path.exists():
   adopted=P.parent/f'usagi_v4_{row["id"]}_takosan.wav';rec=P.parent/'usagi_adopted_audio_v4.json'
   matching=next((d for d in json.loads(rec.read_text())['audio'] if d['publicAudio']==name),None) if rec.exists() else None
   if matching:
    assert hashlib.sha256(adopted.read_bytes()).hexdigest()==matching['sha256'];os.link(adopted,path)
   else:path.write_bytes(post('synthesis',{'speaker':61},q))
  queries[row['id']]={'text':row['text'],'spoken':spoken,'moras':moras,'query':q};kana=q.get('kana')
 else:
  name=previous['audio'];path=P/'public'/name;settings=previous['voiceSettings'];spoken=previous['spoken'];kana=previous.get('kana')
  if not path.exists():os.link(P.parent/f'duo_v3_{row["id"]}_yametaro.wav',path)
  assert hashlib.sha256(path.read_bytes()).hexdigest()==previous['audioSha256']
 with wave.open(str(path)) as w:
  assert w.getnchannels()==1 and w.getsampwidth()==2
  sr=w.getframerate();x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
 frames=math.ceil(len(x)/sr*30)
 envelope=[round(float(np.sqrt(np.mean(z*z))) if len(z) else 0,5) for i in range(frames) for z in [x[round(i*sr/30):round((i+1)*sr/30)]]]
 prepared.append(dict(row,audio=name,spoken=spoken,kana=kana,durationInFrames=frames,envelope=envelope,voiceSettings=settings,audioSha256=hashlib.sha256(path.read_bytes()).hexdigest(),sampleRate=sr))
 (P/'out/usagi_progress.json').write_text(json.dumps(prepared,ensure_ascii=False,indent=2))
 print('READY',row['id'],frames/30,moras if row['who']=='takosan' else 'reused Yametaro',flush=True)
clips_after=defaultdict(list)
for c in json.loads((P/'clips_config.json').read_text()):clips_after[c['afterId']].append(c)
cursor=15;clips=[]
for d in prepared:
 d['startFrame']=cursor;cursor+=d['durationInFrames']+d.get('pause',12)
 group=clips_after[d['id']]
 for i,c in enumerate(group):
  cursor+=c.get('pauseBeforeFrames',0);clips.append(dict(c,startFrame=cursor));cursor+=c['durationInFrames']+c.get('pauseAfterFrames',15 if i==len(group)-1 else 0)
credits=cursor+30
manifest={'composition':{'width':1280,'height':720,'fps':30,'durationInFrames':credits+240},'mainStartFrame':next(d['startFrame'] for d in prepared if d['view']=='roadmap'),'endingStartFrame':next(d['startFrame'] for d in prepared if d['view']=='h3'),'creditsStartFrame':credits,'voiceModel':'Irodori Yametaro + VOICEVOX Chugoku Usagi','dialogue':prepared,'clips':clips}
(P/'src/edit-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(P.parent/'usagi_voice_record_v4.json').write_text(json.dumps({'version':4,'userSelection':'ノーマル・速度1.1倍・音高-0.04','engineVersion':engine,'credit':'VOICEVOX:中国うさぎ','queries':queries,'lines':[{k:v for k,v in d.items() if k not in ('envelope','caption')} for d in prepared]},ensure_ascii=False,indent=2))
print('DURATION',(credits+240)/30,flush=True)
