from pathlib import Path
import json,math,subprocess,re,shutil,hashlib
root=Path.cwd();work=root/'.local/h3-episode82-edit';ep=root/'03_SCRIPTS/82_last_train_police_taxi';public=ep/'remotion/public/h3'
rows=json.loads((work/'generation.json').read_text());override=work/'revisions.json'
if override.exists():
 replacements={r['id']:r for r in json.loads(override.read_text())};rows=[replacements.get(r['id'],r) for r in rows]
assert len(rows)==10
byid={};voice_manifest=[]
for row in rows:
 src=root/row['path'];name=f"line{row['id']}_{row['speaker']}.wav";shutil.copy2(src,public/name)
 dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(src)]))
 log=subprocess.run(['ffmpeg','-hide_banner','-i',str(src),'-af','volumedetect','-f','null','-'],capture_output=True,text=True).stderr
 mean=float(re.search(r'mean_volume: ([-.\d]+)',log)[1]);peak=float(re.search(r'max_volume: ([-.\d]+)',log)[1]);gain=min(-20-mean,-3-peak)
 item=dict(id=row['id'],file='h3/'+name,duration=math.ceil(dur*24),volume=10**(gain/20),text=row['text'])
 byid[row['id']]=item;voice_manifest.append(dict(**row,selected_file='remotion/public/h3/'+name,seconds=dur,gain_db=gain))
# Each picture slice follows the source's speaking/action interval. Dialogue speed stays unchanged.
shots=[];dialogue=[];cursor=0
specs=[('01',1,0,38),('02',1,38,73),('03',1,73,133),('04',1,133,170),('05',1,170,207),('06',1,207,231)]
for idx,ch,start,end in specs:
 d=byid[idx];length=d['duration']+2
 shots.append(dict(file=f'h3/ch{ch}_480p.mp4',sourceStart=start,sourceEnd=end,from_=cursor,duration=length));dialogue.append(dict(d,from_=cursor));cursor+=length
impact=cursor;shots.append(dict(file='h3/ch1_480p.mp4',sourceStart=231,sourceEnd=281,from_=cursor,duration=50));cursor+=50
d=byid['07'];length=d['duration']+2;shots.append(dict(file='h3/ch1_480p.mp4',sourceStart=281,sourceEnd=362,from_=cursor,duration=length));dialogue.append(dict(d,from_=cursor));cursor+=length
cabin=cursor
for idx,start,end in [('08',0,84),('09',84,173)]:
 d=byid[idx];length=d['duration']+3
 shots.append(dict(file='h3/ch2_480p.mp4',sourceStart=start,sourceEnd=end,from_=cursor,duration=length));dialogue.append(dict(d,from_=cursor));cursor+=length
exterior=cursor;d=byid['10'];length=d['duration']+8
shots.append(dict(file='h3/ch2_480p.mp4',sourceStart=308,sourceEnd=362,from_=cursor,duration=length));dialogue.append(dict(d,from_=cursor+2));cursor+=length
for group in [shots,dialogue]:
 for item in group:item['from']=item.pop('from_')
toast=next(d for d in dialogue if d['id']=='03')['from']
record=dict(composition=dict(id='H3LastTrainIrodori',width=1280,height=720,fps=24,durationInFrames=cursor),shots=shots,dialogue=dialogue,effects=[dict(file='h3/clink.wav',from_=toast+14,duration=31,volume=0.35),dict(file='h3/taxi_stop.wav',from_=impact,duration=50,volume=0.65)],siren=dict(from_=cabin,volumeFrames=[0,6,exterior-cabin,exterior-cabin+4,cursor-cabin-6,cursor-cabin],volumes=[0,0.12,0.12,0.18,0.18,0]))
for e in record['effects']:e['from']=e.pop('from_')
record['siren']['from']=record['siren'].pop('from_')
(ep/'remotion/src/h3-edit.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
(work/'selected-voices.json').write_text(json.dumps(voice_manifest,ensure_ascii=False,indent=2)+'\n')
print('Composition',cursor,'frames',cursor/24,'seconds')
