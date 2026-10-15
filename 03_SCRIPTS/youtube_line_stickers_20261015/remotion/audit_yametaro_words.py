"""Read-only timing screen, not a speech-cutting algorithm."""
from pathlib import Path
import json
import subprocess
import time
import numpy as np
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration, pipeline
P=Path(__file__).resolve().parent;R=P.parents[2]
torch.set_num_threads(2)
cache=R/'.local/hazard_voice/asr-cache'
processor=WhisperProcessor.from_pretrained('openai/whisper-small',cache_dir=cache,local_files_only=True)
model=WhisperForConditionalGeneration.from_pretrained('openai/whisper-small',cache_dir=cache,use_safetensors=True,local_files_only=True,attn_implementation='eager').to('cpu')
asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,device=-1)
targets={r['id'] for r in json.loads((P/'dialogue.json').read_text()) if r['who']=='yametaro' and not r['id'].startswith(('intro-','main-'))}
out=P/'out/yametaro_words_v3.json';report=json.loads(out.read_text()) if out.exists() else {'model':'openai/whisper-small','subjectiveListening':False,'note':'Cross-attention word times are approximate; Japanese phrases can span a single item. Never use wordEnd as a cut point without phoneme review.','utterances':[]}
seen={r['audioSha256'] for r in report['utterances']}
while True:
 try: rows=json.loads((P/'out/voice_progress.json').read_text())
 except (FileNotFoundError,json.JSONDecodeError):time.sleep(3);continue
 selected=[r for r in rows if r['id'] in targets]
 for row in selected:
  if row['audioSha256'] in seen:continue
  raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(P/'public'/row['audio']),'-f','f32le','-ar','16000','-ac','1','-'])
  samples=np.frombuffer(raw,dtype='<f4').copy()
  result=asr({'raw':samples,'sampling_rate':16000},return_timestamps='word',generate_kwargs={'language':'ja','task':'transcribe','num_beams':1,'max_new_tokens':180})
  ends=[c['timestamp'][1] for c in result.get('chunks',[]) if c['timestamp'][1] is not None]
  item={'id':row['id'],'audioSha256':row['audioSha256'],'expected':row['text'],'durationSeconds':row['durationSeconds'],'recognized':result['text'],'words':result.get('chunks',[]),'wordEnd':max(ends) if ends else None}
  report['utterances'].append(item);seen.add(row['audioSha256']);tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');tmp.replace(out)
  print(row['id'],item['wordEnd'],row['durationSeconds'],result['text'],flush=True)
 if len(selected)==len(targets) and all(r['audioSha256'] in seen for r in selected):break
 time.sleep(3)
print('COMPLETE',len(targets),flush=True)
