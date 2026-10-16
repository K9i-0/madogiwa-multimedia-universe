#!/usr/bin/env python3
"""Audit rendered Shorts without changing queue readiness or publishing anything.

Examples:
  python3 03_SCRIPTS/shorts_sobaya_20261016/audit_completed.py --groups group-c.json --out technical-audit-group-c.json
  python3 03_SCRIPTS/shorts_sobaya_20261016/audit_completed.py --groups group-a.json group-b.json group-c.json group-root.json --out technical-audit.json
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess

Q = Path(__file__).resolve().parent
ROOT = Q.parents[1]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def probe(path):
    return json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)
    ]))


def audio_hash(path, start=0, duration=None):
    command = ['ffmpeg', '-v', 'error', '-threads', '1']
    if start:
        command += ['-ss', str(start)]
    command += ['-i', str(path), '-map', '0:a:0', '-c', 'copy']
    if duration is not None:
        command += ['-t', str(duration)]
    command += ['-f', 'hash', '-hash', 'sha256', '-']
    return subprocess.check_output(command, text=True).strip().split('=', 1)[1]


def audit(row):
    slug = row['slug']
    output = ROOT / row['output']
    manifest = ROOT / row['manifest']
    if not output.exists() or not manifest.exists():
        return {'slug': slug, 'passed': False, 'incomplete': True, 'reason': 'Output or manifest missing'}
    try:
        m = read(manifest)
        source = ROOT / row['source']
        adopted_audio = ROOT / m.get('audioSource', m['source'])
        source_info, final_info = probe(source), probe(output)
        original_video = next(s for s in source_info['streams'] if s['codec_type'] == 'video')
        video = next(s for s in final_info['streams'] if s['codec_type'] == 'video')
        audio = next(s for s in final_info['streams'] if s['codec_type'] == 'audio')
        fps = Fraction(str(m['fps']))
        frames = int(video['nb_frames'])
        duration = float(final_info['format']['duration'])
        source_duration = float(source_info['format']['duration'])
        start = m.get('trimStartFrame', 0) / float(fps)
        audio_duration = m['durationInFrames'] / float(fps) if m.get('trimAudio') else None
        original_audio_hash = audio_hash(adopted_audio, start, audio_duration)
        final_audio_hash = audio_hash(output)
        captions = m.get('captions', [])
        caption_bounds = all(
            isinstance(c['startFrame'], int) and isinstance(c['endFrame'], int)
            and 0 <= c['startFrame'] < c['endFrame'] <= m['durationInFrames']
            and 1 <= len(c['text'].splitlines()) <= 3
            for c in captions
        )
        ordered = sorted(captions, key=lambda c: c['startFrame'])
        caption_overlap = all(a['endFrame'] <= b['startFrame'] for a, b in zip(ordered, ordered[1:]))
        decode = subprocess.run(
            ['ffmpeg', '-v', 'error', '-threads', '1', '-i', str(output), '-f', 'null', '-'],
            capture_output=True, text=True, timeout=600,
        )
        checks = {
            'resolution': (video['width'], video['height']) == (720, 1280),
            'sourceAtMost101': 0 < source_duration <= 101,
            'outputAtMost101': 0 < duration <= 101,
            'fps': Fraction(video['r_frame_rate']) == fps == Fraction(original_video['r_frame_rate']),
            'frames': frames == m['durationInFrames'],
            'audio': final_audio_hash == original_audio_hash,
            'decode': decode.returncode == 0 and not decode.stderr.strip(),
            'captions': caption_bounds and caption_overlap,
        }
        result = {
            'slug': slug, 'passed': all(checks.values()), 'checks': checks,
            'sha256': sha(output), 'sourceSha256': sha(source), 'manifestSha256': sha(manifest),
            'duration': duration, 'sourceDuration': source_duration,
            'width': video['width'], 'height': video['height'],
            'fps': video['r_frame_rate'], 'frames': frames, 'audioCodec': audio['codec_name'],
            'audioStreamSha256': final_audio_hash, 'adoptedAudioStreamSha256': original_audio_hash,
            'audioUnchanged': final_audio_hash == original_audio_hash,
            'bytes': output.stat().st_size, 'decodeErrors': decode.stderr.strip(),
            'captionCount': len(captions),
        }
        print(slug, 'PASS' if result['passed'] else 'FAIL', flush=True)
        return result
    except Exception as exc:
        return {'slug': slug, 'passed': False, 'error': f'{type(exc).__name__}: {exc}'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--groups', nargs='+', required=True, help='Group JSON paths relative to this batch')
    parser.add_argument('--out', default='technical-audit.json', help='Result JSON path relative to this batch')
    parser.add_argument('--workers', type=int, default=2)
    args = parser.parse_args()
    rows = [row for group in args.groups for row in read(Q / group)]
    slugs = [row['slug'] for row in rows]
    if len(set(slugs)) != len(slugs):
        parser.error('Duplicate slug in requested groups')
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        videos = list(pool.map(audit, rows))
    result = {
        'checkedAt': dt.datetime.now(dt.timezone.utc).isoformat(),
        'scope': 'Completed outputs from the named groups only; readiness and publication are unchanged',
        'allPassed': bool(videos) and all(v['passed'] for v in videos),
        'listeningAudit': False,
        'listeningNote': 'Technical and subtitle-timing checks do not claim human listening or visual review.',
        'videos': videos,
    }
    target = Q / args.out
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'passed': sum(v['passed'] for v in videos), 'total': len(videos), 'output': str(target)}, ensure_ascii=False))
    if not result['allPassed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
