"""Screen each newly generated Irodori line while synthesis continues."""
from pathlib import Path
import json,subprocess,time,unicodedata,difflib
import numpy as np,torch
from transformers import WhisperProcessor,WhisperForConditionalGeneration
P=Path(__file__).resolve().parent;R=P.parents[2];torch.set_num_threads(2)
cache=R/'.local/hazard_voice/asr-cache'
processor=WhisperProcessor.from_pretrained('openai/whisper-small',cache_dir=cache,local_files_only=True)
model=WhisperForConditionalGeneration.from_pretrained('openai/whisper-small',cache_dir=cache,use_safetensors=True,local_files_only=True).to('cpu')
report=P/'out/asr_duo_v3.json';out=json.loads(report.read_text())['utterances'] if report.exists() else []
seen={r['audio'] for r in out};count=len(json.loads((P/'dialogue.json').read_text()))
def norm(t):return ''.join(c for c in unicodedata.normalize('NFKC',t) if c.isalnum())
while True:
 try:rows=json.loads((P/'out/duo_progress.json').read_text())
 except (FileNotFoundError,json.JSONDecodeError):time.sleep(3);continue
 for d in rows:
  if d['audio'] in seen:continue
  raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(P/'public'/d['audio']),'-f','f32le','-ac','1','-ar','16000','-'])
  inputs=processor(np.frombuffer(raw,dtype='<f4').copy(),sampling_rate=16000,return_tensors='pt',return_attention_mask=True)
  with torch.inference_mode():generated=model.generate(**inputs,language='ja',task='transcribe',max_new_tokens=220)
  text=processor.batch_decode(generated,skip_special_tokens=True)[0]
  row={'id':d['id'],'audio':d['audio'],'expected':d['text'],'spoken':d['spoken'],'recognized':text,'similarity':round(difflib.SequenceMatcher(None,norm(d['spoken']),norm(text)).ratio(),3),'durationSeconds':d['durationInFrames']/30}
  out.append(row);seen.add(d['audio']);report.write_text(json.dumps({'model':'openai/whisper-small','note':'No expected-text prompt; automated screening, not subjective listening.','utterances':out},ensure_ascii=False,indent=2))
  print(d['id'],text,flush=True)
 if len(rows)==count and all(d['audio'] in seen for d in rows):break
 time.sleep(3)
print('COMPLETE',len(rows),flush=True)
