"""Verify the encoded delivery. Does not claim auditory or precise lip-sync review."""
import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path

EP = Path(__file__).resolve().parent
video = EP / 'final_remotion_elearning.mp4'
manifest = json.loads((EP / 'remotion/src/edit-manifest.json').read_text())
assert not manifest['pending'], manifest['pending']

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

runs = []
for name in ('h3-job', 'h3-retry'):
    result = EP / 'generated' / name / 'results'
    status = json.loads((result / 'status.json').read_text())
    assert status['status'] == 'complete'
    for filename, digest in status['sha256'].items():
        assert sha(result / filename) == digest
    runs.append({'job': name, **status})

voices = json.loads((EP / 'voice-records.json').read_text())
for record in voices.values():
    assert sha(EP / record['file']) == record['sha256']
adopted = []
for chapter in manifest['chapters']:
    path = EP / 'remotion/public' / chapter['video']
    adopted.append({'chapter': chapter['id'], 'video': chapter['video'],
                    'sha256': sha(path), 'audio_mode': chapter['audioMode']})
asr = []
for stem in ('q1_480p', 'final_q2_clip_mix', 'final_q3_clip_mix', 'q4_480p', 'q5_480p'):
    evidence = json.loads((EP / 'generated/asr' / (stem + '.json')).read_text())
    asr.append({'source': stem, 'text': evidence['text']})

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
    'adopted_voice_files_verified': len(voices),
    'h3_runs': runs, 'adopted_clips': adopted,
    'final_scene_asr': asr,
    'review_scope': {
        'visual': 'Chronological H3 samples, shirt repair samples, and every question, answer and explanation layout inspected.',
        'audio': 'ASR wording, waveform timing and technical loudness checks. Q2/Q3 final mixes re-transcribed after replacement.',
        'auditory_listening': False,
        'precise_lipsync_verified': False
    }
}
(EP / 'production-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ('file', 'duration_seconds', 'size_bytes', 'audio_loudness_lufs', 'audio_true_peak_dbtp', 'decode_to_end')}, ensure_ascii=False))
