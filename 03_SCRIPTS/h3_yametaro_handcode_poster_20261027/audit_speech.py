"""ASR screening in short overlapping windows; full ASR can suppress repeats."""
from pathlib import Path
import json,subprocess,sys
import numpy as np,torch
from transformers import WhisperProcessor,WhisperForConditionalGeneration
P=Path(__file__).resolve().parent;R=P.parents[1];cache=R/'.local/hazard_voice/asr-cache'
p=WhisperProcessor.from_pretrained('openai/whisper-small',cache_dir=cache,local_files_only=True)
m=WhisperForConditionalGeneration.from_pretrained('openai/whisper-small',cache_dir=cache,local_files_only=True,use_safetensors=True).to('cpu');torch.set_num_threads(4)
rows=[]
for name in sys.argv[1:]:
 path=Path(name);audio=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-f','f32le','-ac','1','-ar','16000','-']),dtype='<f4').copy();duration=len(audio)/16000
 ranges=[(0,duration)]+[(max(0,t-0.25),min(duration,t+4.25)) for t in range(0,int(duration),4)]
 parts=[]
 for start,end in ranges:
  f=p(audio[int(start*16000):int(end*16000)],sampling_rate=16000,return_tensors='pt',return_attention_mask=True)
  with torch.inference_mode():out=m.generate(**f,language='ja',task='transcribe',max_new_tokens=180)
  text=p.batch_decode(out,skip_special_tokens=True)[0];parts.append({'start':start,'end':end,'text':text});print(path.name,start,end,text,flush=True)
 rows.append({'file':path.name,'windows':parts})
(P/'generated/speech-audit.json').write_text(json.dumps({'model':'openai/whisper-small','note':'ASR only; overlapping boundary words are not necessarily repetition. No direct listening or lipsync audit.','clips':rows},ensure_ascii=False,indent=2)+'\n')
