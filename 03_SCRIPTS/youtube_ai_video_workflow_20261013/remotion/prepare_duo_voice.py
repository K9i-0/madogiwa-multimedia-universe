"""Generate canonical Irodori duo narration with one persistent model runtime."""
from pathlib import Path
from collections import defaultdict
import argparse,hashlib,json,math,os,sys,time,subprocess
import numpy as np
import soundfile as sf
P=Path(__file__).resolve().parent;R=P.parents[2]
sys.path.insert(0,str(R/'.local/Irodori-TTS'))
from irodori_tts.inference_runtime import InferenceRuntime,RuntimeKey,SamplingRequest,download_hf_checkpoint,save_wav
parser=argparse.ArgumentParser();parser.add_argument('--ids',nargs='*');args=parser.parse_args()
rows=json.loads((P/'dialogue.json').read_text());model='Aratako/Irodori-TTS-v4.1-Small'
replacements={'Claude Code':'クロードコード','Codex':'コーデックス','Remotion':'リモーション','Irodori':'イロドリ','Qwen Cloud':'クウェンクラウド','Wan 3.0':'ワン、スリーポイントゼロ','Wan':'ワン','API':'エーピーアイ','AI':'エーアイ','480p':'四百八十ピー','720p':'七百二十ピー','1080p':'千八十ピー','h3':'エイチスリー','福ギュン':'ふくぎゅん','音量や間の調整':'音量や、まの調整','動画生成の分です':'動画生成のぶんです','Web':'ウェブ','〜':'。'}
refs={'yametaro':R/'02_CHARACTERS/Yametaro_voice.wav','takosan':R/'02_CHARACTERS/Takosan_voice.wav'}
refhash={k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in refs.items()}
assert refhash['yametaro']=='ede825a58cf1920f1bdfb353eea17d0feb24f20592d7f36d7c5c22c5ab60530b'
assert refhash['takosan']=='f0663c8e8cebb5c0b700b8399d2ce22c744ca8b8d68ab3b7e0b5ee016c30741c'
revision=subprocess.check_output(['git','-C',str(R/'.local/Irodori-TTS'),'rev-parse','HEAD'],text=True).strip()
(P/'out').mkdir(exist_ok=True);runtime=None;prepared={}
adopted_path=P.parent/'duo_adopted_audio.json'
adopted={d['publicAudio']:d for d in json.loads(adopted_path.read_text())['audio']} if adopted_path.exists() else {}
for row in rows:
 who=row['who'];spoken=row.get('reading',row['text'])
 for src,dst in replacements.items():spoken=spoken.replace(src,dst)
 settings={'model':model,'runtimeRevision':revision,'speaker':who,'reference':str(refs[who].relative_to(R)),'referenceSha256':refhash[who],'seed':row.get('seed',7 if who=='yametaro' else 43),'caption':None,'cfgScaleText':5,'cfgScaleSpeaker':5,'numSteps':40,'durationScale':row.get('durationScale',.7 if who=='yametaro' and len(row['text'])<=25 else 1),'trimTail':False,'postTrim':False,'text':spoken}
 key=hashlib.sha256(json.dumps(settings,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:12]
 name=f"duo_{row['id']}_{who}_{key}.wav";path=P/'public'/name
 if not path.exists() and name in adopted:
  source=P.parent/adopted[name]['file']
  assert hashlib.sha256(source.read_bytes()).hexdigest()==adopted[name]['sha256']
  os.link(source,path)
 if args.ids and row['id'] not in args.ids and not path.exists():continue
 if not path.exists():
  if runtime is None:
   checkpoint=download_hf_checkpoint(model)
   runtime=InferenceRuntime.from_key(RuntimeKey(checkpoint=checkpoint,model_device='mps',codec_device='mps'))
  started=time.monotonic()
  result=runtime.synthesize(SamplingRequest(text=spoken,ref_wav=str(refs[who]),seed=settings['seed'],caption=None,cfg_scale_text=5,duration_scale=settings['durationScale'],trim_tail=False),log_fn=None)
  save_wav(str(path),result.audio,result.sample_rate)
  (P/'out'/f'{name}.json').write_text(json.dumps({'settings':settings,'messages':result.messages,'timings':result.stage_timings},ensure_ascii=False,indent=2))
  print('GENERATED',row['id'],round(time.monotonic()-started,2),flush=True)
 x,sr=sf.read(path);assert x.ndim==1
 frames=math.ceil(len(x)/sr*30);envelope=[]
 for frame in range(frames):
  part=x[round(frame*sr/30):round((frame+1)*sr/30)];envelope.append(round(float(np.sqrt(np.mean(part*part))) if len(part) else 0,5))
 prepared[row['id']]=dict(row,audio=name,spoken=spoken,kana=None,durationInFrames=frames,envelope=envelope,voiceSettings=settings,audioSha256=hashlib.sha256(path.read_bytes()).hexdigest(),sampleRate=sr)
 (P/'out/duo_progress.json').write_text(json.dumps(list(prepared.values()),ensure_ascii=False,indent=2))
 print('READY',row['id'],round(len(x)/sr,3),spoken,flush=True)
if len(prepared)!=len(rows):
 print('PARTIAL',len(prepared),'of',len(rows));sys.exit(0)
clips_after=defaultdict(list)
for c in json.loads((P/'clips_config.json').read_text()):clips_after[c['afterId']].append(c)
cursor=15;out=[];clips=[]
for row in rows:
 d=prepared[row['id']];d['startFrame']=cursor;out.append(d);cursor+=d['durationInFrames']+row.get('pause',12)
 group=clips_after[row['id']]
 for i,c in enumerate(group):
  cursor+=c.get('pauseBeforeFrames',0);clips.append(dict(c,startFrame=cursor));cursor+=c['durationInFrames']+c.get('pauseAfterFrames',15 if i==len(group)-1 else 0)
credits=cursor+30
manifest={'composition':{'width':1280,'height':720,'fps':30,'durationInFrames':credits+240},'mainStartFrame':next(d['startFrame'] for d in out if d['view']=='roadmap'),'endingStartFrame':next(d['startFrame'] for d in out if d['view']=='h3'),'creditsStartFrame':credits,'voiceModel':model,'dialogue':out,'clips':clips}
(P/'src/edit-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(P.parent/'duo_voice_record.json').write_text(json.dumps({'model':model,'generation':'new narration, not voice conversion or an edit to source-video dialogue','subjectiveListening':False,'lines':[{k:v for k,v in d.items() if k not in ('envelope','caption')} for d in out]},ensure_ascii=False,indent=2))
print('DURATION',(credits+240)/30,flush=True)
