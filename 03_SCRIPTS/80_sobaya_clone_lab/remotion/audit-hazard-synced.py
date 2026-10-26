from pathlib import Path
import json,subprocess,re,hashlib
r=Path(__file__).resolve().parent;m=json.loads((r/'src/aura-hazard-synced.json').read_text());f=r.parent/m['output'];n=m['composition']['durationInFrames']
d=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_format','-show_streams','-of','json',str(f)]));v=next(s for s in d['streams'] if s['codec_type']=='video');a=next(s for s in d['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_read_frames']))==(720,1280,'30/1',n)
assert abs(float(d['format']['duration'])-34)<.05
assert a['sample_rate']=='48000'
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(f),'-f','null','-'],check=True)
measure=subprocess.run(['ffmpeg','-hide_banner','-i',str(f),'-af','loudnorm=I=-14:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
stats=json.loads(re.findall(r'\{\s*"input_i".*?\}',measure.stderr,re.S)[-1]);assert float(stats['input_tp'])<0
ranges={}
for shot in m['segments']:
 if not shot['file']: continue
 for a,b in ranges.get(shot['file'],[]):
  assert shot['sourceStart']>=b or shot['sourceEnd']<=a, f'Unexpected reused range: {shot}'
 ranges.setdefault(shot['file'],[]).append((shot['sourceStart'],shot['sourceEnd']))
errors=[]
for shot in m['segments'][1:]:
 beat=min(m['music']['measuredAttackSeconds'],key=lambda t:abs(t-(22+shot['fromFrame']/30)))
 delta=(22+shot['fromFrame']/30)-beat
 assert abs(delta)<=1/60+.0001,(shot['id'],delta)
 errors.append({'event':shot['id'],'frame':shot['fromFrame'],'musicAttackSeconds':beat,'errorMs':round(delta*1000,2)})
q={'cutAlignment':errors,'musicRangeSeconds':[22,56],'shatterSourceFrame':762,'shatterOutputFrame':725,'noRepeatedPrimaryVideoRanges':True,'output':f.name,'sha256':hashlib.file_digest(f.open('rb'),'sha256').hexdigest(),'durationSeconds':34,'frames':n,'width':720,'height':1280,'fps':30,'fullDecode':'passed','typecheck':'passed','representativeFrameReview':True,'subjectiveFullPlaybackAudition':False,'audioPolicy':'Only specified REVENGE music; all source-video audio muted and not mapped','loudnessLUFS':float(stats['input_i']),'truePeakDbTP':float(stats['input_tp']),'dialogueCaptions':False,'texts':['SOBAYA HAZARD','BIO-SIGNATURE SCAN','YAMETARO','FUKUGYUN','ANOMALY DETECTED','RETRIEVAL AUTHORIZED']}
(r.parent/'aura_phonk_prep_20261026/hazard-synced-qa.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print(json.dumps(q,ensure_ascii=False,indent=2))
