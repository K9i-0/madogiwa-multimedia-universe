from pathlib import Path
import json,subprocess,numpy as np,torch
from transformers import WhisperProcessor,WhisperForConditionalGeneration
EP=Path(__file__).resolve().parent;ROOT=EP.parents[1];cache=ROOT/'.local/hazard_voice/asr-cache'
p=WhisperProcessor.from_pretrained('openai/whisper-small',cache_dir=cache);m=WhisperForConditionalGeneration.from_pretrained('openai/whisper-small',cache_dir=cache,use_safetensors=True);torch.set_num_threads(4)
rows=[]
for slug in ['hau','himari','sayo']:
 for r in json.loads((EP/f'remotion/src/manifest_{slug}.json').read_text())['lines']:
  if r['who']=='yumemin': rows.append(dict(r,variant=slug))
for r in rows:
 b=subprocess.check_output(['ffmpeg','-v','error','-i',str(EP/'remotion/public'/r['audio']),'-f','f32le','-ac','1','-ar','16000','-']);f=p(np.frombuffer(b,dtype='<f4'),sampling_rate=16000,return_tensors='pt',return_attention_mask=True)
 with torch.inference_mode():ids=m.generate(**f,language='ja',task='transcribe',max_new_tokens=160)
 r['recognized']=p.batch_decode(ids,skip_special_tokens=True)[0];r.pop('energy',None);print(r['audio'],r['recognized'],flush=True)
(EP/'asr_variants.json').write_text(json.dumps({'note':'Automated screening only; not listening verification','lines':rows},ensure_ascii=False,indent=2))
