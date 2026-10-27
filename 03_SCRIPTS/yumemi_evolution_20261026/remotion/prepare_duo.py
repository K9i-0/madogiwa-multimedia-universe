from pathlib import Path
import json,math,wave,subprocess,shutil
import numpy as np
r=Path(__file__).resolve().parent;ep=r.parent;root=ep.parent.parent;work=root/'.local/yumemi_evolution_20261026/duo';pub=r/'public/duo';pub.mkdir(exist_ok=True)
template=root/'03_SCRIPTS/00_TEMPLATES/characters'
assets=[(template/'commentary_base_20261014/yumemin_base_v1.png','yumemin.png')]
assets += [(template/'commentary_duo_v1/exports'/f'yametaro_{m}_{s}.png',f'yametaro_{m}_{s}.png') for m in ['normal','bored','worry','surprise','angry'] for s in ['closed','open']]
for src,name in assets:
 if not (pub/name).exists():shutil.copy2(src,pub/name)
rows=json.loads((work/'lines.json').read_text());result=[];previousEnd=0
captions={'a1':'進化を続ける、ゆめみ。\n公式のアカウントが率先して、大喜利を展開。','a2':'さらに、社員がタレントになる\n芸能事務所、ゆめプロへ。','a3':'派生した窓際族は、AIドラマを制作。\nグッズ販売にまで進出しています。'}
for id,speaker,text,reading in rows:
 src=work/f'{id}.wav'; dst=ep/f'duo_{id}_{speaker}.wav';shutil.copy2(src,dst);shutil.copy2(src,pub/src.name)
 data=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(src),'-f','f32le','-ac','1','-ar','48000','-']),dtype='<f4')
 energy=np.array([np.sqrt(np.mean(x*x)) for x in np.array_split(data,math.ceil(len(data)/480))]);active=np.where(energy>0.008)[0]
 onset=max(0,active[0]*.01-.035);offset=min(len(data)/48000,(active[-1]+1)*.01+.055)
 trim=math.floor(onset*30);dur=math.ceil(offset*30)-trim
 # Start the retort 3 frames before the end of voiced narration, not before trailing silence.
 start=3 if not result else previousEnd-(5 if speaker=='yametaro' else 1)
 end=start+dur;previousEnd=end
 crop=data[trim*1600:min(len(data),(trim+dur)*1600)]
 rms=float(np.sqrt(np.mean(crop*crop)));volume=min(.1/max(rms,.001),.88/max(float(np.max(np.abs(crop))),.001))
 env=[float(np.sqrt(np.mean(crop[i:i+1600]**2))) for i in range(0,len(crop),1600)];peak=max(env)
 result.append(dict(id=id,speaker=speaker,text=text,reading=reading,caption=captions.get(id,text),file=f'duo/{id}.wav',startFrame=start,endFrame=end,durationInFrames=dur,trimBefore=trim,volume=round(volume,5),envelope=[round(v/peak,3) for v in env],mood={'y1':'bored','y2':'worry','y3':'surprise','y4':'angry'}.get(id,'normal')))
by={l['id']:l for l in result};total=previousEnd+10
# Scene blocks follow the dialogue. Retain the complete source timeline, including transitions.
scenes=[]
for start,end,srcstart,srcend in [(0,by['a2']['startFrame'],0,153),(by['a2']['startFrame'],by['a3']['startFrame'],153,249),(by['a3']['startFrame'],by['a4']['startFrame'],249,369),(by['a4']['startFrame'],total,369,465)]:
 scenes.append(dict(startFrame=start,durationInFrames=end-start,sourceStartFrame=srcstart,sourceEndFrame=srcend,playbackRate=(srcend-srcstart)/(end-start)))
m=dict(durationInFrames=total,fps=30,lines=result,scenes=scenes)
(r/'src/duo-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'durationSeconds':total/30,'lines':[{k:l[k] for k in ['id','startFrame','endFrame','trimBefore','text']} for l in result],'scenes':scenes},ensure_ascii=False,indent=2))
