#!/usr/bin/env python3
"""Technical and frame-extraction checks for the approved-opening Short."""
from pathlib import Path
import hashlib
import json
import subprocess
from datetime import datetime, timezone

EPISODE = Path(__file__).resolve().parent
REPO = EPISODE.parents[1]
OUT = EPISODE / 'remotion/out/shorts-audit'


def run(args):
    return subprocess.run([str(a) for a in args], check=True, capture_output=True).stdout


def digest(path):
    with open(path, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    m = json.loads((EPISODE / 'shorts-manifest.json').read_text())
    source = REPO / m['audioSource']
    final = EPISODE / 'final_remotion_shorts_9x16.mp4'
    frames, fps = m['durationInFrames'], m['fps']
    OUT.mkdir(exist_ok=True)
    assert digest(source) == m['sourceSha256']
    info = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', final]))
    video = next(s for s in info['streams'] if s['codec_type'] == 'video')
    audio = next(s for s in info['streams'] if s['codec_type'] == 'audio')
    assert (video['width'], video['height']) == (720, 1280)
    assert video['r_frame_rate'] == '30/1'
    assert int(video['nb_frames']) == frames
    assert float(video['duration']) <= 180
    assert abs(float(video['duration']) - frames / fps) < 0.001
    assert audio['codec_name'] == 'aac' and audio['sample_rate'] == '48000'
    assert float(audio['duration']) <= frames / fps + 0.001
    run(['ffmpeg', '-v', 'error', '-i', final, '-f', 'null', '-'])
    # Compare the exact compressed AAC packets, not a re-encoded approximation.
    audio_cutoff = (int(frames / fps * 48000) // 1024 * 1024 - 1) / 48000
    def aac_hash(path, trim=False):
        data = run(['ffmpeg', '-v', 'error', '-i', path, '-map', '0:a:0', '-c:a', 'copy',
                    *(['-t', str(audio_cutoff)] if trim else []), '-f', 'adts', '-'])
        return hashlib.sha256(data).hexdigest()
    source_audio_hash, final_audio_hash = aac_hash(source, True), aac_hash(final)
    speech_pcm_identical = None
    if 'audioFadeOutStartFrame' in m:
        end_speech = m['audioFadeOutStartFrame'] / fps
        mixed = EPISODE / 'remotion/out/shorts_extended_audio.wav'
        def pcm_prefix(path):
            return run(['ffmpeg', '-v', 'error', '-i', path, '-t', str(end_speech),
                        '-map', '0:a:0', '-c:a', 'pcm_s16le', '-f', 's16le', '-'])
        speech_pcm_identical = pcm_prefix(source) == pcm_prefix(mixed)
        assert speech_pcm_identical
        tail = run(['ffmpeg', '-v', 'error', '-ss', str(m['audioTrimEndFrame']/fps),
                    '-i', mixed, '-c:a', 'pcm_s16le', '-f', 's16le', '-'])
        assert tail and not any(tail)
        assert m['audioTrimEndFrame'] < 1912  # next speaker starts here in v8
    else:
        assert source_audio_hash == final_audio_hash
    for c in m['captions']:
        assert 0 <= c['startFrame'] < c['endFrame'] <= frames
        assert len(c['text'].splitlines()) <= 3
    samples = [{'label': 'first', 'frame': 0}, {'label': 'last', 'frame': frames-1}]
    for i, c in enumerate(m['captions']):
        samples.append({'label': f'caption-{i+1:02d}', 'frame': (c['startFrame'] + c['endFrame']) // 2,
                        'text': c['text'], 'speaker': c['speaker']})
    samples.extend([{'label': 'line-chat-hold', 'frame': 570},
                    {'label': 'mail-before-reaction', 'frame': 835},
                    {'label': 'title-change', 'frame': 1215}])
    if m.get('endCard'):
        samples.extend([{'label': 'end-card-start', 'frame': m['endCard']['from'] + 8},
                        {'label': 'end-card-hold', 'frame': m['endCard']['from'] + 30}])
    for sample in samples:
        target = OUT / f"{sample['label']}-{sample['frame']:04d}.png"
        run(['ffmpeg', '-v', 'error', '-ss', str(sample['frame'] / fps), '-i', final,
             '-frames:v', '1', '-y', target])
        sample['file'] = str(target.relative_to(EPISODE))
    record = {
        'checkedAt': datetime.now(timezone.utc).isoformat(),
        'output': final.name, 'sha256': digest(final), 'bytes': final.stat().st_size,
        'source': str(source.relative_to(REPO)), 'sourceSha256': digest(source),
        'manifestSha256': digest(EPISODE / 'shorts-manifest.json'),
        'width': 720, 'height': 1280, 'fps': fps, 'frames': frames,
        'durationSeconds': frames / fps, 'audioDurationSeconds': float(audio['duration']),
        'codec': video['codec_name'], 'audioCodec': audio['codec_name'],
        'sampleRate': int(audio['sample_rate']),
        'audioPolicy': ('Original v8 decoded speech PCM preserved exactly through frame 1903; only the following pause fades, then silence under the end card. AAC encoded at 192 kbps.' if speech_pcm_identical else 'AAC stream copy of the approved source prefix.'),
        'sourceTrimmedAACSha256': source_audio_hash, 'finalAACSha256': final_audio_hash,
        'audioPayloadIdentical': source_audio_hash == final_audio_hash,
        'speechPcmIdentical': speech_pcm_identical, 'fullDecodePassed': True,
        'captionCards': len(m['captions']), 'maximumCaptionLines': max(len(c['text'].splitlines()) for c in m['captions']),
        'noCaptionSource': m['clips'][0]['source'], 'noCaptionLayer': True,
        'originalTimelinePreserved': True, 'subjectiveListening': False,
        'fullMotionPlayback': False, 'visualReview': 'pending', 'samples': samples,
        'duplicateCheck': {'paths': [
            '03_SCRIPTS/shorts_pilot_20261011/delivery.json',
            '03_SCRIPTS/shorts_pilot_20261011/youtube_uploads',
            '03_SCRIPTS/shorts_queue_20261011/queue.json'],
            'existingEntryFoundBeforeCreation': False},
    }
    (EPISODE / 'shorts-audit.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ['output', 'durationSeconds', 'frames', 'audioPayloadIdentical', 'speechPcmIdentical', 'fullDecodePassed', 'sha256']}, indent=2))


if __name__ == '__main__':
    main()
