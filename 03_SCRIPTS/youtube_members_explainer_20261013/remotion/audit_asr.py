from pathlib import Path
import json,subprocess,numpy as np,torch
from transformers import WhisperProcessor,WhisperForConditionalGeneration
P=Path(__file__).resolve().parent;R=P.parents[2];torch.set_num_threads(4)
p=WhisperProcessor.from_pretrained('openai/whisper-small',cache_dir=R/'.local/hazard_voice/asr-cache',local_files_only=True)
m=WhisperForConditionalGeneration.from_pretrained('openai/whisper-small',cache_dir=R/'.local/hazard_voice/asr-cache',use_safetensors=True,local_files_only=True).to('cpu');rows=[]
for name,c in json.loads((P/'clips.json').read_text()).items():
 data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(c['sourceStartFrame']/30),'-i',str(P/'public'/c['src']),'-t',str(c['durationInFrames']/30),'-f','f32le','-ac','1','-ar','16000','-'])
 features=p(np.frombuffer(data,dtype='<f4').copy(),sampling_rate=16000,return_tensors='pt',return_attention_mask=True)
 with torch.inference_mode():r=m.generate(**features,language='ja',task='transcribe',max_new_tokens=220)
 text=p.batch_decode(r,skip_special_tokens=True)[0];rows.append({'id':name,'text':text});print(name,text,flush=True)
(P/'out/clips_asr.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
