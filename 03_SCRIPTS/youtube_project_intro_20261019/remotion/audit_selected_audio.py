from pathlib import Path
import json,subprocess,numpy as np,torch,sys
from transformers import WhisperProcessor,WhisperForConditionalGeneration
P=Path(__file__).resolve().parent;R=P.parents[2];torch.set_num_threads(3)
p=WhisperProcessor.from_pretrained('openai/whisper-small',cache_dir=R/'.local/hazard_voice/asr-cache',local_files_only=True)
m=WhisperForConditionalGeneration.from_pretrained('openai/whisper-small',cache_dir=R/'.local/hazard_voice/asr-cache',use_safetensors=True,local_files_only=True).to('cpu');rows=[]
source=Path(sys.argv[1]) if len(sys.argv)>1 else P/'public/mixed.wav';duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(source)]))
for start in [250,263,399,606,615]:
 data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-i',str(source),'-t',str(min(13,duration-start)),'-f','f32le','-ac','1','-ar','16000','-'])
 feat=p(np.frombuffer(data,dtype='<f4').copy(),sampling_rate=16000,return_tensors='pt',return_attention_mask=True)
 with torch.inference_mode():r=m.generate(**feat,language='ja',task='transcribe',max_new_tokens=250)
 text=p.batch_decode(r,skip_special_tokens=True)[0];rows.append({'start':start,'text':text});print(start,text,flush=True)
(P/'out/selected_audio_asr.json').write_text(json.dumps({'source':str(source),'method':'Whisper-small local, no prompt. Automatic speech screening, not subjective listening.','segments':rows},ensure_ascii=False,indent=2))
