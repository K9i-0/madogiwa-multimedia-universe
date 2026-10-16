"""Validate the two-line v7 revision while reusing v6 integrity/visual helpers.

Only v7 audit files and previews are written. Active delivery/SRT and all v6
artifacts remain owned by the main production workflow.
"""
import argparse
import hashlib
import json
import subprocess
import wave
from PIL import Image

import verify_delivery_v6 as base

P, R = base.P, base.R
BASELINE = '0a3e1f3f'
CHANGED = {'tips-01', 'settings-03'}
TEXT = {
    'tips-01': '第一弾に続いて、第二弾も販売に向けて準備中です。今回は、その二つを作る中で分かったコツを紹介します。',
    'settings-03': '仕上げは、同じモデルのUltraです。複数のエージェントで作業を分担して、並列に進められます。',
}
load, save, require, digest, run = base.load, base.save, base.require, base.digest, base.run


def baseline_json(relative):
    return json.loads(base.git_bytes(BASELINE, str((P / relative).relative_to(R))))


def check_retained():
    old = baseline_json('delivery.json')
    video = P / old['video']
    require(video.name == 'final_remotion_line_stickers_v6.mp4', 'Baseline delivery must be v6')
    require(digest(video) == old['sha256'], 'Approved v6 video has changed')
    retained = [{'file': video.name, 'sha256': old['sha256']}]
    for relative in ['voice_audit_v6.json', 'verify_delivery_v6.py', 'remotion/audit_voice_v6.py',
                     'thumbnails/thumbnail_youtube.jpg', 'thumbnails/thumbnail_youtube.png',
                     'thumbnails/selected_thumbnail.json']:
        expected = hashlib.sha256(base.git_bytes(BASELINE, str((P / relative).relative_to(R)))).hexdigest()
        require(digest(P / relative) == expected, 'Retained v6 audit/thumbnail changed', relative)
        retained.append({'file': relative, 'sha256': expected})
    return retained


def preflight():
    manifest = load(P / 'remotion/src/edit-manifest.json')
    rows, comp = manifest['dialogue'], manifest['composition']
    script = load(P / 'remotion/dialogue.json')
    by_id = base.check_script(rows, script)
    require(len(rows) == 107, 'v7 must retain all 107 dialogue lines')
    baseline_rows = baseline_json('remotion/src/edit-manifest.json')['dialogue']
    baseline_ids = {row['id']: row for row in baseline_rows}
    require([r['id'] for r in rows] == [r['id'] for r in baseline_rows], 'v7 changed dialogue inventory')
    for row in rows:
        if row['id'] in CHANGED:
            require(row['text'] == TEXT[row['id']] and row['who'] == 'takosan',
                    'Changed v7 line differs from approved text/cast', row['id'])
        else:
            for field in ['text', 'who', 'reading', 'voiceSettings', 'audioSha256']:
                require(row.get(field) == baseline_ids[row['id']].get(field),
                        'Unexpected change outside two requested lines', row['id'], field)
    visual = (P / 'remotion/src/TipsVisualAid.tsx').read_text()
    require(all(word in visual for word in ['審査中', '分担', '並列']), 'Missing v7 on-screen clarification')
    base.BASELINE = BASELINE  # Only the imported helper report label; no v6 file changes.
    audio = base.check_audio(rows, load(P / 'adopted_audio.json')['audio'], baseline_rows, set())
    require(len(audio['unchangedAudio']) == 105 and
            {r['id'] for r in audio['newOrRewrittenLines']} == CHANGED,
            'Exactly two rewritten / 105 unchanged voices are required')
    record = load(P / 'voice_record.json')['lines']
    require(len(record) == len(rows), 'Voice record count mismatch')
    for rec, row in zip(record, rows):
        for key in ['id', 'text', 'who', 'spoken', 'voiceSettings', 'audioSha256', 'startFrame', 'durationInFrames']:
            require(rec[key] == row[key], 'Voice record differs from timeline', row['id'], key)
    screening = load(P / 'voice_audit_v7.json')
    require({r['id'] for r in screening['changedUtterances']} == CHANGED and
            screening['allWaveformHashesVerified'] and
            screening['allUnchangedSettingsAndWaveformsPreserved'], 'Incomplete v7 voice screening')
    for row in screening['changedUtterances']:
        require(row['audioSha256'] == by_id[row['id']]['audioSha256'], 'Stale voice screening', row['id'])
        require(row['nonFiniteSamples'] == 0 and row['voicevoxMoraEvidence']['allTermsPresent'],
                'Voice waveform/mora integrity failed', row['id'])
    srt = base.check_captions(rows, comp)
    require((P / 'subtitles_ja.srt').read_text().strip() == '\n'.join(srt).strip(), 'Published SRT is stale')
    require((comp['width'], comp['height'], comp['fps']) == (1280, 720, 30), 'Wrong output format')
    require(manifest['creditsInDescription'] and manifest['creditsStartFrame'] == comp['durationInFrames'],
            'Credits must remain in the description')
    intro_end = by_id['intro-10']['startFrame'] + by_id['intro-10']['durationInFrames']
    require(manifest['mainStartFrame'] == by_id['main-01']['startFrame'] == intro_end+42,
            'Approved intro transition changed')
    mix = load(P / 'mix_record.json')
    require(mix['mainMusicStartFrame'] == intro_end+18 and
            not any('title' in e['name'] for e in mix['soundEvents']), 'Retired title transition returned')
    require(digest(P / 'remotion/public' / manifest['audioSrc']) == mix['mixedSha256'] and
            mix['frames'] == comp['durationInFrames'], 'Mixed audio differs from timeline')
    with wave.open(str(P / 'remotion/public' / manifest['audioSrc']), 'rb') as wav:
        require((wav.getnchannels(), wav.getframerate(), wav.getnframes()) ==
                (2, 48000, comp['durationInFrames']*1600), 'Mixed WAV format/length differs')
    # v6 already has a complete visual audit. Cover every layout in the new
    # encoded file, then inspect the two revised lines and affected transitions.
    all_samples = base.collect_samples(rows, comp, intro_end)
    samples = {name: frame for name, frame in all_samples.items()
               if name.startswith(('view-', 'transition-')) or
               name in {'opening-first', 'final-line-hold', 'final', 'close-05-page-1'}}
    for name in CHANGED:
        row = by_id[name]
        for index, page in enumerate(row['captionSegments'], 1):
            samples[f'{name}-page-{index}'] = row['startFrame']+(page['startFrame']+page['endFrame'])//2
            if index > 1:
                boundary = row['startFrame'] + page['startFrame']
                samples[f'{name}-page-{index}-before'] = boundary-1
                samples[f'{name}-page-{index}-start'] = boundary
        samples[f'{name}-end'] = row['startFrame']+row['durationInFrames']-1
    for name in ['tips-01', 'tips-second-01', 'settings-01', 'settings-04', 'options-01']:
        row = by_id[name]
        samples[f'cut-{name}-before'] = row['startFrame']-1
        samples[f'cut-{name}-after'] = row['startFrame']+1
    report = {'version': 7, 'baselineCommit': BASELINE, 'utterances': len(rows), 'subtitlePages': len(srt),
              'durationInFrames': comp['durationInFrames'], 'durationSeconds': comp['durationInFrames']/30,
              'dialogueAndCaptionIntegrity': 'passed', 'changedDialogueIds': sorted(CHANGED),
              'voiceAudit': audio, 'newVoiceMachineScreening': {'record': 'voice_audit_v7.json',
                  'sha256': digest(P / 'voice_audit_v7.json'), 'utterances': 2, 'subjectiveListening': False},
              'historicalAlphaEvidence': base.check_history(), 'retainedV6AndThumbnail': check_retained(),
              'mixedSha256': mix['mixedSha256'], 'plannedReviewFrames': len(samples),
              'subjectiveListening': False}
    return manifest, by_id, samples, report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', default='final_remotion_line_stickers_v7.mp4')
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--skip-excerpts', action='store_true')
    args = parser.parse_args()
    manifest, by_id, samples, report = preflight()
    comp = manifest['composition']; fps = comp['fps']
    audit = P / 'remotion/out/final-audit-v7'; audit.mkdir(parents=True, exist_ok=True)
    save(audit / 'preflight.json', report)
    if args.preflight:
        print(json.dumps({k:report[k] for k in ['version','utterances','subtitlePages','durationSeconds','plannedReviewFrames']}))
        return
    video = P / args.video
    require(video.resolve() != (P/'final_remotion_line_stickers_v6.mp4').resolve(), 'Do not overwrite v6')
    probe = json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]))
    videos = [s for s in probe['streams'] if s['codec_type']=='video']
    audios = [s for s in probe['streams'] if s['codec_type']=='audio']
    require(len(videos)==len(audios)==1, 'Expected one video and one audio stream')
    v,a = videos[0],audios[0]
    require((v['width'],v['height'],v['r_frame_rate'],int(v['nb_read_frames'])) ==
            (1280,720,'30/1',comp['durationInFrames']), 'Final video format/frame count mismatch')
    require((a['sample_rate'],a['channels'])==('48000',2), 'Final audio format mismatch')
    decoded = subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],
                             check=True,capture_output=True,text=True)
    require(not decoded.stderr.strip(), 'Final video decode error', decoded.stderr)
    for name,frame in samples.items():
        run(['ffmpeg','-v','error','-y','-ss',str(frame/fps),'-i',str(video),'-frames:v','1',str(audit/f'{name}.png')])
    with Image.open(audit/'transition-white.png') as image:
        histogram=image.convert('RGB').histogram(); count=image.width*image.height
        require(min(sum(histogram[c*256+248:(c+1)*256])/count for c in range(3))>.995,
                'White transition midpoint changed')
    sheets=base.contact_sheets(audit,samples)
    print('AUDIT_FRAMES_READY',json.dumps({'frames':len(samples),'contactSheets':sheets}),flush=True)
    excerpts=[]
    if not args.skip_excerpts:
        for name,first,last in [('preview_second_set_v7.mp4','tips-01','tips-second-03'),
                                ('preview_settings_v7.mp4','settings-01','settings-05')]:
            start=by_id[first]['startFrame']; end=by_id[last]['startFrame']+by_id[last]['durationInFrames']+18
            run(['ffmpeg','-v','error','-y','-ss',str(start/fps),'-i',str(video),'-t',str((end-start)/fps),
                 '-map','0:v:0','-map','0:a:0','-c:v','libx264','-crf','18','-preset','fast',
                 '-c:a','aac','-b:a','192k','-movflags','+faststart',str(P/name)])
            excerpts.append({'file':name,'startFrame':start,'endFrame':end,'durationSeconds':(end-start)/fps})
    report.update(video=video.name,sha256=digest(video),bytes=video.stat().st_size,resolution=[1280,720],fps=30,
        audio={'codec':a['codec_name'],'sampleRate':48000,'channels':2},fullDecode='passed',excerpts=excerpts,
        contactSheets=sheets,reviewFrames=[{'id':k,'frame':f,'path':f'remotion/out/final-audit-v7/{k}.png'} for k,f in samples.items()],
        note='Automated source, waveform and timing checks are separate from subjective listening and visual review.')
    save(audit/'delivery_v7.json',report)
    print(json.dumps({k:report[k] for k in ['video','durationSeconds','bytes','utterances','subtitlePages','fullDecode']}))


if __name__ == '__main__':
    main()
