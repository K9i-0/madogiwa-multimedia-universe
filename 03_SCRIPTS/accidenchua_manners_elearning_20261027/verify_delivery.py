"""Verify the encoded delivery. Does not claim auditory or precise lip-sync review."""
import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path

EP = Path(__file__).resolve().parent
manifest = json.loads((EP / 'remotion/src/edit-manifest.json').read_text())
content = json.loads((EP / 'content.json').read_text())
video = EP / manifest['outputFile']
assert not manifest['pending'], manifest['pending']
assert manifest['revision'] == content['revision'] == 2
assert content['chapters'][2]['options'][content['chapters'][2]['answer']] == '窓際なのにすみません'
for chapter in content['chapters']:
    assert set(chapter['cast']) == {'sobaya', 'fukuchan'}
    assert sorted(f['option'] for f in chapter['feedback']) == [0, 1, 2]
    assert all(f['correct'] == (f['option'] == chapter['answer']) for f in chapter['feedback'])
    assert len([s for s in manifest['segments'] if s['type'] == 'feedback' and s['chapter'] == chapter['number']]) == 3

probe = json.loads(subprocess.check_output([
    'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(video)
]))
picture = next(s for s in probe['streams'] if s['codec_type'] == 'video')
sound = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
frames = manifest['composition']['durationInFrames']
assert (picture['width'], picture['height']) == (1280, 720)
assert picture['r_frame_rate'] == '24/1'
assert int(picture['nb_frames']) == frames
assert picture['codec_name'] == 'h264'
assert sound['codec_name'] == 'aac'
assert (int(sound['sample_rate']), sound['channels']) == (48000, 2)
assert abs(float(probe['format']['duration']) - frames / 24) < .06
subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(video), '-f', 'null', '-'], check=True)
measurement = subprocess.run([
    'ffmpeg', '-hide_banner', '-i', str(video),
    '-af', 'loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json', '-f', 'null', '-'
], capture_output=True, text=True, check=True)
levels = json.JSONDecoder().raw_decode(measurement.stderr[measurement.stderr.rfind('{'):])[0]
assert float(levels['input_tp']) <= 0, levels
assert -17 <= float(levels['input_i']) <= -15, levels

cursor = 0
for segment in manifest['segments']:
    assert segment['start'] == cursor
    cursor += segment['duration']
assert cursor == frames
captions = sorted(manifest['captions'], key=lambda c: c['start'])
for cue in captions:
    assert 0 <= cue['start'] < cue['end'] <= frames
for before, after in zip(captions, captions[1:]):
    assert before['end'] <= after['start']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

frame_audit = json.loads((EP / 'generated/audit-r2/encoded/manifest.json').read_text())
assert frame_audit['sha256'] == sha(video)
assert len(frame_audit['frames']) >= len(captions)

runs = []
for name in ('h3-job', 'h3-r2'):
    result = EP / 'generated' / name / 'results'
    status = json.loads((result / 'status.json').read_text())
    assert status['status'] == 'complete'
    for filename, digest in status['sha256'].items():
        assert sha(result / filename) == digest
    runs.append({'job': name, **status})

voices = json.loads((EP / 'voice-records.json').read_text())
active_lines = list(content['opening']) + list(content['ending'])
for chapter in content['chapters']:
    active_lines += chapter['dialogue'] + [chapter['question']] + [f['line'] for f in chapter['feedback']]
active_ids = {line['id'] for line in active_lines}
for line in active_lines:
    record = voices[line['id']]
    assert record['text'] == line['text']
    assert sha(EP / record['file']) == record['sha256']
adopted = []
for chapter in manifest['chapters']:
    path = EP / 'remotion/public' / chapter['video']
    adopted.append({'chapter': chapter['id'], 'video': chapter['video'],
                    'sha256': sha(path), 'audio_mode': chapter['audioMode']})
asr = []
for stem in (f'final_q{n}_clip_mix' for n in range(1, 6)):
    evidence = json.loads((EP / 'generated/asr' / (stem + '.json')).read_text())
    assert evidence['source_sha256'] == sha(EP / 'generated' / (stem + '.wav'))
    asr.append({'source': stem, 'text': evidence['text'], 'source_sha256': evidence['source_sha256']})

report = {
    'verified_at': datetime.now().astimezone().isoformat(),
    'file': video.name, 'sha256': sha(video), 'size_bytes': video.stat().st_size,
    'composition': manifest['composition'],
    'duration_seconds': frames / 24,
    'video_codec': picture['codec_name'], 'audio_codec': sound['codec_name'],
    'audio_sample_rate': int(sound['sample_rate']), 'audio_channels': sound['channels'],
    'audio_loudness_lufs': float(levels['input_i']),
    'audio_true_peak_dbtp': float(levels['input_tp']),
    'audio_lra': float(levels['input_lra']),
    'decode_to_end': 'passed', 'timeline': 'contiguous',
    'caption_count': len(captions), 'caption_overlap': False,
    'encoded_frame_audit': {'manifest': 'generated/audit-r2/encoded/manifest.json',
                            'sample_count': len(frame_audit['frames']), 'contact_sheets': len(frame_audit['pages'])},
    'revision': 2,
    'cast_in_all_scenes': ['そば屋', '福ギュン'],
    'feedback_narrations': 15,
    'adopted_voice_files_verified': len(active_ids),
    'active_voice_ids': sorted(active_ids),
    'h3_runs': runs, 'adopted_clips': adopted,
    'final_scene_asr': asr,
    'review_scope': {
        'visual': 'Chronological samples of all five adopted H3 clips, localized shirt repairs, all question/answer/feedback layouts and encoded caption frames inspected.',
        'audio': 'Canonical narration and dialogue ASR wording reviewed; all five final scene mixes re-transcribed with source hashes. Waveform timing and encoded loudness checked.',
        'auditory_listening': False,
        'precise_lipsync_verified': False
    }
}
(EP / 'production-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ('file', 'duration_seconds', 'size_bytes', 'audio_loudness_lufs', 'audio_true_peak_dbtp', 'decode_to_end')}, ensure_ascii=False))
