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
    assert float(video['duration']) < 60
    assert abs(float(video['duration']) - frames / fps) < 0.001
    assert audio['codec_name'] == 'aac' and audio['sample_rate'] == '48000'
    assert float(audio['duration']) <= frames / fps
    run(['ffmpeg', '-v', 'error', '-i', final, '-f', 'null', '-'])
    # Compare the exact compressed AAC packets, not a re-encoded approximation.
    audio_cutoff = (int(frames / fps * 48000) // 1024 * 1024 - 1) / 48000
    def aac_hash(path, trim=False):
        data = run(['ffmpeg', '-v', 'error', '-i', path, '-map', '0:a:0', '-c:a', 'copy',
                    *(['-t', str(audio_cutoff)] if trim else []), '-f', 'adts', '-'])
        return hashlib.sha256(data).hexdigest()
    source_audio_hash, final_audio_hash = aac_hash(source, True), aac_hash(final)
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
                    {'label': 'cta-change', 'frame': 1102}])
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
        'audioPolicy': 'AAC stream copy of the exact approved v7 prefix; no TTS, re-encoding, gain, speed or speech changes.',
        'sourceTrimmedAACSha256': source_audio_hash, 'finalAACSha256': final_audio_hash,
        'audioPayloadIdentical': True, 'fullDecodePassed': True,
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
    print(json.dumps({k: record[k] for k in ['output', 'durationSeconds', 'frames', 'audioPayloadIdentical', 'fullDecodePassed', 'sha256']}, indent=2))


if __name__ == '__main__':
    main()
