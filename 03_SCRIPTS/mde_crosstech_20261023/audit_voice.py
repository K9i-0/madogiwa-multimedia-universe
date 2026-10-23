"""ASR timing and text cross-check; not a substitute for listening."""
from pathlib import Path
import json,subprocess,time
import numpy as np
import torch
from transformers import pipeline,WhisperProcessor,WhisperForConditionalGeneration
EP=Path(__file__).resolve().parent; ROOT=EP.parents[1]
cache=ROOT/'.local/hazard_voice/asr-cache'
torch.set_num_threads(3)
p=WhisperProcessor.from_pretrained('openai/whisper-small',cache_dir=cache,local_files_only=True)
m=WhisperForConditionalGeneration.from_pretrained('openai/whisper-small',cache_dir=cache,local_files_only=True,use_safetensors=True)
asr=pipeline('automatic-speech-recognition',model=m,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,device='cpu')
out=ROOT/'.local/mde-crosstech/asr.json'
rows=json.loads(out.read_text()) if out.exists() else []
done={r['id'] for r in rows}
lines=json.loads((EP/'dialogue.json').read_text())
for line in lines:
 if line['id'] in done:continue
 wav=EP/f"{line['id']}_{line['speaker']}.wav"
 for _ in range(450):
  rec=EP/'voice_generation_record.json'
  try:ready={r['id'] for r in json.loads(rec.read_text())}
  except (FileNotFoundError,json.JSONDecodeError):ready=set()
  if line['id'] in ready:break
  time.sleep(8)
 else:raise RuntimeError('Timed out waiting for '+line['id'])
 audio=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(wav),'-f','f32le','-ac','1','-ar','16000','-']),dtype='<f4').copy()
 result=asr({'raw':audio,'sampling_rate':16000},return_timestamps='word',generate_kwargs={'language':'ja','task':'transcribe'})
 row=dict(id=line['id'],expected=line['text'],result=result)
 rows.append(row);out.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
 print(line['id'],result['text'],flush=True)
