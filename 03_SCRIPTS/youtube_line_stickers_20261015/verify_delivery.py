"""Validate the rendered master, export captions and an opening review excerpt."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

P = Path(__file__).resolve().parent


def run(args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def timecode(frame, fps):
    ms = round(frame * 1000 / fps)
    return f'{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', default='final_remotion_line_stickers.mp4')
    parser.add_argument('--section-excerpt', help='Optional filename for the Imagegen explanation excerpt')
    args = parser.parse_args()
    video = P / args.video
    manifest = json.loads((P / 'remotion/src/edit-manifest.json').read_text())
    script = json.loads((P / 'remotion/dialogue.json').read_text())
    comp = manifest['composition']
    fps = comp['fps']
    lines = manifest['dialogue']
    assert [d['id'] for d in script] == [d['id'] for d in lines]
    assert [d['text'] for d in script] == [d['text'] for d in lines]
    assert len(lines) == 91
    forbidden = ['栄転だそうです', '廃村に栄転することある']
    assert not any(x in d['text'] for x in forbidden for d in lines)
    assert next(d for d in lines if d['id'] == 'intro-09')['reading'] == '明日からハイソンエンジニアですね。'
    assert next(d for d in lines if d['id'] == 'intro-10')['reading'] == 'パイソンエンジニアみたいに言うな！'
    srt = []
    for row in lines:
        pages = row['captionSegments']
        assert ''.join(x['text'].replace('\n', '') for x in pages) == row['text']
        for page in pages:
            assert len(page['text'].splitlines()) <= 2
            assert 0 <= page['startFrame'] < page['endFrame'] <= row['durationInFrames']
            start = row['startFrame'] + page['startFrame']
            end = row['startFrame'] + page['endFrame']
            srt.append(f'{len(srt)+1}\n{timecode(start, fps)} --> {timecode(end, fps)}\n{page["text"]}\n')
    (P / 'subtitles_ja.srt').write_text('\n'.join(srt))
    probe = json.loads(run(['ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', str(video)]))
    stream = next(x for x in probe['streams'] if x['codec_type'] == 'video')
    audio = next(x for x in probe['streams'] if x['codec_type'] == 'audio')
    assert (stream['width'], stream['height']) == (1280, 720)
    assert stream['r_frame_rate'] == '30/1'
    assert int(stream['nb_read_frames']) == comp['durationInFrames']
    assert audio['sample_rate'] == '48000'
    run(['ffmpeg', '-v', 'error', '-i', str(video), '-f', 'null', '-'])
    audit = P / 'remotion/out/final-audit'
    audit.mkdir(parents=True, exist_ok=True)
    by_id = {x['id']: x for x in lines}
    ids = ['intro-04', 'intro-08', 'intro-09', 'intro-10', 'main-01', 'main-04', 'flow-03', 'sheet-04', 'sheet-08', 'motion-06', 'alpha-09', 'alpha-13', 'export-05', 'record-06', 'end-05']
    samples = []
    for id in ids:
        row = by_id[id]
        frame = row['startFrame'] + min(35, row['durationInFrames'] // 2)
        samples.append((id, frame))
    if args.section_excerpt:
        for id in ['flow-04', 'flow-05', 'flow-06', 'flow-07']:
            row = by_id[id]
            for index, page in enumerate(row['captionSegments']):
                frame = row['startFrame'] + (page['startFrame'] + page['endFrame']) // 2
                samples.append((f'{id}-page-{index+1}', frame))
        cleanup = P / 'remotion/voice_cleanup.json'
        if cleanup.exists():
            for cut in json.loads(cleanup.read_text())['cuts']:
                row = by_id[cut['id']]
                end = row['startFrame'] + row['durationInFrames']
                samples.extend([(f'voice-cut-{cut["id"]}-end', end - 1),
                    (f'voice-cut-{cut["id"]}-after', end + 2)])
    last = by_id['intro-13']
    samples.append(('title', last['startFrame'] + last['durationInFrames'] + 40))
    samples.append(('final', comp['durationInFrames'] - 1))
    for name, frame in samples:
        run(['ffmpeg', '-v', 'error', '-y', '-ss', str(frame / fps), '-i', str(video), '-frames:v', '1', str(audit / f'{name}.png')])
    intro_end = by_id['main-03']['startFrame'] + by_id['main-03']['durationInFrames'] + 15
    excerpt = P / 'preview_intro.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(video), '-t', str(intro_end / fps), '-map', '0:v:0', '-map', '0:a:0', '-c', 'copy', '-movflags', '+faststart', str(excerpt)])
    report = {
        'video': video.name,
        'sha256': hashlib.sha256(video.read_bytes()).hexdigest(),
        'bytes': video.stat().st_size,
        'durationInFrames': comp['durationInFrames'],
        'durationSeconds': comp['durationInFrames'] / fps,
        'resolution': [stream['width'], stream['height']],
        'fps': fps,
        'audio': {'codec': audio['codec_name'], 'sampleRate': int(audio['sample_rate']), 'channels': audio['channels']},
        'utterances': len(lines),
        'subtitlePages': len(srt),
        'fullDecode': 'passed',
        'dialogueAndCaptionIntegrity': 'passed',
        'requestedIntroRevisions': 'passed',
        'introExcerpt': excerpt.name,
        'reviewFrames': [{'id': id, 'frame': frame, 'path': f'remotion/out/final-audit/{id}.png'} for id, frame in samples],
        'subjectiveListening': False,
        'note': 'Machine checks do not constitute a subjective listening pass. Visual review is recorded separately in review.md.'
    }
    (P / 'delivery.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    if args.section_excerpt:
        section = P / args.section_excerpt
        start = by_id['flow-04']['startFrame']
        end = by_id['flow-08']['startFrame']
        run(['ffmpeg', '-v', 'error', '-y', '-ss', str(start / fps), '-i', str(video), '-t', str((end - start) / fps), '-map', '0:v:0', '-map', '0:a:0', '-c:v', 'libx264', '-crf', '18', '-preset', 'fast', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(section)])
        report['sectionExcerpt'] = {'file': section.name, 'startFrame': start, 'endFrame': end, 'durationSeconds': (end - start) / fps}
        (P / 'delivery.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['video', 'durationSeconds', 'bytes', 'fullDecode', 'introExcerpt']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
