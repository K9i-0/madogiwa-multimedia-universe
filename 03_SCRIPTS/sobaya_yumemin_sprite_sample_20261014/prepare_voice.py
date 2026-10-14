from pathlib import Path
import subprocess,json,os,urllib.request,urllib.parse,math,wave
ROOT=Path(__file__).resolve().parents[2]; EP=Path(__file__).resolve().parent; WORK=ROOT/'.local/sobaya-yumemin-sample'
lines=[('yumemin','今日は、そば屋さんと立ち絵のテストみん！','normal'),('sobaya','表情も、ポーズも、ばっちりです！','happy'),('yumemin','でも、なんでビールを持ってるみん？','beer_hold'),('sobaya','解説には、水分補給が大切です！','beer_hold'),('yumemin','それ、水じゃなくてビールみん！','worry'),('sobaya','細かいことは気にせず、乾杯！','beer_cheers'),('yumemin','仕事は、乾杯してからみん！','beer_cheers')]
rows=[];cursor=18
for i,(who,text,pose) in enumerate(lines):
 raw=WORK/f'line{i+1:02}_raw.wav'; adopted=EP/(f'line{i+1:02}_{who}_min.wav' if who=='yumemin' else f'line{i+1:02}_{who}.wav')
 if not adopted.exists():
  if who=='sobaya':
   subprocess.run([str(ROOT/'tools/irodori_speak.sh'),text,str(raw),str(ROOT/'02_CHARACTERS/Sobaya_voice.wav'),'42'],check=True)
   voiced=WORK/f'line{i+1:02}_monster.wav';subprocess.run([str(ROOT/'tools/sobaya_monsterize.sh'),str(raw),str(voiced)],check=True)
  else:
   url='http://127.0.0.1:50021'
   req=urllib.request.Request(url+'/audio_query?'+urllib.parse.urlencode({'text':text,'speaker':3}),data=b'',method='POST')
   q=json.load(urllib.request.urlopen(req));q.update(speedScale=1.15,prePhonemeLength=.09,postPhonemeLength=.12,outputSamplingRate=24000)
   (WORK/f'line{i+1:02}_query.json').write_text(json.dumps(q,ensure_ascii=False,indent=2))
   req=urllib.request.Request(url+'/synthesis?speaker=3',data=json.dumps(q).encode(),headers={'Content-Type':'application/json'},method='POST')
   raw.write_bytes(urllib.request.urlopen(req).read());voiced=raw
  subprocess.run(['ffmpeg','-y','-v','error','-i',str(voiced),'-af','loudnorm=I=-18:TP=-2:LRA=7','-ar','48000','-ac','1',str(adopted)],check=True)
 duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(adopted)]))
 frames=math.ceil(duration*30)
 with wave.open(str(adopted)) as w:
  import array
  a=array.array('h',w.readframes(w.getnframes()));hop=1600
  energy=[min(1,(sum(v*v for v in a[j:j+hop])/max(1,len(a[j:j+hop])))**.5/3500) for j in range(0,len(a),hop)]
 rows.append(dict(who=who,text=text,pose=pose,audio=adopted.name,start=cursor,frames=frames,duration=duration,energy=energy))
 cursor+=frames+12
 (EP/'dialogue.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 print('DONE',i+1,who,duration,flush=True)
manifest={'composition':{'width':1280,'height':720,'fps':30,'durationInFrames':cursor+30},'lines':rows}
(EP/'remotion/src/edit-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
