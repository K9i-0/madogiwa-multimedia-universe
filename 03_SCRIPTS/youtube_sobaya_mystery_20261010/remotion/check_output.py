from pathlib import Path
import subprocess,json,wave,hashlib
import numpy as np
P=Path(__file__).resolve().parent;m=json.loads((P/'src/edit-manifest.json').read_text());r=[]
last=0
for d in m['dialogue']:
 if '霜重' in d['text']:
  assert 'シモジュウ' in d['kana'].replace("'",'').replace('/',''),d['kana']
 assert d['startFrame']>=last
 assert len(d['caption'].splitlines())<=2
 assert max(map(len,d['caption'].splitlines()))<=38
 with wave.open(str(P/'public'/d['audio'])) as w:
  assert w.getframerate()==24000
  a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16)
  assert len(a)>1000 and np.max(np.abs(a.astype(float)))>100
  assert abs(len(a)/24000-d['durationInFrames']/30)<1/30+.001
 last=d['startFrame']+d['durationInFrames']
 r.append({'startFrame':d['startFrame'],'durationInFrames':d['durationInFrames'],'audio':d['audio'],'sha256':hashlib.sha256((P/'public'/d['audio']).read_bytes()).hexdigest()})
reveal=next(d['startFrame'] for d in m['dialogue'] if d['view']=='employee')
for d in m['dialogue']:
 if d['startFrame']<reveal:
  assert 'そば屋' not in d['text'] and 'クローン' not in d['text'] and 'ビール' not in d['text'],d['text']
assert sum('ラピュタ' in d['text'] for d in m['dialogue'])==1
assert not any(d['view']=='movie_evidence' or 'E.T.' in d['text'] for d in m['dialogue'])
report={'fictionReferenceValidation':'pass: one Laputa reference', 'voiceFiles':len(r),'durationSeconds':m['composition']['durationInFrames']/30,'captionAndTimelineValidation':'pass','voices':r,'listeningAudit':'Not performed; technical checks do not establish listening quality'}
f=P.parent/'final_remotion_sobaya_mystery_v6.mp4'
if f.exists():
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(f)]))
 v=next(x for x in probe['streams'] if x['codec_type']=='video');a=next(x for x in probe['streams'] if x['codec_type']=='audio')
 assert (v['width'],v['height'],v['r_frame_rate'])==(1280,720,'30/1')
 assert int(v['nb_read_frames'])==m['composition']['durationInFrames'];assert a['sample_rate']=='48000'
 subprocess.run(['ffmpeg','-v','error','-i',str(f),'-f','null','-'],check=True)
 report.update(finalProbe=probe,fullDecode='pass',frameCount='pass')
(P.parent/'qa_record.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print({k:v for k,v in report.items() if k not in ['voices','finalProbe']})
