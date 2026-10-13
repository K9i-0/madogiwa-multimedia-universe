from pathlib import Path
import json,subprocess,hashlib,unicodedata,difflib
import numpy as np,torch
from transformers import WhisperProcessor,WhisperForConditionalGeneration
P=Path(__file__).resolve().parent;R=P.parents[2];cache=R/'.local/hazard_voice/asr-cache'
torch.set_num_threads(2)
processor=WhisperProcessor.from_pretrained('openai/whisper-small',cache_dir=cache)
model=WhisperForConditionalGeneration.from_pretrained('openai/whisper-small',cache_dir=cache,use_safetensors=True).to('cpu')
m=json.loads((P/'src/edit-manifest.json').read_text());report=P/'out/asr.json';out=[]
old={x['audio']:x for x in json.loads(report.read_text())['utterances']} if report.exists() else {}
for i,d in enumerate(m['dialogue']):
 if d['audio'] in old:out.append(old[d['audio']]);continue
 data=subprocess.check_output(['ffmpeg','-v','error','-i',str(P/'public'/d['audio']),'-f','f32le','-ac','1','-ar','16000','-'])
 features=processor(np.frombuffer(data,dtype='<f4').copy(),sampling_rate=16000,return_tensors='pt',return_attention_mask=True)
 with torch.inference_mode():result=model.generate(**features,language='ja',task='transcribe',max_new_tokens=180)
 text=processor.batch_decode(result,skip_special_tokens=True)[0]
 row=dict(index=i,audio=d['audio'],expected=d['text'],spoken=d['spoken'],recognized=text,kana=d['kana']);out.append(row)
 report.write_text(json.dumps({'model':'openai/whisper-small','note':'Automated transcript screening, not perceptual listening. No expected-text prompt.','utterances':out},ensure_ascii=False,indent=2))
 print(i,text,flush=True)
# Preserve cached rows after the last changed utterance as well.
report.write_text(json.dumps({'model':'openai/whisper-small','note':'Automated transcript screening, not perceptual listening. No expected-text prompt.','utterances':out},ensure_ascii=False,indent=2))
