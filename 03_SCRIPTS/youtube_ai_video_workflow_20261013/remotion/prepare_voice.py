"""Generate cached VOICEVOX narration and insert source clips after dialogue IDs."""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import math
import os
import wave

import numpy as np
import requests

P = Path(__file__).resolve().parent
FPS = 30
ENGINE = 'http://127.0.0.1:50021'


def get_json(url, **kwargs):
    response = requests.get(url, timeout=30, **kwargs)
    response.raise_for_status()
    return response.json()


version = get_json(f'{ENGINE}/version')
rows = json.loads((P / 'dialogue.json').read_text())
clip_config = json.loads((P / 'clips_config.json').read_text())
if isinstance(clip_config, dict):
    clip_config = clip_config['clips']
row_ids = [row['id'] for row in rows]
assert len(set(row_ids)) == len(row_ids), 'Dialogue IDs must be unique'
clips_after = defaultdict(list)
for clip in clip_config:
    assert clip['afterId'] in row_ids, f"Unknown clip insertion ID: {clip['afterId']}"
    clips_after[clip['afterId']].append(clip)

replacements = {
    'Claude Code': 'クロードコード', 'Codex': 'コーデックス',
    'VOICEVOX': 'ボイスボックス', 'Remotion': 'リモーション',
    'Irodori': 'イロドリ', 'Qwen Cloud': 'クウェンクラウド',
    'Wan 3.0': 'ワン、スリーポイントゼロ', 'Wan': 'ワン',
    'API': 'エーピーアイ', 'AI': 'エーアイ',
    '480p': '480ピー', '720p': '720ピー', '1080p': '1080ピー',
    'h3': 'エイチスリー', '福ギュン': 'フクギュン',
}
# Disambiguate Japanese readings while leaving the approved text and captions intact.
phrase_readings = {
    '音量や間の調整': '音量や、まの調整',
    '動画生成の分よ': '動画生成のぶんよ',
}
out = []
clips = []
cursor = 15
(P / 'public').mkdir(exist_ok=True)
(P / 'out').mkdir(exist_ok=True)
for i, row in enumerate(rows):
    speaker = 2 if row['who'] == 'metan' else 3
    spoken = row.get('reading', row['text'])
    for original, reading in phrase_readings.items():
        spoken = spoken.replace(original, reading)
    for original, reading in replacements.items():
        spoken = spoken.replace(original, reading)
    response = requests.post(f'{ENGINE}/audio_query', params={'speaker': speaker, 'text': spoken}, timeout=60)
    response.raise_for_status()
    query = response.json()
    # VOICEVOX 0.25.1 tokenizes this renamed character as three unrelated words.
    # Keep the approved caption/text intact and join the proper name in the kana
    # pronunciation query. The speaker-specific accent endpoint recalculates
    # mora lengths and pitch for the merged phrase without editing global dictionaries.
    if '福ギュンが' in row['text']:
        separated_name = "フ'ク/ギュ'/ンガ'"
        assert separated_name in query['kana'], ('Review Fukugyun reading for this engine version', query['kana'])
        corrected_kana = query['kana'].replace(separated_name, "フクギュ'ンガ")
        response = requests.post(f'{ENGINE}/accent_phrases',
                                 params={'speaker': speaker, 'text': corrected_kana, 'is_kana': True}, timeout=60)
        response.raise_for_status()
        query['accent_phrases'] = response.json()
        query['kana'] = corrected_kana
    query.update(speedScale=row.get('speedScale', 1.13 if speaker == 2 else 1.15),
                 prePhonemeLength=.09, postPhonemeLength=.12, outputSamplingRate=24000)
    key = hashlib.sha256(json.dumps([speaker, version, query], sort_keys=True).encode()).hexdigest()[:12]
    name = f'voice_{i:03}_{key}.wav'
    path = P / 'public' / name
    reused = path.exists()
    if not reused:
        # The query hash contains speaker, engine version, text, pronunciation and synthesis settings.
        # Reuse identical audio even if an edit moved the line to another index.
        cached = next(iter((P / 'public').glob(f'voice_*_{key}.wav')), None)
        if cached:
            os.link(cached, path)
            reused = True
        else:
            response = requests.post(f'{ENGINE}/synthesis', params={'speaker': speaker}, json=query, timeout=120)
            response.raise_for_status()
            path.write_bytes(response.content)
    with wave.open(str(path)) as wav:
        assert wav.getnchannels() == 1 and wav.getsampwidth() == 2, name
        samples = np.frombuffer(wav.readframes(wav.getnframes()), dtype=np.int16).astype(float) / 32768
        rate = wav.getframerate()
    frames = math.ceil(len(samples) / rate * FPS)
    envelope = []
    for j in range(frames):
        block = samples[int(j * rate / FPS):min(len(samples), int((j + 1) * rate / FPS))]
        envelope.append(round(float(np.sqrt(np.mean(block ** 2))), 4) if len(block) else 0)
    out.append(dict(row, startFrame=cursor, durationInFrames=frames, audio=name, speaker=speaker,
                    spoken=spoken, kana=query['kana'], envelope=envelope))
    cursor += frames + row.get('pause', 9)
    inserted = clips_after.get(row['id'], [])
    for clip_index, clip in enumerate(inserted):
        cursor += clip.get('pauseBeforeFrames', 0)
        clips.append(dict(clip, startFrame=cursor))
        cursor += clip['durationInFrames']
        # A short breath after the group avoids cutting straight from sample audio to narration.
        cursor += clip.get('pauseAfterFrames', 15 if clip_index == len(inserted) - 1 else 0)
    print(i, row['id'], frames, 'cache' if reused else 'synth', query['kana'], flush=True)

credits_start = cursor + 30
manifest = {
    'composition': {'width': 1280, 'height': 720, 'fps': FPS, 'durationInFrames': credits_start + 8 * FPS},
    'mainStartFrame': next(d['startFrame'] for d in out if d['view'] in ('roles', 'roadmap')),
    'endingStartFrame': next(d['startFrame'] for d in out if d['view'] == 'h3'),
    'creditsStartFrame': credits_start,
    'voicevoxVersion': version,
    'dialogue': out,
    'clips': clips,
}
(P / 'src/edit-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
print('DURATION', manifest['composition']['durationInFrames'] / FPS, flush=True)
