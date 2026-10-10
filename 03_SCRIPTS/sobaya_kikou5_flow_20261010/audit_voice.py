from pathlib import Path
import json,subprocess,numpy as np,torch,sys,hashlib
from transformers import WhisperProcessor,WhisperForConditionalGeneration
root=Path.cwd();ep=Path(__file__).resolve().parent;cache=root/'.local/hazard_voice/asr-cache'
p=WhisperProcessor.from_pretrained('openai/whisper-small',cache_dir=cache);m=WhisperForConditionalGeneration.from_pretrained('openai/whisper-small',cache_dir=cache,use_safetensors=True);torch.set_num_threads(4)
rows=json.loads((ep/'dialogue.json').read_text())
prior={r['audio']:r for r in json.loads((ep/'asr_screening.json').read_text())['lines']} if (ep/'asr_screening.json').exists() else {}
indices={int(x) for x in sys.argv[1:]}
for i,r in enumerate(rows,1):
 if not (ep/r['audio']).exists():continue
 r['sha256']=hashlib.sha256((ep/r['audio']).read_bytes()).hexdigest()
 if r['audio'] in prior and 'recognized' in prior[r['audio']] and prior[r['audio']].get('sha256')==r['sha256'] and (not indices or i not in indices):
  r['recognized']=prior[r['audio']]['recognized'];continue
 b=subprocess.check_output(['ffmpeg','-v','error','-i',str(ep/r['audio']),'-f','f32le','-ac','1','-ar','16000','-']);f=p(np.frombuffer(b,dtype='<f4'),sampling_rate=16000,return_tensors='pt',return_attention_mask=True)
 with torch.inference_mode():ids=m.generate(**f,language='ja',task='transcribe',max_new_tokens=160)
 r['recognized']=p.batch_decode(ids,skip_special_tokens=True)[0];print(r['audio'],r['recognized'],flush=True)
(ep/'asr_screening.json').write_text(json.dumps({'note':'Automated screening only; not listening verification','lines':rows},ensure_ascii=False,indent=2))
