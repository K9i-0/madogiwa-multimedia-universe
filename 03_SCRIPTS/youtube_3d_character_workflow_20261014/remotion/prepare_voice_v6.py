"""v6 narration: text-hash reuse, canonical Yametaro and normal Usagi."""
from pathlib import Path
from collections import defaultdict
import json,hashlib,math,os,sys,subprocess,urllib.request,urllib.parse
import numpy as np
import soundfile as sf
P=Path(__file__).resolve().parent;R=P.parents[2]
sys.path.insert(0,str(R/'.local/Irodori-TTS'))
from irodori_tts.inference_runtime import InferenceRuntime,RuntimeKey,SamplingRequest,download_hf_checkpoint,save_wav
rows=json.loads((P/'dialogue-v6.json').read_text());old_y={}
previous={d['id']:d for d in json.loads((P/'src/edit-manifest-v5.json').read_text())['dialogue']}
for requested in rows:
 if requested.get('reuseFrom')=='v5':
  assert (requested['text'],requested['who'])==(previous[requested['id']]['text'],previous[requested['id']]['who']), f"Remove reuseFrom to regenerate {requested['id']}"
rows=[dict(previous[d['id']],**d,reuseAudio=True) if d.get('reuseFrom')=='v5' else d for d in rows]
base='http://127.0.0.1:50021';engine=json.load(urllib.request.urlopen(base+'/version'))
speaker=next(x for x in json.load(urllib.request.urlopen(base+'/speakers')) if x['name']=='中国うさぎ')
ref=R/'02_CHARACTERS/Yametaro_voice.wav';refhash=hashlib.sha256(ref.read_bytes()).hexdigest()
assert refhash=='ede825a58cf1920f1bdfb353eea17d0feb24f20592d7f36d7c5c22c5ab60530b'
revision=subprocess.check_output(['git','-C',str(R/'.local/Irodori-TTS'),'rev-parse','HEAD'],text=True).strip()
replacements={'Unity':'ユニティ','Tripo':'トリポ','Three.js':'スリージェイエス','Blender':'ブレンダー','Cursor':'カーソル','Flutter Scene':'フラッターシーン','Flutter':'フラッター','Studio':'スタジオ','Python':'パイソン','3D':'スリーディー','AR':'エーアール','JSON':'ジェイソン','Claude Code':'クロードコード','Codex':'コーデックス','Remotion':'リモーション','Irodori':'イロドリ','Qwen Cloud':'クウェンクラウド','Wan 3.0':'ワン、サンテンゼロ','Wan':'ワン','API':'エーピーアイ','AI':'エーアイ','480p':'四百八十ピー','720p':'七百二十ピー','1080p':'千八十ピー','H3':'エイチスリー','h3':'エイチスリー','TikTok':'ティックトック','ByteDance':'バイトダンス','Seedance':'シーダンス','Alibaba':'アリババ','MiniMax':'ミニマックス','Higgsfield':'ヒッグスフィールド','React':'リアクト','GitHub':'ギットハブ','Git':'ギット','GPU':'ジーピーユー','Colab':'コラボ','IT':'アイティー','100%':'ひゃくパーセント','福ギュン':'ふくぎゅん','Web':'ウェブ','〜':'。','動画生成の分です':'動画生成のぶんです','その分':'そのぶん','全身のほう':'全身のほう','音量や間の調整':'音量や、まの調整','次の一本':'次のいっぽん','一本ずつ':'いっぽんずつ'}
def post(path,params,data=None):
 req=urllib.request.Request(base+'/'+path+'?'+urllib.parse.urlencode(params),data=b'' if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method='POST')
 return urllib.request.urlopen(req,timeout=120).read()
prepared=[];runtime=None
for row in rows:
 spoken=row.get('voicevoxReading',row.get('reading',row['text']))
 for a,b in replacements.items():spoken=spoken.replace(a,b)
 kana=None
 if row.get('reuseAudio'):
  name=row['audio'];path=P/'public'/name;settings=row['voiceSettings'];spoken=row['spoken'];kana=row.get('kana')
  assert hashlib.sha256(path.read_bytes()).hexdigest()==row['audioSha256']
 elif row['who']=='takosan':
  q=json.loads(post('audio_query',{'speaker':61,'text':spoken}))
  q.update(speedScale=1.1,pitchScale=0,intonationScale=1,volumeScale=1,outputSamplingRate=48000,outputStereo=False,prePhonemeLength=.10,postPhonemeLength=.20)
  settings={'model':'VOICEVOX:中国うさぎ','engineVersion':engine,'speakerVersion':speaker['version'],'speakerId':61,'style':'ノーマル','query':q,'text':spoken}
  key=hashlib.sha256(json.dumps(settings,ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:12]
  name=f'v7_{row["id"]}_{key}.wav'
  if not (P/'public'/name).exists():name=f'v8_{row["id"]}_{key}.wav'
  if not (P/'public'/name).exists():name=f'v9_{row["id"]}_{key}.wav'
  if not (P/'public'/name).exists():name=f'v10_{row["id"]}_{key}.wav'
  if not (P/'public'/name).exists():name=f'v6_{row["id"]}_{key}.wav'
  path=P/'public'/name;kana=q.get('kana')
  if not path.exists():path.write_bytes(post('synthesis',{'speaker':61},q))
 elif row['text'] in old_y and 'seed' not in row:
  prev=old_y[row['text']];name=prev['audio'];path=P/'public'/name;settings=prev['voiceSettings'];spoken=prev['spoken']
  if not path.exists():raise FileNotFoundError(path)
  assert hashlib.sha256(path.read_bytes()).hexdigest()==prev['audioSha256']
 else:
  settings={'model':'Aratako/Irodori-TTS-v4.1-Small','runtimeRevision':revision,'reference':str(ref.relative_to(R)),'referenceSha256':refhash,'seed':row.get('seed',7),'caption':None,'cfgScaleText':5,'cfgScaleSpeaker':5,'numSteps':40,'durationScale':row.get('durationScale',.7),'trimTail':False,'postTrim':False,'text':spoken}
  key=hashlib.sha256(json.dumps(settings,ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:12]
  name=f'v7_{row["id"]}_{key}.wav'
  if not (P/'public'/name).exists():name=f'v8_{row["id"]}_{key}.wav'
  if not (P/'public'/name).exists():name=f'v9_{row["id"]}_{key}.wav'
  if not (P/'public'/name).exists():name=f'v10_{row["id"]}_{key}.wav'
  if not (P/'public'/name).exists():name=f'v6_{row["id"]}_{key}.wav'
  path=P/'public'/name
  if not path.exists():
   if runtime is None:runtime=InferenceRuntime.from_key(RuntimeKey(checkpoint=download_hf_checkpoint(settings['model']),model_device='mps',codec_device='mps'))
   result=runtime.synthesize(SamplingRequest(text=spoken,ref_wav=str(ref),seed=settings['seed'],caption=None,cfg_scale_text=5,duration_scale=settings['durationScale'],trim_tail=False),log_fn=None)
   save_wav(str(path),result.audio,result.sample_rate)
   (P/'out'/f'{name}.json').write_text(json.dumps({'settings':settings,'messages':result.messages,'timings':result.stage_timings},ensure_ascii=False,indent=2))
 x,sr=sf.read(path);assert x.ndim==1
 frames=math.ceil(len(x)/sr*30)
 envelope=[round(float(np.sqrt(np.mean(z*z))) if len(z) else 0,5) for i in range(frames) for z in [x[round(i*sr/30):round((i+1)*sr/30)]]]
 prepared.append(dict(row,audio=name,spoken=spoken,kana=kana,durationInFrames=frames,envelope=envelope,voiceSettings=settings,audioSha256=hashlib.sha256(path.read_bytes()).hexdigest(),sampleRate=sr))
 temp=P/'out/voice_progress_v6.tmp';temp.write_text(json.dumps(prepared,ensure_ascii=False,indent=2));temp.replace(P/'out/voice_progress_v6.json')
 print('READY',len(prepared),len(rows),row['id'],round(len(x)/sr,2),spoken,flush=True)
cursor=60
for d in prepared:
 d['startFrame']=cursor;cursor+=d['durationInFrames']+d.get('pause',12)
end=cursor+75
manifest={'composition':{'width':1280,'height':720,'fps':30,'durationInFrames':end},'mainStartFrame':next(d['startFrame'] for d in prepared if d['chapter'].startswith('2.')),'endingStartFrame':next(d['startFrame'] for d in prepared if d['chapter'].startswith('8.')),'creditsInDescription':True,'voiceModel':'Irodori Yametaro + VOICEVOX Chugoku Usagi','dialogue':prepared,'clips':[]}
(P/'src/edit-manifest-v6.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(P.parent/'voice_record_v6.json').write_text(json.dumps({'version':6,'subjectiveListening':False,'lines':[{k:v for k,v in d.items() if k!='envelope'} for d in prepared]},ensure_ascii=False,indent=2)+'\n')
print('COMPLETE',end/30,flush=True)
