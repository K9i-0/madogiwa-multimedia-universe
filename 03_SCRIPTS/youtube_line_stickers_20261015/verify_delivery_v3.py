"""Verify the human-technique revision and export captions/review excerpts."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

from verify_delivery import run, timecode

P = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', default='final_remotion_line_stickers_v3.mp4')
    args = parser.parse_args()
    video = P / args.video
    manifest = json.loads((P / 'remotion/src/edit-manifest.json').read_text())
    script = json.loads((P / 'remotion/dialogue.json').read_text())
    intro = json.loads((P / 'intro_reference_v2.json').read_text())['dialogue']
    adopted = json.loads((P / 'adopted_audio.json').read_text())['audio']
    comp = manifest['composition']
    fps = comp['fps']
    rows = manifest['dialogue']
    by_id = {row['id']: row for row in rows}
    assert len(rows) == len(by_id) == len(script) == len(adopted) == 89
    assert [(r['id'], r['who'], r['text']) for r in rows] == [(r['id'], r['who'], r['text']) for r in script]
    assert {r['chapter'] for r in rows} == set(range(10))
    assert not any(word in r['text'] for r in rows for word in ['栄転だそうです', '廃村に栄転することある'])
    for original in intro:
        current = by_id[original['id']]
        for key, value in original.items():
            assert current.get(key) == value, ('Opening changed', original['id'], key)
    expected_files = {r['file'] for r in adopted}
    assert {f.name for f in P.glob('voice_*.wav')} == expected_files
    for audio in adopted:
        digest = hashlib.sha256((P / audio['file']).read_bytes()).hexdigest()
        assert digest == audio['sha256'] == by_id[audio['id']]['audioSha256']
    srt = []
    previous_end = 0
    for row in rows:
        assert row['startFrame'] >= previous_end
        previous_end = row['startFrame'] + row['durationInFrames']
        assert previous_end <= comp['durationInFrames']
        pages = row['captionSegments']
        assert ''.join(page['text'].replace('\n', '') for page in pages) == row['text']
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
    assert (stream['width'], stream['height'], stream['r_frame_rate']) == (1280, 720, '30/1')
    assert int(stream['nb_read_frames']) == comp['durationInFrames']
    assert audio['sample_rate'] == '48000' and audio['channels'] == 2
    run(['ffmpeg', '-v', 'error', '-i', str(video), '-f', 'null', '-'])

    samples = {}
    for id in ['intro-04', 'intro-08', 'intro-09', 'intro-10', 'main-01', 'main-03', 'ideas-07', 'options-04', 'options-08', 'redraw-05', 'pets-04', 'acting-05', 'acting-13', 'inspect-03', 'tools-06', 'close-05', 'close-06']:
        row = by_id[id]
        samples[id] = row['startFrame'] + min(35, row['durationInFrames']//2)
    views = set()
    for row in rows[16:]:
        if row['view'] not in views:
            samples[f'view-{row["view"]}'] = row['startFrame'] + row['durationInFrames']//2
            views.add(row['view'])
        if row['view'].endswith('-prompt'):
            samples[f'prompt-hold-{row["id"]}'] = row['startFrame'] + row['durationInFrames'] + 30
    last_intro = by_id['intro-13']
    samples['title'] = last_intro['startFrame'] + last_intro['durationInFrames'] + 40
    samples['final'] = comp['durationInFrames'] - 1
    audit = P / 'remotion/out/final-audit-v3'
    audit.mkdir(parents=True, exist_ok=True)
    for name, frame in samples.items():
        run(['ffmpeg', '-v', 'error', '-y', '-ss', str(frame/fps), '-i', str(video), '-frames:v', '1', str(audit / f'{name}.png')])

    start = by_id['ideas-01']['startFrame']
    end = by_id['redraw-01']['startFrame']
    excerpt = P / 'preview_tips_v3.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-ss', str(start/fps), '-i', str(video), '-t', str((end-start)/fps), '-map', '0:v:0', '-map', '0:a:0', '-c:v', 'libx264', '-crf', '18', '-preset', 'fast', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(excerpt)])

    report = {
        'video': video.name,
        'sha256': hashlib.sha256(video.read_bytes()).hexdigest(),
        'bytes': video.stat().st_size,
        'durationInFrames': comp['durationInFrames'], 'durationSeconds': comp['durationInFrames']/fps,
        'resolution': [stream['width'], stream['height']], 'fps': fps,
        'audio': {'codec': audio['codec_name'], 'sampleRate': int(audio['sample_rate']), 'channels': audio['channels']},
        'utterances': len(rows), 'subtitlePages': len(srt),
        'fullDecode': 'passed', 'dialogueAndCaptionIntegrity': 'passed',
        'preservedOpening': {'reference': 'intro_reference_v2.json', 'utterances': len(intro), 'audioHashesAndTimingAndCaptions': 'passed'},
        'adoptedAudioHashes': 'passed',
        'techniqueExcerpt': {'file': excerpt.name, 'startFrame': start, 'endFrame': end, 'durationSeconds': (end-start)/fps},
        'reviewFrames': [{'id': key, 'frame': value, 'path': f'remotion/out/final-audit-v3/{key}.png'} for key, value in samples.items()],
        'subjectiveListening': False,
        'note': 'Automated checks and extracted frames are separate from subjective listening/continuous visual review.'
    }
    (P / 'delivery.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: report[k] for k in ['video', 'durationSeconds', 'bytes', 'utterances', 'subtitlePages', 'fullDecode']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
