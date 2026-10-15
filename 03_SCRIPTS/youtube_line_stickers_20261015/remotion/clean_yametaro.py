"""Replay individually reviewed cuts without changing the preserved TTS originals.

prepare_voice.py applies these recipes automatically before measuring its timeline.
Running this file directly restores/verifies the processed public WAVs only.
"""
from pathlib import Path
import hashlib
import json
import wave
import numpy as np

P = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_recipes():
    source = P / 'voice_cleanup.json'
    return {row['id']: row for row in json.loads(source.read_text())['cuts']} if source.exists() else {}


def apply_cleanup(row_id, raw_path=None, generation_settings_sha256=None):
    recipe = load_recipes()[row_id]
    original = P.parent / recipe['source']
    assert sha(original) == recipe['sourceSha256'], ('Uncut source changed', row_id)
    if raw_path is not None:
        assert sha(raw_path) == recipe['sourceSha256'], ('Wrong generation for this cut', row_id)
    if generation_settings_sha256 is not None:
        assert generation_settings_sha256 == recipe['generationSettingsSha256'], ('Regenerated line needs a new cut review', row_id)
    identity = {key: recipe[key] for key in ['sourceSha256', 'sampleRate', 'keepStartSample', 'keepEndSample', 'tailFadeSamples']}
    identity['algorithm'] = 'pcm16_keep_linear_tail_fade_v1'
    key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    output = P / 'public' / f'clean_{row_id}_{key[:12]}.wav'
    if not output.exists():
        with wave.open(str(original)) as wav:
            params = wav.getparams()
            assert params.sampwidth == 2 and params.nchannels == 1 and params.framerate == recipe['sampleRate']
            samples = np.frombuffer(wav.readframes(wav.getnframes()), '<i2').copy()
        start, end, fade = recipe['keepStartSample'], recipe['keepEndSample'], recipe['tailFadeSamples']
        assert 0 <= start < end <= len(samples) and 0 < fade < end-start
        clipped = samples[start:end].copy()
        clipped[-fade:] = np.rint(clipped[-fade:].astype(np.float64) * np.linspace(1, 0, fade)).astype('<i2')
        assert np.array_equal(clipped[:-fade], samples[start:end-fade])
        with wave.open(str(output), 'wb') as wav:
            wav.setparams(params)
            wav.writeframes(clipped.astype('<i2').tobytes())
    assert sha(output) == recipe['expectedOutputSha256'], ('Cleanup output differs from reviewed candidate', row_id)
    record = {**recipe, 'algorithm': identity['algorithm'], 'processingIdentity': key,
        'outputAudio': output.name, 'outputSha256': sha(output), 'sourcePreserved': True,
        'subjectiveListening': False}
    return output, record


if __name__ == '__main__':
    records = [apply_cleanup(row_id)[1] for row_id in load_recipes()]
    target = P / 'out/cleanup_render_report.json'
    target.write_text(json.dumps({'audio': records}, ensure_ascii=False, indent=2) + '\n')
    print('Restored/verified', len(records), 'individually reviewed cuts; originals unchanged.')
