"""Screen changed v6 voices and prove untouched v5 waveform preservation.

ASR and VAD are read-only screening tools, not listening or safe cut-point proof.
"""
from pathlib import Path
import difflib
import hashlib
import json
import re
import subprocess
import sys
import unicodedata

import numpy as np
import soundfile as sf
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from prepare_voice import write_json

P = Path(__file__).resolve().parent
R = P.parents[2]
torch.set_num_threads(2)
cache = R / '.local/hazard_voice/asr-cache'
processor = WhisperProcessor.from_pretrained('openai/whisper-small', cache_dir=cache, local_files_only=True)
model = WhisperForConditionalGeneration.from_pretrained('openai/whisper-small', cache_dir=cache,
    use_safetensors=True, local_files_only=True).to('cpu')
sys.path.insert(0, str(R / '.local/silero-vad-analysis/src'))
from silero_vad.utils_vad import get_speech_timestamps, init_jit_model
vad = init_jit_model(str(R / '.local/silero-vad-analysis/src/silero_vad/data/silero_vad.jit'))


def norm(text):
    return ''.join(char for char in unicodedata.normalize('NFKC', text) if char.isalnum())


def review_signals(item):
    """Informational warnings only: names, dialect and intentional pauses vary."""
    speech = item['sileroVAD']['0.5']
    gaps = [round(right['start']-left['end'], 3) for left, right in zip(speech, speech[1:])]
    recognized = norm(item['recognized'])
    expected = norm(item['spoken'])
    repetition = re.search(r'(.{6,30})\1+', recognized)
    unexpected_repeat = repetition.group(0) if repetition and repetition.group(0) not in expected else None
    flags = []
    if item['similarity'] < .45:
        flags.append('ASR_LOW_TEXT_SIMILARITY')
    if gaps and max(gaps) > 1.2:
        flags.append('LONG_INTERNAL_VAD_GAP')
    if item['tailAfterVadSeconds'] > .7 and (item['tailAfterVadPeakRmsDb'] or -99) > -35:
        flags.append('AUDIBLE_ENERGY_AFTER_VAD_END')
    if unexpected_repeat:
        flags.append('UNEXPECTED_ASR_REPETITION')
    if not speech:
        flags.append('NO_VAD_SPEECH')
    if item['maxPcmFullScaleRunSamples'] >= 48:
        flags.append('AT_LEAST_1MS_FULL_SCALE_RUN')
    return {'internalVadGapsSeconds': gaps, 'maxInternalVadGapSeconds': max(gaps, default=0),
            'unexpectedAsrRepetition': unexpected_repeat, 'machineReviewFlags': flags,
            'requiresHumanListeningForNaturalness': True}


def main():
    current = json.loads((P.parent / 'voice_record.json').read_text())['lines']
    baseline_data = subprocess.check_output(['git', 'show',
        'bc765980:03_SCRIPTS/youtube_line_stickers_20261015/voice_record.json'], cwd=R, text=True)
    baseline = {r['id']: r for r in json.loads(baseline_data)['lines']}
    changed = {r['id'] for r in current if r['id'] not in baseline
        or any(r.get(k) != baseline[r['id']].get(k) for k in ['who', 'text', 'reading', 'voiceSettings'])}
    report_path = P.parent / 'voice_audit_v6.json'
    old_report = json.loads(report_path.read_text()) if report_path.exists() else {}
    cached = {r['audioSha256']: r for r in old_report.get('changedUtterances', [])}
    reviewed_hashes_unchanged = set(cached) == {r['audioSha256'] for r in current if r['id'] in changed}
    adopted = {r['id']: r for r in json.loads((P.parent / 'adopted_audio.json').read_text())['audio']}
    verified, preserved, rows = [], [], []
    for row in current:
        source = P / 'public' / row['audio']
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        assert digest == row['audioSha256']
        assert hashlib.sha256((P.parent / adopted[row['id']]['file']).read_bytes()).hexdigest() == digest
        x, sr = sf.read(source)
        assert x.ndim == 1 and len(x) and np.isfinite(x).all()
        verified.append(row['id'])
        if row['id'] not in changed:
            assert digest == baseline[row['id']]['audioSha256'], row['id']
            assert row['voiceSettings'] == baseline[row['id']]['voiceSettings'], row['id']
            preserved.append(row['id'])
            continue
        if digest in cached:
            item = cached[digest]
        else:
            raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(source),
                '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'])
            audio = np.frombuffer(raw, dtype='<f4').copy()
            inputs = processor(audio, sampling_rate=16000, return_tensors='pt', return_attention_mask=True)
            with torch.inference_mode():
                result = model.generate(**inputs, language='ja', task='transcribe', max_new_tokens=220)
            recognized = processor.batch_decode(result, skip_special_tokens=True)[0]
            speech = {str(level): get_speech_timestamps(torch.from_numpy(audio), vad,
                sampling_rate=16000, threshold=level, min_speech_duration_ms=80,
                min_silence_duration_ms=100, speech_pad_ms=0, return_seconds=True)
                for level in [.25, .5]}
            rms = np.array([np.sqrt(np.mean(audio[i:i+160] ** 2)) for i in range(0, len(audio), 160)])
            last = speech['0.5'][-1]['end'] if speech['0.5'] else 0
            tail = rms[min(len(rms), round(last * 100)):]
            item = {'id': row['id'], 'who': row['who'], 'audioSha256': digest,
                'audio': row['audio'], 'expected': row['text'], 'spoken': row['spoken'],
                'recognized': recognized,
                'similarity': round(difflib.SequenceMatcher(None, norm(row['spoken']), norm(recognized)).ratio(), 3),
                'durationSeconds': len(x) / sr, 'sampleRate': sr,
                'peak': float(np.max(np.abs(x))), 'nonFiniteSamples': int(np.sum(~np.isfinite(x))),
                'clippedSamples': int(np.sum(np.abs(x) >= .999)),
                'sileroVAD': speech, 'tailAfterVadSeconds': round(len(audio)/16000-last, 3),
                'tailAfterVadPeakRmsDb': round(float(20*np.log10(max(float(tail.max()), 1e-9))), 2) if len(tail) else None,
                'voiceSettings': row['voiceSettings'], 'postprocessingApplied': bool(row.get('audioProcessing'))}
        full_scale = (x <= -1) | (x >= 32767 / 32768)
        edges = np.diff(np.pad(full_scale.astype(int), (1, 1)))
        starts, ends = np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)
        item.update(actualPcmFullScaleSamples=int(full_scale.sum()),
            maxPcmFullScaleRunSamples=int(max(ends-starts)) if len(starts) else 0)
        item.update(review_signals(item))
        rows.append(item)
        report = {'version': 6, 'status': 'automated_screening', 'subjectiveListening': False,
            'baseline': 'v5; immutable voice record from Git bc765980',
            'asrModel': 'openai/whisper-small', 'expectedTextPrompt': False,
            'vadModel': 'Silero VAD', 'vadRevision': '1e261b036686cd0017d500ee96acd1c4ba572a9d',
            'note': 'ASR/VAD/waveform checks only. Dialect and proper-name transcription may vary. VAD is not proof of a safe phoneme cut or natural performance.',
            'adoptedUtterances': len(current), 'changedUtteranceIds': sorted(changed),
            'changedUtterances': rows, 'unchangedWaveformIdsVerified': preserved,
            'retainedCleanupIds': [r['id'] for r in current if r.get('audioProcessing')],
            'allWaveformHashesVerified': len(verified) == len(current),
            'allUnchangedSettingsAndWaveformsPreserved': len(preserved) == len(current)-len(changed),
            'allChangedLinesScreened': len(rows) == len(changed),
            'machineFlaggedUtteranceIds': [r['id'] for r in rows if r['machineReviewFlags']]}
        if reviewed_hashes_unchanged and old_report.get('screeningReview'):
            report['screeningReview'] = old_report['screeningReview']
        write_json(report_path, report)
        print(row['id'], round(item['durationSeconds'], 3), 'tail', item['tailAfterVadSeconds'], item['recognized'], flush=True)
    report.update(unchangedWaveformIdsVerified=preserved,
        allWaveformHashesVerified=len(verified) == len(current),
        allUnchangedSettingsAndWaveformsPreserved=len(preserved) == len(current)-len(changed))
    write_json(report_path, report)
    assert report['allWaveformHashesVerified'] and report['allUnchangedSettingsAndWaveformsPreserved'] and report['allChangedLinesScreened']
    print('PASS', len(current), 'waveforms;', len(preserved), 'preserved;', len(rows), 'changed voices screened.')


if __name__ == '__main__':
    main()
