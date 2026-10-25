from pathlib import Path
import subprocess,json,numpy as np,torch
from transformers import pipeline,WhisperProcessor,WhisperForConditionalGeneration
P=Path(__file__).resolve().parent;R=P.parents[1];cache=R/'.local/hazard_voice/asr-cache';torch.set_num_threads(2)
p=WhisperProcessor.from_pretrained('openai/whisper-small',cache_dir=cache,local_files_only=True)
m=WhisperForConditionalGeneration.from_pretrained('openai/whisper-small',cache_dir=cache,local_files_only=True,use_safetensors=True)
asr=pipeline('automatic-speech-recognition',model=m,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,device='cpu')
manifest=json.loads((P/'remotion/src/edit-manifest.json').read_text());out=[]
cases=[{'id':d['id'],'path':P/d['audio'],'text':d['text']} for d in manifest['dialogue'] if d['id'] in ['line-009','line-058','line-081','line-086','line-092','line-100']]
for c in manifest['clips']:
 if c['id']=='expert':cases.append({'id':'clip-expert','path':P/'remotion/public'/c['src'],'start':c['sourceStartFrame']/30,'duration':c['durationInFrames']/30})
for c in cases:
 cmd=['ffmpeg','-v','error']
 if 'start' in c:cmd+=['-ss',str(c['start'])]
 cmd+=['-i',str(c['path'])]
 if 'duration' in c:cmd+=['-t',str(c['duration'])]
 data=subprocess.check_output(cmd+['-f','f32le','-ac','1','-ar','16000','-'])
 r=asr({'raw':np.frombuffer(data,dtype='<f4').copy(),'sampling_rate':16000},return_timestamps=True,generate_kwargs={'language':'ja','task':'transcribe'})
 out.append({'id':c['id'],'expected':c.get('text'),'result':r});print(json.dumps(out[-1],ensure_ascii=False),flush=True)
 (P/'speech_asr_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
