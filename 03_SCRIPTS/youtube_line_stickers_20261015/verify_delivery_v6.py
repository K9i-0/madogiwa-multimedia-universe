"""Verify v6 feedback, measured timing, preserved v5 voices and adopted evidence.

Preflight checks the script, original voices, captions, source evidence and mix.
The final pass decodes the actual MP4 and extracts representative/boundary frames.
Neither a passing script nor ASR is a substitute for listening and visual review.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import subprocess
import wave
from PIL import Image, ImageDraw

from verify_delivery import run, timecode

P = Path(__file__).resolve().parent
R = P.parents[1]
BASELINE = 'bc765980'
YAMETARO_REF_HASH = 'ede825a58cf1920f1bdfb353eea17d0feb24f20592d7f36d7c5c22c5ab60530b'


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def load(path):
    return json.loads(path.read_text())


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def require(condition, message, *details):
    if not condition:
        raise AssertionError((message, *details))


def git_bytes(commit, path):
    return subprocess.check_output(['git', '-C', str(R), 'show', f'{commit}:{path}'])


def check_history():
    history = load(P / 'first_set_alpha_history.json')
    require(history['sourceAuthenticity']['noGeneratedOrArtificialDamage'] is True,
            'Historical before example must not have generated/artificial damage')
    require(bool(history['implementation']['intentionalOutline']),
            'Intentional readability outlines must be distinguished from residual background')
    checked = []
    for source in history['historicalArtifacts']:
        data = git_bytes(source['commit'], source['path'])
        actual = hashlib.sha256(data).hexdigest()
        if source.get('sha256'):
            require(actual == source['sha256'], 'Historical Git source hash mismatch', source['stage'])
        checked.append({**source, 'verifiedSha256': actual})
    local = []
    for source in history['localResearchArtifacts']:
        path = P / source['file']
        if path.exists():
            require(digest(path) == source['sha256'], 'Historical comparison or screenshot changed', source['file'])
            local.append(source)
    public_checked = []
    assets = load(P / 'asset_sources_v5.json')
    asset_index = load(P / 'remotion/src/tips-assets.json')['images']
    for item in assets['records']:
        if 'adoptedInput' in item:
            actual = digest(R / item['adoptedInput'])
            require(actual == item['sha256'], 'Adopted historical input changed', item['adoptedInput'])
            if 'commit' in item:
                blob_hash = hashlib.sha256(git_bytes(item['commit'], item['gitPath'])).hexdigest()
                require(actual == blob_hash, 'Historical input differs from Git blob', item['adoptedInput'])
        elif 'source' in item:
            require(digest(R / item['source']) == item['sourceSha256'],
                    'Visual source SHA differs', item['key'])
        if 'output' in item:
            output = P / 'remotion/public' / item['output']
            require(digest(output) == item['outputSha256'], 'Visual output SHA differs', item['key'])
            require(asset_index[item['key']]['path'] == item['output'], 'Visual index points to wrong file', item['key'])
            with Image.open(R / item['source']) as source:
                source.seek(item.get('frame', 0))
                expected = source.convert('RGBA')
                if item.get('crop'):
                    expected = expected.crop(item['crop'])
                with Image.open(output) as image:
                    actual = image.convert('RGBA')
                    require(actual.size == expected.size and actual.tobytes() == expected.tobytes(),
                            'Historical rendered asset is not a pixel-exact decode/crop', item['key'])
            public_checked.append({'key': item['key'], 'path': item['output'],
                                   'sha256': item['outputSha256'], 'pixelExact': True})
    require({'historySobayaBefore', 'historySobayaAfter', 'historyReport'}.issubset(
        {item['key'] for item in public_checked}), 'Missing genuine before/after/report assets')
    return {'gitSources': checked, 'localEvidenceHashes': local, 'renderedAssetEvidence': public_checked,
            'intentionalOutlineIsNotFailure': True,
            'sourceAuthenticity': history['sourceAuthenticity'],
            'evidenceLimit': history['evidenceLimit']}


def check_script(rows, script):
    by_id = {row['id']: row for row in rows}
    require(len(rows) == len(by_id) == len(script), 'Duplicate/missing dialogue IDs')
    fields = ('id', 'who', 'text', 'view', 'chapter')
    require([[row[key] for key in fields] for row in rows] ==
            [[row[key] for key in fields] for row in script], 'Manifest differs from approved script')
    require(all(row['who'] in {'yametaro', 'takosan'} for row in rows), 'Unexpected cast')
    require({row['chapter'] for row in rows} == set(range(10)), 'Expected 10 narrative chapters')
    require(not {'intro-11', 'intro-12', 'intro-13'}.intersection(by_id),
            'Discarded post-Python opening lines returned')
    intro = [row for row in rows if row['id'].startswith('intro-')]
    require(intro and intro[-1]['id'] == 'intro-10', 'Cold open must end at the Python joke')
    require('Python' in by_id['intro-10']['text'], 'Missing approved final opening joke')
    require('よーたんからや' in by_id['intro-04']['text'], 'Missing notification reaction')
    text = '\n'.join(row['text'] for row in rows)
    for phrase in ['栄転だそうです', '廃村に栄転することある']:
        require(phrase not in text, 'Deleted joke returned', phrase)
    # User-approved wording is checked independently of row numbering.
    for phrase in ['馴れ馴れしかったものを選びました', 'どういう選定基準やねん',
                   'スタンプでも、窓際に異動してるんやな。さすがそば屋さんや！',
                   'そば屋さんが脱ぐとか誰得って感じやしな', 'そば屋マニア']:
        require(phrase in text, 'Missing adopted feedback line', phrase)
    require('第一弾' in text and '第二弾' in text, 'Both sets must be identified')
    require('OpenCV' in text and 'ImageMagick' in text, 'Missing image-processing explanation')
    require('OpenAI公式のLINEスタンプ制作法' not in text, 'Pets attribution overstates the source')
    require(by_id['intro-08']['text'] == 'ガチの島流しやないか！ワイ明日から廃村ゆめみ村に移動らしいわ…',
            'Missing extended island-exile reaction')
    require(by_id['close-05']['text'] == 'やっぱやめさんも窓際族ですね' or
            by_id['close-05']['text'] == 'やっぱやめさんも窓際族ですね。',
            'Final punchline differs from feedback')
    require(rows[-1]['id'] == 'close-05' and 'close-06' not in by_id,
            'Stop the conversation after Takosan final punchline')
    require('道具' not in text, 'All current dialogue must use ツール')
    for row in script:
        if '案出し' in row['text']:
            require('あんだし' in row.get('reading', '') or
                    'アンダシ' in row.get('reading', '') or
                    'アンダシ' in row.get('voicevoxReading', ''),
                    'Explicit あんだし pronunciation is required', row['id'])
    required_ids = {f'tips-plan-{i:02}' for i in range(1, 3)} | {
        f'ideas-speed-{i:02}' for i in range(1, 4)} | {
        f'settings-{i:02}' for i in range(1, 6)} | {'acting-06b', 'acting-06c'}
    require(required_ids.issubset(by_id), 'Missing new feedback dialogue', sorted(required_ids-set(by_id)))
    require('プランの選び方' in by_id['tips-plan-01']['text'] and
            'コンテンツ制作' in by_id['tips-plan-02']['text'],
            'Missing ChatGPT plan-video exchange')
    speed_text = ''.join(by_id[f'ideas-speed-{i:02}']['text'] for i in range(1, 4))
    require('Imagegen' in speed_text and '回数' in speed_text and
            ('速' in speed_text or '早' in speed_text),
            'Explain fewer Imagegen calls and faster ideation')
    settings_text = ''.join(by_id[f'settings-{i:02}']['text'] for i in range(1, 6))
    require(all(term in settings_text for term in ['GPT 6 Astra', 'Light', 'Ultra']) and
            ('好み' in settings_text or '好き' in settings_text),
            'Include personal GPT 6 Astra Light/Ultra workflow and audience preference')
    require('そば屋さんの扱い' in by_id['acting-06b']['text'] and
            'そば屋だから仕方ない' in by_id['acting-06c']['text'],
            'Missing new Sobaya exchange')
    source = (P / 'remotion/src/Explainer.tsx').read_text()
    require('isTitleCard' not in source and 'titleStart' not in source,
            'Retired green title screen is still in active source')
    for name in ['TipsVisualAid.tsx', 'SpreadsheetFrame.tsx']:
        require('道具' not in (P / 'remotion/src' / name).read_text(),
                'Active on-screen text still uses 道具', name)
    return by_id


def check_audio(rows, adopted, baseline_rows, allow_regenerated):
    adopted_by_id = {item['id']: item for item in adopted}
    require(len(adopted) == len(adopted_by_id) == len(rows), 'Adopted audio inventory mismatch')
    require(set(adopted_by_id) == {row['id'] for row in rows}, 'Adopted audio IDs differ')
    # Archive old audio elsewhere; episode-root voice files are the active adopted set.
    require({path.name for path in P.glob('voice_*.wav')} == {item['file'] for item in adopted},
            'Episode-root voice inventory contains stale/missing adopted files')
    baseline = {row['id']: row for row in baseline_rows}
    reused, regenerated, changed = [], [], []
    cast_counts = {'yametaro': 0, 'takosan': 0}
    for row in rows:
        item = adopted_by_id[row['id']]
        require(item['who'] == row['who'], 'Adopted speaker differs', row['id'])
        require(item['publicAudio'] == row['audio'], 'Adopted public path differs', row['id'])
        public = P / 'remotion/public' / row['audio']
        actual = digest(public)
        require(actual == digest(P / item['file']) == item['sha256'] == row['audioSha256'],
                'Adopted/public/manifest audio SHA mismatch', row['id'])
        with wave.open(str(public), 'rb') as wav:
            require(wav.getframerate() == 48000 and wav.getnchannels() == 1,
                    'Utterance must be mono 48 kHz', row['id'])
            expected_frames = (wav.getnframes() * 30 + wav.getframerate() - 1) // wav.getframerate()
            require(expected_frames == row['durationInFrames'], 'Measured utterance timing mismatch', row['id'])
        settings = row['voiceSettings']
        if row['who'] == 'yametaro':
            require(settings['model'] == 'Aratako/Irodori-TTS-v4.1-Small', 'Yametaro must use regular Irodori', row['id'])
            require(settings['reference'] == '02_CHARACTERS/Yametaro_voice.wav' and
                    settings['referenceSha256'] == YAMETARO_REF_HASH,
                    'Yametaro canonical reference changed', row['id'])
        else:
            require(settings['model'] == 'VOICEVOX:中国うさぎ' and settings['speakerId'] == 61,
                    'Takosan cast differs', row['id'])
            query = settings['query']
            require(query['speedScale'] == 1.1 and query['pitchScale'] == 0,
                    'Takosan standard voice settings differ', row['id'])
        cast_counts[row['who']] += 1
        original = baseline.get(row['id'])
        unchanged_text = original and all(row.get(key) == original.get(key)
                                         for key in ('who', 'text', 'reading', 'voicevoxReading'))
        if unchanged_text:
            evidence = {'id': row['id'], 'baselineSha256': original['audioSha256'], 'audioSha256': actual}
            if actual == original['audioSha256']:
                reused.append(evidence)
            else:
                require(row['id'] in allow_regenerated,
                        'Unchanged line regenerated without an intentional exception', row['id'])
                regenerated.append(evidence)
        else:
            changed.append({'id': row['id'], 'audioSha256': actual, 'newId': original is None})
    require(digest(R / '02_CHARACTERS/Yametaro_voice.wav') == YAMETARO_REF_HASH,
            'Canonical Yametaro voice file changed')
    return {'baselineCommit': BASELINE, 'castCounts': cast_counts, 'unchangedAudio': reused,
            'intentionallyRegeneratedSameText': regenerated, 'newOrRewrittenLines': changed,
            'adoptedAudioHashes': 'passed'}


def check_captions(rows, comp):
    srt = []
    previous_end = 0
    for row in rows:
        require(isinstance(row['startFrame'], int) and isinstance(row['durationInFrames'], int),
                'Dialogue timing must use integer frames', row['id'])
        require(row['startFrame'] >= previous_end, 'Dialogue overlap', row['id'])
        previous_end = row['startFrame'] + row['durationInFrames']
        require(previous_end <= comp['durationInFrames'], 'Dialogue outside composition', row['id'])
        require(len(row['envelope']) == row['durationInFrames'] and
                all(math.isfinite(value) for value in row['envelope']), 'Invalid mouth envelope', row['id'])
        pages = row['captionSegments']
        require(''.join(page['text'].replace('\n', '') for page in pages) == row['text'],
                'Caption content differs from script', row['id'])
        require(pages[0]['startFrame'] == 0 and pages[-1]['endFrame'] == row['durationInFrames'],
                'Caption does not cover utterance', row['id'])
        for i, page in enumerate(pages):
            require(len(page['text'].splitlines()) <= 2, 'Caption exceeds two lines', row['id'], i)
            require(0 <= page['startFrame'] < page['endFrame'] <= row['durationInFrames'],
                    'Caption out of range', row['id'], i)
            if i:
                require(pages[i-1]['endFrame'] == page['startFrame'],
                        'Caption pages have a gap or overlap', row['id'], i)
            start = row['startFrame'] + page['startFrame']
            end = row['startFrame'] + page['endFrame']
            srt.append(f'{len(srt)+1}\n{timecode(start, comp["fps"])} --> {timecode(end, comp["fps"])}\n{page["text"]}\n')
    return srt


def collect_samples(rows, comp, intro_end):
    """Cover every layout, every joke and every caption/scene boundary in changed examples."""
    samples = {'opening-first': 30, 'transition-hold': intro_end + 5,
               'transition-fade-out': intro_end + 12, 'transition-white': intro_end + 18,
               'transition-fade-in': intro_end + 24, 'transition-greeting': intro_end + 30,
               'final-line-hold': rows[-1]['startFrame'] + rows[-1]['durationInFrames'] + 3,
               'final': comp['durationInFrames'] - 1}
    views = set()
    significant = ('馴れ馴れし', '選定基準', 'さすがそば屋', '誰得', 'そば屋マニア',
                   'OpenCV', 'ImageMagick', '消し残', '黒背景', '白背景')
    for i, row in enumerate(rows):
        start = row['startFrame']; end = start + row['durationInFrames']
        if row['view'] not in views:
            samples[f'view-{row["view"]}'] = start + row['durationInFrames']//2
            views.add(row['view'])
        key_example = (row['id'].startswith(('intro-', 'inspect-', 'tips-plan-', 'ideas-speed-', 'settings-')) or row['id'] in {'acting-06b', 'acting-06c', 'close-05'} or
                       any(phrase in row['text'] for phrase in significant) or
                       any(word in row['view'] for word in ('history', 'alpha', 'compare', 'outlook')))
        if key_example:
            for n, page in enumerate(row['captionSegments'], 1):
                samples[f'{row["id"]}-page-{n}'] = start + (page['startFrame'] + page['endFrame'])//2
        if i and rows[i-1]['view'] != row['view']:
            samples[f'cut-{row["id"]}-before'] = max(0, start - 1)
            samples[f'cut-{row["id"]}-after'] = start + min(2, row['durationInFrames']-1)
        if row['view'].endswith('-prompt'):
            next_start = rows[i+1]['startFrame'] if i+1 < len(rows) else comp['durationInFrames']
            if next_start - end > 15:
                samples[f'prompt-hold-{row["id"]}'] = min(end + 30, next_start - 1)
    return {re.sub(r'[^a-zA-Z0-9_-]', '_', name): frame for name, frame in samples.items()
            if 0 <= frame < comp['durationInFrames']}


def contact_sheets(audit, samples):
    """Compact indexes; full-resolution PNGs remain the visual-review authority."""
    sheets = []
    entries = list(samples.items())
    for offset in range(0, len(entries), 16):
        subset = entries[offset:offset+16]
        canvas = Image.new('RGB', (1280, math.ceil(len(subset)/4)*206), '#e8ece9')
        draw = ImageDraw.Draw(canvas)
        for index, (name, frame) in enumerate(subset):
            x = index % 4 * 320; y = index // 4 * 206
            with Image.open(audit / f'{name}.png') as source:
                canvas.paste(source.convert('RGB').resize((320, 180), Image.Resampling.LANCZOS), (x, y))
            draw.text((x+5, y+184), f'{name[:42]}  f{frame}', fill='#172d23')
        path = audit / f'contact-{offset//16+1:02}.jpg'
        canvas.save(path, quality=92)
        sheets.append(str(path.relative_to(P)))
    return sheets


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', default='final_remotion_line_stickers_v6.mp4')
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--allow-regenerated-id', action='append', default=['intro-04'])
    parser.add_argument('--skip-excerpts', action='store_true')
    args = parser.parse_args()
    manifest = load(P / 'remotion/src/edit-manifest.json')
    script = load(P / 'remotion/dialogue.json')
    adopted = load(P / 'adopted_audio.json')['audio']
    voice_records = load(P / 'voice_record.json')['lines']
    mix = load(P / 'mix_record.json')
    comp = manifest['composition']; rows = manifest['dialogue']; fps = comp['fps']
    require((comp['width'], comp['height'], fps) == (1280, 720, 30), 'Wrong composition format')
    by_id = check_script(rows, script)
    require([row['id'] for row in voice_records] == [row['id'] for row in rows],
            'Voice record IDs differ from manifest')
    for record, row in zip(voice_records, rows):
        for field in ('who', 'text', 'spoken', 'voiceSettings', 'audioSha256', 'durationInFrames', 'startFrame'):
            require(record[field] == row[field], 'Voice record differs from manifest', row['id'], field)
    baseline_path = str((P / 'remotion/src/edit-manifest.json').relative_to(R))
    baseline_rows = json.loads(git_bytes(BASELINE, baseline_path))['dialogue']
    audio_report = check_audio(rows, adopted, baseline_rows, set(args.allow_regenerated_id))
    screening = load(P / 'voice_audit_v6.json')
    screened = screening['changedUtterances']
    expected_screening = {item['id'] for item in audio_report['newOrRewrittenLines']} | {
        item['id'] for item in audio_report['intentionallyRegeneratedSameText']}
    require({item['id'] for item in screened} == expected_screening,
            'Voice screening does not cover exactly the new/changed audio')
    for item in screened:
        require(item['audioSha256'] == by_id[item['id']]['audioSha256'],
                'Voice screening is for a different waveform', item['id'])
        require(item['nonFiniteSamples'] == 0, 'Non-finite voice samples', item['id'])
    srt = check_captions(rows, comp)
    history = check_history()
    require(manifest['creditsInDescription'] is True and manifest['creditsStartFrame'] == comp['durationInFrames'],
            'Do not reintroduce a credits card')
    require(manifest['mainStartFrame'] == by_id['main-01']['startFrame'], 'Main start differs from greeting')
    intro_end = by_id['intro-10']['startFrame'] + by_id['intro-10']['durationInFrames']
    require(by_id['main-01']['startFrame'] == intro_end + 42,
            'White-dip transition must finish before greeting at Python end + 42 frames')
    events = mix['soundEvents']
    title_events = [event for event in events if 'title' in event['name'].lower()]
    notification_events = [event for event in events if 'notification' in event['name'].lower()]
    require(not title_events, 'Retired title cue must not return')
    require(len(notification_events) == 1, 'Missing/duplicate notification cue')
    require(mix.get('mainMusicStartFrame') == intro_end + 18,
            'Main music must enter at white-dip midpoint')
    require(0 <= by_id['intro-04']['startFrame'] - notification_events[0]['startFrame'] <= 30,
            'Notification must precede immediate reaction')
    require(digest(P / 'remotion/public' / manifest['audioSrc']) == mix['mixedSha256'], 'Mixed waveform hash differs')
    require(mix['frames'] == comp['durationInFrames'] and mix['sampleRate'] == 48000, 'Mix timeline differs')
    with wave.open(str(P / 'remotion/public' / manifest['audioSrc']), 'rb') as wav:
        require(wav.getnchannels() == 2 and wav.getframerate() == 48000, 'Mix must be stereo 48 kHz')
        require(wav.getnframes() == comp['durationInFrames'] * 1600, 'Mix sample count differs from frame timeline')
    audit = P / 'remotion/out/final-audit-v6'; audit.mkdir(parents=True, exist_ok=True)
    samples = collect_samples(rows, comp, intro_end)
    basic = {'version': 6, 'utterances': len(rows), 'subtitlePages': len(srt),
             'durationInFrames': comp['durationInFrames'], 'durationSeconds': comp['durationInFrames']/fps,
             'dialogueAndCaptionIntegrity': 'passed', 'coldOpenEndsAt': 'intro-10',
             'adoptedFeedbackLines': 'passed', 'finalSpokenLine': by_id['close-05']['text'],
             'transition': {'kind': 'whole-screen white dip', 'pythonEndFrame': intro_end,
                            'fadeOutFrames': [intro_end+6, intro_end+18],
                            'fadeInFrames': [intro_end+18, intro_end+30],
                            'greetingStartFrame': by_id['main-01']['startFrame']}, 'voiceAudit': audio_report, 'historicalAlphaEvidence': history,
             'newVoiceMachineScreening': {'record': 'voice_audit_v6.json',
                                         'sha256': digest(P / 'voice_audit_v6.json'),
                                         'utterances': len(screened), 'waveformHashesMatched': True,
                                         'subjectiveListening': False},
             'mixedSha256': mix['mixedSha256'], 'subjectiveListening': False,
             'plannedReviewFrames': len(samples)}
    save(audit / 'preflight.json', basic)
    if args.preflight:
        print(json.dumps({key: basic[key] for key in ('version', 'utterances', 'subtitlePages', 'durationSeconds', 'plannedReviewFrames')}, ensure_ascii=False))
        return
    video = P / args.video
    probe = json.loads(run(['ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', str(video)]))
    videos = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
    audios = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
    require(len(videos) == len(audios) == 1, 'Expected one video and one audio stream')
    stream = videos[0]; audio = audios[0]
    require((stream['width'], stream['height'], stream['r_frame_rate']) == (1280, 720, '30/1'), 'Final video format differs')
    require(int(stream['nb_read_frames']) == comp['durationInFrames'], 'Final video frame count differs')
    require(audio['sample_rate'] == '48000' and audio['channels'] == 2, 'Final audio format differs')
    decoded = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(video), '-f', 'null', '-'],
                             check=True, capture_output=True, text=True)
    require(not decoded.stderr.strip(), 'Final MP4 decoding emitted errors', decoded.stderr.strip())
    for name, frame in samples.items():
        run(['ffmpeg', '-v', 'error', '-y', '-ss', str(frame/fps), '-i', str(video), '-frames:v', '1', str(audit/f'{name}.png')])
    with Image.open(audit / 'transition-white.png') as image:
        # H.264 may introduce a small rounding error; the midpoint is intentionally white.
        histogram = image.convert('RGB').histogram()
        pixel_count = image.width * image.height
        white_channels = [sum(histogram[channel*256+248:(channel+1)*256]) / pixel_count
                          for channel in range(3)]
        require(min(white_channels) > .995, 'Transition midpoint is not full-screen white', white_channels)
    basic['transition']['encodedWhiteMidpointChannelFractions'] = white_channels
    sheets = contact_sheets(audit, samples)
    print('AUDIT_FRAMES_READY', json.dumps({'frames': len(samples), 'contactSheets': sheets},
                                        ensure_ascii=False), flush=True)
    excerpts = []
    if not args.skip_excerpts:
        opening_last = by_id['tips-second-03']
        ranges = [('preview_opening_v6.mp4', 0,
                   opening_last['startFrame'] + opening_last['durationInFrames'] + 18),
                  ('preview_settings_v6.mp4', by_id['settings-01']['startFrame'],
                   by_id['settings-05']['startFrame'] + by_id['settings-05']['durationInFrames'] + 18),
                  ('preview_ending_v6.mp4', by_id['close-04']['startFrame'], comp['durationInFrames'])]
        for name, start, end in ranges:
            run(['ffmpeg', '-v', 'error', '-y', '-ss', str(start/fps), '-i', str(video), '-t', str((end-start)/fps),
                 '-map', '0:v:0', '-map', '0:a:0', '-c:v', 'libx264', '-crf', '18', '-preset', 'fast',
                 '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(P/name)])
            excerpts.append({'file': name, 'startFrame': start, 'endFrame': end, 'durationSeconds': (end-start)/fps})
    require((P / 'subtitles_ja.srt').read_text().strip() == '\n'.join(srt).strip(),
            'Published SRT differs from measured caption pages')
    report = {**basic, 'video': video.name, 'sha256': digest(video), 'bytes': video.stat().st_size,
              'resolution': [stream['width'], stream['height']], 'fps': fps,
              'audio': {'codec': audio['codec_name'], 'sampleRate': int(audio['sample_rate']), 'channels': audio['channels']},
              'fullDecode': 'passed', 'excerpts': excerpts,
              'contactSheets': sheets,
              'reviewFrames': [{'id': key, 'frame': value, 'path': f'remotion/out/final-audit-v6/{key}.png'} for key, value in samples.items()],
              'note': 'Automated integrity/source checks and extracted frames are separate from subjective listening and visual review.'}
    save(audit / 'delivery_v6.json', report)
    print(json.dumps({key: report[key] for key in ('video', 'durationSeconds', 'bytes', 'utterances', 'subtitlePages', 'fullDecode')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
