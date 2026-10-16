#!/usr/bin/env python3
"""Check the one-word display correction and exact audio preservation."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
OUT = P / 'remotion/out/caption-fix-v8-audit'


def run(args):
    return subprocess.check_output([str(a) for a in args], cwd=ROOT)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def aac(path):
    return hashlib.sha256(run(['ffmpeg', '-v', 'error', '-i', path, '-map', '0:a:0',
                               '-c:a', 'copy', '-f', 'adts', '-'])).hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    prefix = str(P.relative_to(ROOT)) + '/'
    for name in ['remotion/src/edit-manifest.json', 'remotion/dialogue.json']:
        expected = json.loads(run(['git', 'show', 'd49cbdab:' + prefix + name]))
        for d in expected['dialogue'] if isinstance(expected, dict) else expected:
            if d['id'] == 'intro-08':
                d['text'] = d['text'].replace('移動らしい', '異動らしい')
                for c in d.get('captionSegments', []):
                    c['text'] = c['text'].replace('移動らしい', '異動らしい')
        assert json.loads((P / name).read_text()) == expected
    records = []
    for name, frames, width, height, audio_source in [
        ('final_remotion_line_stickers_v8.mp4', 20440, 1280, 720, 'final_remotion_line_stickers_v7.mp4'),
        ('final_remotion_x_opening_16x9.mp4', 1186, 1280, 720, 'final_remotion_shorts_9x16.mp4'),
        ('final_remotion_shorts_9x16.mp4', 1186, 720, 1280, None),
    ]:
        path = P / name
        probe = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', path]))
        v = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        a = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
        assert (v['width'], v['height'], int(v['nb_frames']), v['r_frame_rate']) == (width, height, frames, '30/1')
        assert v['codec_name'] == 'h264' and v['pix_fmt'] in ('yuv420p', 'yuvj420p')
        assert a['codec_name'] == 'aac' and a['sample_rate'] == '48000'
        if audio_source:
            assert aac(path) == aac(P / audio_source)
        run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'null', '-'])
        samples = []
        for frame in ([0, 910, 911, 952, 993, 994, 1133, 1185] if frames == 1186 else [952, 1210, 20439]):
            target = OUT / f'{path.stem}-{frame:05d}.png'
            run(['ffmpeg', '-v', 'error', '-ss', str(frame / 30), '-i', path, '-frames:v', '1', '-y', target])
            samples.append(str(target.relative_to(P)))
        records.append({'file': name, 'sha256': digest(path), 'bytes': path.stat().st_size,
                        'frames': frames, 'width': width, 'height': height, 'fps': 30,
                        'durationSeconds': frames / 30, 'fullDecodePassed': True,
                        'audioSha256': aac(path), 'audioMatches': audio_source, 'samples': samples})
    record = {'checkedAt': datetime.now(timezone.utc).isoformat(), 'baselineCommit': 'd49cbdab',
              'change': 'intro-08 display text: 移動 → 異動', 'displayOnlyDifferencePassed': True,
              'voiceAndTimingUnchanged': True, 'visualReview': 'pending',
              'subjectiveListening': False, 'outputs': records}
    (P / 'caption_fix_v8.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: r[k] for k in ['file', 'sha256', 'durationSeconds']} for r in records], ensure_ascii=False))


if __name__ == '__main__':
    main()
