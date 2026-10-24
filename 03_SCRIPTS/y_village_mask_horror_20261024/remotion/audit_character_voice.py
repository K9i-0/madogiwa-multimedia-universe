"""Content screening only; not a replacement for listening/voice-identity review."""
from pathlib import Path
import json, subprocess, hashlib
import numpy as np
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
processor=WhisperProcessor.from_pretrained('openai/whisper-small',cache_dir=ROOT/'.local/hazard_voice/asr-cache')
model=WhisperForConditionalGeneration.from_pretrained('openai/whisper-small',cache_dir=ROOT/'.local/hazard_voice/asr-cache',use_safetensors=True).to('cpu')
torch.set_num_threads(4)
rows=[]
for item in json.loads((P.parent/'character-voice.json').read_text()):
    f=P.parent/item['file']
    data=subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-f','f32le','-ac','1','-ar','16000','-'])
    features=processor(np.frombuffer(data,dtype='<f4'),sampling_rate=16000,return_tensors='pt',return_attention_mask=True)
    with torch.inference_mode(): result=model.generate(**features,language='ja',task='transcribe',max_new_tokens=100)
    recognized=processor.batch_decode(result,skip_special_tokens=True)[0]
    rows.append({'id':item['id'],'expected':item['text'],'recognized':recognized,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
    print(item['id'],recognized,flush=True)
(P.parent/'voice-asr-review.json').write_text(json.dumps({'method':'openai/whisper-small; no expected-text prompt','limitation':'ASR content screening only. Human listening and timbre/acting judgment not performed.','clips':rows},ensure_ascii=False,indent=2)+'\n')
