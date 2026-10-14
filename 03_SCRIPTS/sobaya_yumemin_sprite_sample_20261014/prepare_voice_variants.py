from pathlib import Path
import json,urllib.request,urllib.parse,subprocess,math,wave,array,hashlib,os
EP=Path(__file__).resolve().parent;ROOT=EP.parents[1];WORK=ROOT/'.local/sobaya-yumemin-sample/voice-variants';WORK.mkdir(parents=True,exist_ok=True)
base=json.loads((EP/'remotion/src/edit-manifest.json').read_text());variants=[('hau','雨晴はう',10),('himari','冥鳴ひまり',14),('sayo','小夜/SAYO',46)]
records=[]
for slug,name,speaker in variants:
 rows=[];cursor=18
 for i,original in enumerate(base['lines']):
  row=dict(original)
  if row['who']=='yumemin':
   text=row['text'];filename=f'line{i+1:02}_yumemin_{slug}.wav';audio=WORK/filename
   settings={'text':text,'speaker':speaker,'engine':'0.25.1','speedScale':1.15,'pitchScale':0,'intonationScale':1,'prePhonemeLength':.09,'postPhonemeLength':.12,'outputSamplingRate':24000}
   key=hashlib.sha256(json.dumps(settings,sort_keys=True,ensure_ascii=False).encode()).hexdigest();meta=WORK/f'{filename}.json'
   if not audio.exists() or not meta.exists() or json.loads(meta.read_text()).get('cacheKey')!=key:
    req=urllib.request.Request('http://127.0.0.1:50021/audio_query?'+urllib.parse.urlencode({'text':text,'speaker':speaker}),data=b'',method='POST')
    q=json.load(urllib.request.urlopen(req));q.update({k:v for k,v in settings.items() if k not in ['text','speaker','engine']})
    req=urllib.request.Request(f'http://127.0.0.1:50021/synthesis?speaker={speaker}',data=json.dumps(q).encode(),headers={'Content-Type':'application/json'},method='POST')
    raw=WORK/f'{filename}.raw.wav';raw.write_bytes(urllib.request.urlopen(req).read())
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(raw),'-af','loudnorm=I=-18:TP=-2:LRA=7','-ar','48000','-ac','1',str(audio)],check=True)
    meta.write_text(json.dumps({'cacheKey':key,'settings':settings,'query':q},ensure_ascii=False,indent=2))
   dst=EP/'remotion/public'/filename
   if dst.exists():dst.unlink()
   os.link(audio,dst)
   duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(audio)]))
   with wave.open(str(audio)) as w:a=array.array('h',w.readframes(w.getnframes()))
   energy=[min(1,(sum(v*v for v in a[j:j+1600])/max(1,len(a[j:j+1600])))**.5/3500) for j in range(0,len(a),1600)]
   row.update(audio=filename,duration=duration,frames=math.ceil(duration*30),energy=energy)
  row['start']=cursor;cursor+=row['frames']+12;rows.append(row)
 manifest={'composition':{**base['composition'],'durationInFrames':cursor+30},'lines':rows}
 (EP/f'remotion/src/manifest_{slug}.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 records.append({'id':slug,'name':name,'speaker':speaker,'frames':cursor+30,'speedScale':1.15,'pitchScale':0,'intonationScale':1,'loudness':'-18 LUFS','voicevox':'0.25.1','audioDirectory':str(WORK),'credit':f'VOICEVOX:{name}'})
 print(name,(cursor+30)/30,'seconds',flush=True)
(EP/'voice_variants.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
