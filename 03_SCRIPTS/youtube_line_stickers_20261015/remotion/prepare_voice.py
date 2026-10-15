"""Generate this episode's two canonical voices and measure the integer-frame timeline.

Run with .local/Irodori-TTS/.venv/bin/python from the repository root.
No speed/pitch postprocessing or silence trimming is applied to voice inputs.
"""
from pathlib import Path
import hashlib
import json
import math
import os
import subprocess
import sys
import urllib.parse
import urllib.request

import numpy as np
import soundfile as sf

P = Path(__file__).resolve().parent
R = P.parents[2]
OLD = R / '03_SCRIPTS/youtube_ai_video_workflow_20261013'
BASE = 'http://127.0.0.1:50021'
FPS = 30


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(settings):
    return hashlib.sha256(json.dumps(settings, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def write_json(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def post(endpoint, params, data=None):
    req = urllib.request.Request(BASE + '/' + endpoint + '?' + urllib.parse.urlencode(params),
        data=b'' if data is None else json.dumps(data).encode(),
        headers={'Content-Type': 'application/json'}, method='POST')
    return urllib.request.urlopen(req, timeout=120).read()


def link_or_copy(source, destination):
    if destination.exists():
        assert sha(source) == sha(destination), destination
        return
    try:
        os.link(source, destination)
    except OSError:
        import shutil
        shutil.copy2(source, destination)


replacements = {
    'Claude Code': 'クロードコード', 'Codex': 'コーデックス',
    'Python': 'パイソン', 'Outlook': 'アウトルック', 'LINE': 'ライン',
    'APNG': 'エーピーエヌジー', 'PNG': 'ピーエヌジー', 'GIF': 'ジフ',
    'AI': 'エーアイ', 'GitHub': 'ギットハブ', 'Git': 'ギット',
    'main': 'メイン', 'tab': 'タブ', 'MB': 'メガバイト',
    '福ギュン': 'ふくぎゅん', '廃村': 'ハイソン', '〜': '。',
}


def main():
    for sub in ['public', 'out', 'src']:
        (P / sub).mkdir(exist_ok=True)
    rows = json.loads((P / 'dialogue.json').read_text())
    voice_overrides = json.loads((P / 'voice_overrides.json').read_text()) if (P / 'voice_overrides.json').exists() else {}
    timeline_config = json.loads((P / 'voice_timeline_config.json').read_text()) if (P / 'voice_timeline_config.json').exists() else {}
    engine = json.load(urllib.request.urlopen(BASE + '/version'))
    speaker = next(x for x in json.load(urllib.request.urlopen(BASE + '/speakers')) if x['name'] == '中国うさぎ')
    ref = R / '02_CHARACTERS/Yametaro_voice.wav'
    ref_hash = sha(ref)
    assert ref_hash == 'ede825a58cf1920f1bdfb353eea17d0feb24f20592d7f36d7c5c22c5ab60530b'
    revision = subprocess.check_output(['git', '-C', str(R / '.local/Irodori-TTS'), 'rev-parse', 'HEAD'], text=True).strip()
    old_by_identity = {}
    for record in [OLD / 'voice_record_v11.json', P.parent / 'voice_record.json']:
        if not record.exists():
            continue
        adoption_file = record.parent / ('adopted_audio_v11.json' if record.parent == OLD else 'adopted_audio.json')
        adopted_by_hash = {item['sha256']: record.parent / item['file']
            for item in json.loads(adoption_file.read_text())['audio']} if adoption_file.exists() else {}
        for d in json.loads(record.read_text())['lines']:
            source = record.parent / 'remotion/public' / d['audio']
            if not source.exists():
                source = adopted_by_hash.get(d['audioSha256'], source)
            if source.exists():
                old_by_identity[identity(d['voiceSettings'])] = (source, d['audioSha256'])
    runtime = None
    prepared = []
    for original_row in rows:
        row = dict(original_row, **voice_overrides.get(original_row['id'], {}))
        spoken = row.get('voicevoxReading', row.get('reading', row['text'])) if row['who'] == 'takosan' else row.get('reading', row['text'])
        for source, replacement in replacements.items():
            spoken = spoken.replace(source, replacement)
        kana = None
        if row['who'] == 'takosan':
            query = json.loads(post('audio_query', {'speaker': 61, 'text': spoken}))
            query.update(speedScale=1.1, pitchScale=0, intonationScale=1, volumeScale=1,
                outputSamplingRate=48000, outputStereo=False, prePhonemeLength=.10, postPhonemeLength=.20)
            settings = {'model': 'VOICEVOX:中国うさぎ', 'engineVersion': engine,
                'speakerVersion': speaker['version'], 'speakerId': 61, 'style': 'ノーマル',
                'query': query, 'text': spoken}
            kana = query.get('kana')
        else:
            assert row['who'] == 'yametaro', row
            settings = {'model': 'Aratako/Irodori-TTS-v4.1-Small', 'runtimeRevision': revision,
                'reference': str(ref.relative_to(R)), 'referenceSha256': ref_hash,
                'seed': row.get('seed', 7), 'caption': None, 'cfgScaleText': 5,
                'cfgScaleSpeaker': 5, 'numSteps': 40, 'durationScale': row.get('durationScale', .70),
                'trimTail': False, 'postTrim': False, 'text': spoken}
        key = identity(settings)
        name = f'voice_{row["id"]}_{key[:12]}.wav'
        path = P / 'public' / name
        reused_from = None
        if not path.exists() and key in old_by_identity:
            old_path, old_hash = old_by_identity[key]
            assert old_path.exists() and sha(old_path) == old_hash
            link_or_copy(old_path, path)
            reused_from = str(old_path.relative_to(R))
        if not path.exists():
            if row['who'] == 'takosan':
                path.write_bytes(post('synthesis', {'speaker': 61}, query))
            else:
                sys.path.insert(0, str(R / '.local/Irodori-TTS'))
                from irodori_tts.inference_runtime import InferenceRuntime, RuntimeKey, SamplingRequest, download_hf_checkpoint, save_wav
                if runtime is None:
                    runtime = InferenceRuntime.from_key(RuntimeKey(checkpoint=download_hf_checkpoint(settings['model']), model_device='mps', codec_device='mps'))
                result = runtime.synthesize(SamplingRequest(text=spoken, ref_wav=str(ref), seed=settings['seed'],
                    caption=None, cfg_scale_text=5, duration_scale=settings['durationScale'], trim_tail=False), log_fn=None)
                save_wav(str(path), result.audio, result.sample_rate)
                write_json(P / 'out' / (name + '.json'), {'settings': settings, 'messages': result.messages, 'timings': result.stage_timings})
        x, sr = sf.read(path)
        assert x.ndim == 1 and len(x) and np.isfinite(x).all()
        frames = math.ceil(len(x) / sr * FPS)
        envelope = [round(float(np.sqrt(np.mean(chunk * chunk))) if len(chunk) else 0, 5)
            for i in range(frames) for chunk in [x[round(i * sr / FPS):round((i + 1) * sr / FPS)]]]
        item = dict(row, audio=name, spoken=spoken, kana=kana, durationInFrames=frames,
            envelope=envelope, voiceSettings=settings, audioSha256=sha(path), sampleRate=sr,
            durationSeconds=len(x)/sr, reusedFrom=reused_from)
        prepared.append(item)
        write_json(P / 'out/voice_progress.json', prepared)
        print('READY', len(prepared), len(rows), row['id'], round(len(x) / sr, 2), spoken, flush=True)
    # Only measured frame indices are timing authorities; seconds are reporting values.
    cursor = timeline_config.get('startFrame', 60)
    for d in prepared:
        cursor += round(d.get('pauseBefore', 0) * FPS)
        d['startFrame'] = cursor
        cursor += d['durationInFrames'] + round(d.get('pause', .3) * FPS)
    end = cursor + timeline_config.get('endHoldFrames', 90)
    main_id = timeline_config.get('mainStartId', 'main-01')
    ending_id = timeline_config.get('endingStartId', 'end-01')
    manifest = {'composition': {'width': 1280, 'height': 720, 'fps': FPS, 'durationInFrames': end},
        'mainStartFrame': next((d['startFrame'] for d in prepared if d['id'] == main_id), prepared[0]['startFrame']),
        'endingStartFrame': next((d['startFrame'] for d in prepared if d['id'] == ending_id), end),
        'creditsStartFrame': end, 'creditsInDescription': True,
        'voiceModel': 'Irodori Yametaro + VOICEVOX Chugoku Usagi', 'audioSrc': 'mixed.wav', 'dialogue': prepared, 'clips': []}
    write_json(P / 'src/edit-manifest.json', manifest)
    write_json(P.parent / 'voice_record.json', {'version': 1, 'subjectiveListening': False,
        'takosanSelection': '中国うさぎ・ノーマル・速度1.1・音高0',
        'lines': [{k: v for k, v in d.items() if k != 'envelope'} for d in prepared]})
    adoption = []
    for d in prepared:
        adopted = P.parent / f'voice_{d["id"]}_{d["who"]}_{d["audioSha256"][:8]}.wav'
        link_or_copy(P / 'public' / d['audio'], adopted)
        adoption.append({'id': d['id'], 'file': adopted.name, 'publicAudio': d['audio'], 'sha256': d['audioSha256'], 'who': d['who']})
    write_json(P.parent / 'adopted_audio.json', {'version': 1, 'audio': adoption})
    print('COMPLETE', end / FPS, 'seconds', flush=True)


if __name__ == '__main__':
    main()
