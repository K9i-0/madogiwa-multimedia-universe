"""Spot-check the final mixed waveform at key jokes, names, and format terms."""
from pathlib import Path
import json
import subprocess
import numpy as np
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from prepare_voice import write_json

P = Path(__file__).resolve().parent
R = P.parents[2]
torch.set_num_threads(2)
cache = R / '.local/hazard_voice/asr-cache'
processor = WhisperProcessor.from_pretrained('openai/whisper-small', cache_dir=cache, local_files_only=True)
model = WhisperForConditionalGeneration.from_pretrained('openai/whisper-small', cache_dir=cache, use_safetensors=True, local_files_only=True).to('cpu')
m = json.loads((P / 'src/edit-manifest.json').read_text())
rows = []
ids = {'intro-07', 'intro-08', 'intro-09', 'intro-10', 'intro-13', 'main-01', 'main-02', 'main-03', 'export-02', 'end-05'}
for row in m['dialogue']:
    if row['id'] not in ids:
        continue
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(row['startFrame']/30),
        '-t', str(row['durationInFrames']/30), '-i', str(P / 'public/mixed.wav'), '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'])
    samples = np.frombuffer(raw, dtype='<f4').copy()
    inputs = processor(samples, sampling_rate=16000, return_tensors='pt', return_attention_mask=True)
    with torch.inference_mode():
        result = model.generate(**inputs, language='ja', task='transcribe', max_new_tokens=180)
    text = processor.batch_decode(result, skip_special_tokens=True)[0]
    rows.append({'id': row['id'], 'startFrame': row['startFrame'], 'durationInFrames': row['durationInFrames'],
        'expected': row['text'], 'recognized': text})
    print(row['id'], text, flush=True)
write_json(P / 'out/mixed_audio_audit.json', {'model': 'openai/whisper-small', 'expectedTextPrompt': False,
    'subjectiveListening': False, 'note': 'Automated spot check of the final music/effects/narration mix.', 'segments': rows})
