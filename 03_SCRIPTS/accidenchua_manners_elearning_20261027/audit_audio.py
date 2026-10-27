"""ASR evidence and timing assistance; never a substitute for listening or voice QA."""
from pathlib import Path
import json,subprocess,sys
import numpy as np
import torch
from transformers import WhisperProcessor,WhisperForConditionalGeneration

EP=Path(__file__).resolve().parent;ROOT=EP.parents[1]
torch.set_num_threads(4)
cache=ROOT/'.local/hazard_voice/asr-cache'
processor=WhisperProcessor.from_pretrained('openai/whisper-large-v3-turbo',cache_dir=cache,local_files_only=True)
model=WhisperForConditionalGeneration.from_pretrained('openai/whisper-large-v3-turbo',cache_dir=cache,local_files_only=True,use_safetensors=True).to('mps').float().eval()
outdir=EP/'generated/asr';outdir.mkdir(parents=True,exist_ok=True)
for arg in sys.argv[1:]:
 source=Path(arg);out=outdir/(source.stem+'.json')
 if out.exists():print('EXISTS',source.name,flush=True);continue
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(source),'-f','f32le','-ac','1','-ar','16000','-'])
 samples=np.frombuffer(raw,dtype='<f4').copy()
 features=processor(samples,sampling_rate=16000,return_tensors='pt',return_attention_mask=True).to('mps')
 with torch.inference_mode():result=model.generate(**features,language='ja',task='transcribe',max_new_tokens=300,return_timestamps=True)
 decoded=processor.tokenizer.decode(result[0].cpu().tolist(),skip_special_tokens=True,output_offsets=True)
 out.write_text(json.dumps({'source':str(source),'duration':len(samples)/16000,'model':'openai/whisper-large-v3-turbo',**decoded},ensure_ascii=False,indent=2)+'\n')
 print(source.name,decoded,flush=True)
