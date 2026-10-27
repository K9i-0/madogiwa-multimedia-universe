from pathlib import Path
import json,math,subprocess,shutil,hashlib
import numpy as np
r=Path(__file__).resolve().parent;ep=r.parent;root=ep.parent.parent;work=root/'.local/yumemi_evolution_20261026/sobaya';pub=r/'public/sobaya';pub.mkdir(exist_ok=True)
template=root/'03_SCRIPTS/00_TEMPLATES/characters/commentary_sobaya_v2'
for name in ['sobaya_normal.png','sobaya_normal_talk.png']:shutil.copy2(template/name,pub/name)
anchors={l['id']:l for l in json.loads((r/'src/solo-manifest.json').read_text())['lines']}
texts=json.loads((work/'lines.json').read_text());result=[];cursor=3;records=[]
for i,text in enumerate(texts,1):
 a=dict(anchors[f'a{i}']);a['startFrame']=cursor;a['endFrame']=cursor+a['durationInFrames'];result.append(a)
 src=work/f's{i}.wav';dst=ep/f'sobaya_line{i}.wav';shutil.copy2(src,dst);shutil.copy2(src,pub/src.name)
 d=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(src),'-f','f32le','-ac','1','-ar','48000','-']),dtype='<f4')
 energy=np.array([np.sqrt(np.mean(x*x)) for x in np.array_split(d,math.ceil(len(d)/480))]);active=np.where(energy>.008)[0]
 trim=math.floor(max(0,active[0]*.01-.035)*30);end=math.ceil(min(len(d)/48000,(active[-1]+1)*.01+.055)*30);dur=end-trim;start=a['endFrame']-5
 crop=d[trim*1600:min(len(d),end*1600)];rms=float(np.sqrt(np.mean(crop*crop)));volume=min(.1/max(rms,.001),.88/max(float(np.max(np.abs(crop))),.001))
 env=[float(np.sqrt(np.mean(crop[j:j+1600]**2))) for j in range(0,len(crop),1600)];peak=max(env)
 result.append(dict(id=f's{i}',speaker='sobaya',text=text,reading=text,file=f'sobaya/s{i}.wav',startFrame=start,endFrame=start+dur,durationInFrames=dur,trimBefore=trim,volume=volume,envelope=[round(v/peak,3) for v in env]));cursor=start+dur-1
 records.append(dict(id=f's{i}',text=text,model='Aratako/Irodori-TTS-v4-Large',reference='02_CHARACTERS/Sobaya_voice.wav',referenceSha256=hashlib.sha256((root/'02_CHARACTERS/Sobaya_voice.wav').read_bytes()).hexdigest(),seed=42,caption='食い気味に、勢いよくツッコむ。',cfgText=3,durationScale=1,uncut=False,postprocess='tools/sobaya_monsterize.sh',durationSeconds=len(d)/48000,sha256=hashlib.sha256(src.read_bytes()).hexdigest()))
total=result[-1]['endFrame']+10;by={l['id']:l for l in result};bounds=[0]+[by[f'a{i}']['startFrame'] for i in range(2,5)]+[total];source=[0,153,249,369,465]
scenes=[dict(startFrame=bounds[i],durationInFrames=bounds[i+1]-bounds[i],sourceStartFrame=source[i],sourceEndFrame=source[i+1],playbackRate=(source[i+1]-source[i])/(bounds[i+1]-bounds[i])) for i in range(4)]
(r/'src/sobaya-manifest.json').write_text(json.dumps(dict(durationInFrames=total,fps=30,lines=result,scenes=scenes),ensure_ascii=False,indent=2)+'\n');(ep/'sobaya-generation.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print('duration',total/30)
