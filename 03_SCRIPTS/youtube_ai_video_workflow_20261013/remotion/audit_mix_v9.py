from pathlib import Path
import json,subprocess,numpy as np,torch
from transformers import WhisperProcessor,WhisperForConditionalGeneration
P=Path(__file__).resolve().parent;R=P.parents[2];m=json.loads((P/'src/edit-manifest.json').read_text());torch.set_num_threads(2)
processor=WhisperProcessor.from_pretrained('openai/whisper-small',cache_dir=R/'.local/hazard_voice/asr-cache')
model=WhisperForConditionalGeneration.from_pretrained('openai/whisper-small',cache_dir=R/'.local/hazard_voice/asr-cache',use_safetensors=True).to('cpu')
segments=[(c['id'],c['startFrame']/30,c['durationInFrames']/30) for c in m['clips']]
ids={'v000','v007','v016','v125','v126','v127','v129','v130','v099'}
for d in m['dialogue']:
 if d['id'] in ids:segments.append((d['id'],d['startFrame']/30,d['durationInFrames']/30))
rows=[]
for name,start,duration in segments:
 data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-t',str(duration),'-i',str(P/'public/mixed.wav'),'-f','f32le','-ac','1','-ar','16000','-'])
 features=processor(np.frombuffer(data,dtype='<f4').copy(),sampling_rate=16000,return_tensors='pt',return_attention_mask=True)
 with torch.inference_mode():result=model.generate(**features,language='ja',task='transcribe',max_new_tokens=180)
 text=processor.batch_decode(result,skip_special_tokens=True)[0];rows.append(dict(name=name,start=start,duration=duration,recognized=text));print(name,text,flush=True)
(P/'out/mixed_asr_v9.json').write_text(json.dumps({'note':'Automated screening of final mixed waveform; no subjective listening claim.','segments':rows},ensure_ascii=False,indent=2))
