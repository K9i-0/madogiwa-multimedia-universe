"""Independent larger-checkpoint ASR of critical terms and uncertain lines."""
from pathlib import Path
import json,subprocess,time,argparse
import numpy as np,torch
from transformers import WhisperProcessor,WhisperForConditionalGeneration
P=Path(__file__).resolve().parent;R=P.parents[2];torch.set_num_threads(2)
cache=R/'.local/hazard_voice/asr-cache';checkpoint='openai/whisper-large-v3-turbo'
processor=WhisperProcessor.from_pretrained(checkpoint,cache_dir=cache)
model=WhisperForConditionalGeneration.from_pretrained(checkpoint,cache_dir=cache,use_safetensors=True).to(device='cpu',dtype=torch.float32)
report=P/'out/asr_v2.json';out=json.loads(report.read_text())['utterances'] if report.exists() else [];seen={d['audio'] for d in out}
ids={'n000','n006','n010','n021','n024','n026','u008','u028','u030','u046','u053','u065','u067','u068','u069','u075','u080','u083','u089','u092','u099','u104','u107'}
parser=argparse.ArgumentParser();parser.add_argument('--ids',nargs='+');args=parser.parse_args()
if args.ids:ids=set(args.ids)
while True:
 try:rows=json.loads((P/'out/voice_progress_v2.json').read_text())
 except (FileNotFoundError,json.JSONDecodeError):time.sleep(3);continue
 chosen=[d for d in rows if d['id'] in ids]
 for d in chosen:
  if d['audio'] in seen:continue
  raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(P/'public'/d['audio']),'-f','f32le','-ac','1','-ar','16000','-'])
  inputs=processor(np.frombuffer(raw,dtype='<f4').copy(),sampling_rate=16000,return_tensors='pt',return_attention_mask=True)
  with torch.inference_mode():result=model.generate(**inputs,language='ja',task='transcribe',max_new_tokens=220)
  text=processor.batch_decode(result,skip_special_tokens=True)[0]
  out.append({'id':d['id'],'audio':d['audio'],'expected':d['text'],'spoken':d['spoken'],'recognized':text});seen.add(d['audio'])
  report.write_text(json.dumps({'model':checkpoint,'note':'No expected-text prompt; independent ASR screening, not subjective listening.','utterances':out},ensure_ascii=False,indent=2));print(d['id'],text,flush=True)
 if len(chosen)==len(ids) and all(d['audio'] in seen for d in chosen):break
 time.sleep(3)
print('COMPLETE',len(chosen),flush=True)
