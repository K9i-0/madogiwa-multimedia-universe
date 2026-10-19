from pathlib import Path
import json, subprocess, numpy as np, torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
P=Path(__file__).resolve().parent;R=P.parents[2];torch.set_num_threads(2)
m=json.loads((P/'src/edit-manifest.json').read_text())
old=json.loads(subprocess.check_output(['git','show','91c77472:03_SCRIPTS/youtube_project_intro_20261019/remotion/src/edit-manifest.json'],cwd=R));used={d['audio'] for d in old['dialogue']}
p=WhisperProcessor.from_pretrained('openai/whisper-small',cache_dir=R/'.local/hazard_voice/asr-cache',local_files_only=True)
model=WhisperForConditionalGeneration.from_pretrained('openai/whisper-small',cache_dir=R/'.local/hazard_voice/asr-cache',use_safetensors=True,local_files_only=True).to('cpu');rows=[]
for d in m['dialogue']:
 if d['audio'] in used:continue
 data=subprocess.check_output(['ffmpeg','-v','error','-i',str(P.parent/d['audio']),'-f','f32le','-ac','1','-ar','16000','-'])
 feat=p(np.frombuffer(data,dtype='<f4').copy(),sampling_rate=16000,return_tensors='pt',return_attention_mask=True)
 with torch.inference_mode():result=model.generate(**feat,language='ja',task='transcribe',max_new_tokens=220)
 text=p.batch_decode(result,skip_special_tokens=True)[0];rows.append(dict(id=d['id'],expected=d['text'],asr=text,kana=d['kana']));print(d['id'],text,flush=True)
(P.parent/'qa_revision_audio.json').write_text(json.dumps(dict(method='Whisper-small local, no prompt; not subjective listening',rows=rows),ensure_ascii=False,indent=2))
