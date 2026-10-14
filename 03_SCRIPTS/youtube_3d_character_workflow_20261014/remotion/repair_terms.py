from pathlib import Path
import json,sys,hashlib,math
import numpy as np,soundfile as sf
P=Path(__file__).resolve().parent;R=P.parents[2];sys.path.insert(0,str(R/'.local/Irodori-TTS'))
from irodori_tts.inference_runtime import InferenceRuntime,RuntimeKey,SamplingRequest,download_hf_checkpoint,save_wav
rows=json.loads((P/'out/voice_progress.json').read_text());runtime=InferenceRuntime.from_key(RuntimeKey(checkpoint=download_hf_checkpoint('Aratako/Irodori-TTS-v4.1-Small'),model_device='mps',codec_device='mps'))
for d in rows:
 if d['id'] not in {'u002','u010'}:continue
 settings=dict(d['voiceSettings']);d['spoken']=d['spoken'].replace('ワイもコーデックス','ワイも、コーデックス').replace('契約してるコーデックス','契約してる、コーデックス');settings['seed']=7;settings['durationScale']=.85;settings['text']=d['spoken'];d['seed']=7;d['durationScale']=.85;d['reading']=d['spoken'];d['take']='term_clear'
 name=f"repair_{d['id']}_7_d85.wav";path=P/'public'/name
 if not path.exists():
  result=runtime.synthesize(SamplingRequest(text=d['spoken'],ref_wav=str(R/'02_CHARACTERS/Yametaro_voice.wav'),seed=7,caption=None,cfg_scale_text=5,duration_scale=.85,trim_tail=False),log_fn=None);save_wav(str(path),result.audio,result.sample_rate)
 x,sr=sf.read(path);frames=math.ceil(len(x)/sr*30)
 d.update(audio=name,voiceSettings=settings,durationInFrames=frames,audioSha256=hashlib.sha256(path.read_bytes()).hexdigest(),sampleRate=sr,envelope=[round(float(np.sqrt(np.mean(z*z))) if len(z) else 0,5) for i in range(frames) for z in [x[round(i*sr/30):round((i+1)*sr/30)]]])
 print('REPAIRED',d['id'],len(x)/sr,flush=True)
(P/'out/voice_progress.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
dialogue=json.loads((P/'dialogue.json').read_text())
for d in dialogue:
 if d['id'] in {'u002','u010'}:
  updated=next(x for x in rows if x['id']==d['id']);d.update(seed=7,durationScale=.85,reading=updated['spoken'],take='term_clear')
(P/'dialogue.json').write_text(json.dumps(dialogue,ensure_ascii=False,indent=2))
