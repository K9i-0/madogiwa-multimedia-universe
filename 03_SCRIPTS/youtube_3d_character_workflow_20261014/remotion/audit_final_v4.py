from pathlib import Path
import subprocess,json,hashlib
import numpy as np
P=Path(__file__).resolve().parent;f=P.parent/'final_remotion_tripo_workflow_v4.mp4';m=json.loads((P/'src/edit-manifest-v4.json').read_text())
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(f)]))
v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'])==(1280,720,'30/1');assert int(v['nb_read_frames'])==m['composition']['durationInFrames'];assert a['sample_rate']=='48000' and a['channels']==2
subprocess.run(['ffmpeg','-v','error','-i',str(f),'-f','null','-'],check=True)
# Scan every frame for the known repeated green header-band failure.
scan=subprocess.Popen(['ffmpeg','-v','error','-i',str(f),'-vf','scale=160:90','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
count=0;bad=[];black=[]
while True:
 raw=scan.stdout.read(160*90*3)
 if not raw:break
 assert len(raw)==160*90*3
 im=np.frombuffer(raw,dtype=np.uint8).reshape(90,160,3).astype(np.int16)
 green=(np.max(np.abs(im-np.array([24,106,74])),axis=2)<25)
 if green[10:85].mean(axis=1).max()>.8:bad.append(count)
 if (im.max(axis=2)<12).mean()>.98:black.append(count)
 count+=1
assert scan.wait()==0 and count==int(v['nb_read_frames'])
assert not bad,('repeated header band',bad[:20])
assert not black,('black frame',black[:20])
views={}
for d in m['dialogue']:
 if d['view'] not in views:views[d['view']]=d['startFrame']+min(30,d['durationInFrames']-1)
for name in ['sobaya_intro','turn','views','rig','website','remotion','ending']:
 d=next(d for d in m['dialogue'] if d['view']==name)
 views[name+'_cut_before']=max(0,d['startFrame']-1)
 views[name+'_cut_after']=d['startFrame']
for id,offset,name in [('u110',1.8,'hand_cue'),('u110',3.5,'close_cue'),('u096',5.6,'pelvis_cue'),('u068',5.5,'dollar_cue'),('u068',9.0,'yen_cue'),('u102',20.0,'site_held'),('u079',3.0,'face_compare'),('s118',5.0,'game_record'),('u127',1.0,'ending_joke')]:
 d=next(d for d in m['dialogue'] if d['id']==id);views[name]=d['startFrame']+round(offset*30)
for id,offset,name in [('u002',2.0,'opening_reference'),('u008',2.0,'three_way_reference'),('u048',5.0,'resolution_used'),('t050',5.0,'resolution_recommendation'),('u115',2.0,'ar_home_joke'),('r117',1.0,'mobile_apps')]:
 d=next(d for d in m['dialogue'] if d['id']==id);views[name]=d['startFrame']+round(offset*30)
views['ending_last']=m['composition']['durationInFrames']-45
for id,offset,name in [('r027',3.0,'plan_studio'),('r027',7.0,'plan_api'),('r031',6.0,'plans_separate'),('r062',2.0,'human_check'),('s116',2.0,'unity_example'),('u004',1.2,'acting_awkward'),('u007',1.2,'acting_surprise'),('u126',1.2,'acting_bored'),('u127',1.2,'acting_punchline'),('s038',2.0,'analogy_blueprint'),('s046',2.0,'analogy_turn'),('r015',2.0,'analogy_specialists'),('u095',2.0,'analogy_rig'),('u082',1.8,'ten_limbs'),('u083',3.0,'eight_limbs')]:
 d=next(d for d in m['dialogue'] if d['id']==id);views[name]=d['startFrame']+round(offset*30)
out=P/'out/final_frames_v4';out.mkdir(exist_ok=True)
for name,frame in views.items():subprocess.run(['ffmpeg','-v','error','-y','-ss',str(frame/30),'-i',str(f),'-frames:v','1',str(out/f'{name}.jpg')],check=True)
record={'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'videoCodec':v['codec_name'],'audioCodec':a['codec_name'],'videoFrames':int(v['nb_read_frames']),'durationSeconds':int(v['nb_read_frames'])/30,'width':v['width'],'height':v['height'],'fps':30,'audioSampleRate':48000,'audioChannels':2,'fullDecode':'pass','repeatedHeaderBandScan':{'frames':count,'anomalies':bad},'blackFrameScan':{'frames':count,'anomalies':black},'representativeFrames':views,'subjectiveListening':False}
(P.parent/'delivery_v4.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
