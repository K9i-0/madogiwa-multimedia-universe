from pathlib import Path
import json,subprocess,hashlib
import numpy as np
import torch
from transformers import WhisperProcessor,WhisperForConditionalGeneration
p=Path(__file__).resolve().parent
root=p.parent.parent
processor=WhisperProcessor.from_pretrained('openai/whisper-small',cache_dir=root/'.local/hazard_voice/asr-cache')
model=WhisperForConditionalGeneration.from_pretrained('openai/whisper-small',cache_dir=root/'.local/hazard_voice/asr-cache',use_safetensors=True).to('cpu')
torch.set_num_threads(4)
rows=[]
for f in sorted(p.glob('voice_*.wav')):
 data=subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-f','f32le','-ac','1','-ar','16000','-'])
 features=processor(np.frombuffer(data,dtype='<f4'),sampling_rate=16000,return_tensors='pt',return_attention_mask=True)
 with torch.inference_mode(): result=model.generate(**features,language='ja',task='transcribe',max_new_tokens=160)
 text=processor.batch_decode(result,skip_special_tokens=True)[0]
 rows.append({'file':f.name,'recognized':text,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()});print(f.name,text,flush=True)
(p/'audio_audit.json').write_text(json.dumps({'note':'Automated transcript screening only; not listening approval.','clips':rows},ensure_ascii=False,indent=2))
