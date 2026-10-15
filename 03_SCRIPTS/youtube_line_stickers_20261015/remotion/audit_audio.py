"""Transcribe every adopted utterance without an expected-text prompt.

This is automated screening; it does not claim subjective listening.
"""
from pathlib import Path
import difflib
import hashlib
import json
import subprocess
import time
import unicodedata
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
report = P / 'out/audio_audit.json'
out = json.loads(report.read_text())['utterances'] if report.exists() else []
seen = {row['audioSha256'] for row in out}
count = len(json.loads((P / 'dialogue.json').read_text()))


def norm(text):
    return ''.join(char for char in unicodedata.normalize('NFKC', text) if char.isalnum())


while True:
    try:
        rows = json.loads((P / 'out/voice_progress.json').read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        time.sleep(3)
        continue
    for row in rows:
        if row['audioSha256'] in seen:
            continue
        raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(P / 'public' / row['audio']), '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'])
        samples = np.frombuffer(raw, dtype='<f4').copy()
        inputs = processor(samples, sampling_rate=16000, return_tensors='pt', return_attention_mask=True)
        with torch.inference_mode():
            generated = model.generate(**inputs, language='ja', task='transcribe', max_new_tokens=220)
        recognized = processor.batch_decode(generated, skip_special_tokens=True)[0]
        item = {'id': row['id'], 'who': row['who'], 'audio': row['audio'], 'audioSha256': row['audioSha256'],
            'expected': row['text'], 'spoken': row['spoken'], 'recognized': recognized,
            'similarity': round(difflib.SequenceMatcher(None, norm(row['spoken']), norm(recognized)).ratio(), 3),
            'durationSeconds': row['durationSeconds'], 'peak': float(np.max(np.abs(samples))),
            'nonFiniteSamples': int(np.sum(~np.isfinite(samples))), 'clippedSamples': int(np.sum(np.abs(samples) >= .999))}
        out.append(item)
        seen.add(row['audioSha256'])
        write_json(report, {'model': 'openai/whisper-small', 'expectedTextPrompt': False,
            'subjectiveListening': False, 'note': 'Automated transcription and waveform screening only.', 'utterances': out})
        print(row['id'], recognized, flush=True)
    if len(rows) == count and all(row['audioSha256'] in seen for row in rows):
        break
    time.sleep(3)
print('COMPLETE', len(rows), flush=True)
