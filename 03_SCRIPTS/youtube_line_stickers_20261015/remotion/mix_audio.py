"""Mix canonical narration, quiet adopted music, and two original tonal cues."""
from pathlib import Path
import json
import math
import subprocess
import wave
import numpy as np
from prepare_voice import link_or_copy, sha, write_json

P = Path(__file__).resolve().parent
R = P.parents[2]
SR = 48000
SAMPLES_PER_FRAME = 1600
MUSIC = {
    'intro.mp3': {
        'title': '昼下がり気分', 'author': 'KK',
        'url': 'https://opentracks.com/bgm/detail/4695',
        'originalGlob': '.local/voicevox-explainer/intro.mp3',
        'originalSha256': 'b3be5e54383b778ac1cd25ae21bc3597039989100853903dfe83d3a10ff471e4',
        'workingSha256': 'b3be5e54383b778ac1cd25ae21bc3597039989100853903dfe83d3a10ff471e4',
        'workingConversion': 'Unchanged distribution MP3, Track 1.',
    },
    'main.wav': {
        'title': 'ほのぼのワルツ【リコーダー】', 'author': 'エクシエ',
        'url': 'https://commons.nicovideo.jp/works/nc116360',
        'originalGlob': '03_SCRIPTS/youtube_explainer_pilot_20261008/input/nc116360_*.wav',
        'originalSha256': '93b3e15199b1a924854efed27c1e8762ef070874546a388a1a78da0764e8afc2',
        'workingSha256': '9ccfc9b032d1a1fd2e818f7128ba9a287f8c68344c5d18a3c8f01acb7399313f',
        'workingConversion': 'FFmpeg decode to 48000 Hz stereo float32, then PCM16 WAV using this script save(); no loudness change in the working input.',
    },
}


def decode(path, filters=None):
    command = ['ffmpeg', '-v', 'error', '-i', str(path)]
    if filters:
        command += ['-af', filters]
    raw = subprocess.check_output(command + ['-f', 'f32le', '-ar', str(SR), '-ac', '2', 'pipe:1'])
    return np.frombuffer(raw, dtype='<f4').reshape(-1, 2).copy()


def save(path, samples):
    with wave.open(str(path), 'wb') as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(SR)
        out.writeframes((np.clip(samples, -1, 1) * 32767).astype('<i2').tobytes())


def fade(samples, head, tail):
    head, tail = min(head, len(samples)), min(tail, len(samples))
    if head:
        samples[:head] *= np.linspace(0, 1, head)[:, None]
    if tail:
        samples[-tail:] *= np.linspace(1, 0, tail)[:, None]
    return samples


def loop_to(samples, target):
    if len(samples) >= target:
        return samples[:target].copy()
    cross = SR
    result = samples.copy()
    while len(result) < target:
        overlap = result[-cross:] * np.linspace(1, 0, cross)[:, None] + samples[:cross] * np.linspace(0, 1, cross)[:, None]
        result = np.concatenate([result[:-cross], overlap, samples[cross:]])
    return result[:target]


def tones(notes, duration):
    """Original sine/bell cue. Not a recording of LINE/Outlook notification audio."""
    mono = np.zeros(round(duration * SR), np.float32)
    for start, hz, length, amplitude in notes:
        count = round(length * SR)
        t = np.arange(count) / SR
        attack = np.minimum(1, t / .009)
        decay = np.exp(-6 * t / length)
        tone = (np.sin(2 * math.pi * hz * t) + .18 * np.sin(2 * math.pi * hz * 2 * t)) * attack * decay * amplitude
        index = round(start * SR)
        end = min(len(mono), index + count)
        mono[index:end] += tone[:end-index]
    return np.stack([mono, mono], axis=1)


def music_inputs():
    """Restore stable working inputs directly from locally retained distribution originals."""
    sources = {}
    for name, meta in MUSIC.items():
        originals = list(R.glob(meta['originalGlob']))
        assert len(originals) == 1, (name, originals)
        original = originals[0]
        assert sha(original) == meta['originalSha256'], original
        target = P / 'public' / name
        if not target.exists():
            if name == 'intro.mp3':
                link_or_copy(original, target)
            else:
                save(target, decode(original))
        assert sha(target) == meta['workingSha256'], target
        sources[name] = {**meta, 'canonicalOriginal': str(original.relative_to(R)),
            'workingInput': str(target.relative_to(R)), 'sha256': sha(target),
            'provenanceRecord': '03_SCRIPTS/youtube_explainer_pilot_20261008/asset_sources.json'}
    return sources


def main():
    m = json.loads((P / 'src/edit-manifest.json').read_text())
    assert m['composition']['fps'] == 30
    n = m['composition']['durationInFrames'] * SAMPLES_PER_FRAME
    sources = music_inputs()
    voice = np.zeros((n, 2), np.float32)
    for row in m['dialogue']:
        sound = decode(P / 'public' / row['audio'], 'loudnorm=I=-18:TP=-2:LRA=11')
        start = row['startFrame'] * SAMPLES_PER_FRAME
        assert start + len(sound) <= n
        voice[start:start+len(sound)] += sound
    save(P / 'out/voice_unmixed.wav', voice)
    voice = decode(P / 'out/voice_unmixed.wav', 'loudnorm=I=-18:TP=-2:LRA=11')[:n]
    if len(voice) < n:
        voice = np.pad(voice, ((0, n-len(voice)), (0, 0)))
    bgm = np.zeros((n, 2), np.float32)
    main_start = m['mainStartFrame'] * SAMPLES_PER_FRAME
    intro = decode(P / 'public/intro.mp3', 'loudnorm=I=-34:TP=-3:LRA=11')
    bgm[:main_start] = fade(loop_to(intro, main_start), SR//2, SR)
    main = decode(P / 'public/main.wav', 'loudnorm=I=-34:TP=-3:LRA=11')
    bgm[main_start:] = fade(loop_to(main, n-main_start), round(.6*SR), 4*SR)
    effects = np.zeros((n, 2), np.float32)
    sound_events = []
    cue_config = json.loads((P / 'sound_cues.json').read_text()) if (P / 'sound_cues.json').exists() else {}
    notification_id = cue_config.get('notificationBeforeId', 'intro-04')
    notification_line = next((row for row in m['dialogue'] if row['id'] == notification_id), None)
    if notification_line:
        start_frame = max(0, notification_line['startFrame'] - 12)
        cue = tones([(0, 880, .5, .045), (.14, 1174.66, .6, .04)], .8)
        start = start_frame * SAMPLES_PER_FRAME
        effects[start:start+len(cue)] += cue
        save(P / 'public/notification.wav', cue)
        sound_events.append({'name': 'original two-tone notification', 'startFrame': start_frame, 'durationInFrames': 24})
    final_intro = next((row for row in m['dialogue'] if row['id'] == 'intro-13'), None)
    if final_intro:
        start_frame = final_intro['startFrame'] + final_intro['durationInFrames'] + 24
        start = start_frame * SAMPLES_PER_FRAME
        cue = tones([(0, 523.25, .65, .03), (.18, 659.25, .7, .028), (.36, 783.99, 1.1, .026)], 2)
        effects[start:start+len(cue)] += cue
        bgm[start:start+len(cue)] *= .2
        save(P / 'public/title_jingle.wav', cue)
        sound_events.append({'name': 'original soft major triad title cue', 'startFrame': start_frame, 'durationInFrames': 60})
    mixed = voice + bgm + effects
    peak = float(np.max(np.abs(mixed)))
    master_gain = min(1, .95/peak)
    mixed *= master_gain
    save(P / 'public/mixed.wav', mixed)
    write_json(P.parent / 'mix_record.json', {'sampleRate': SR, 'frames': m['composition']['durationInFrames'],
        'voiceTargetLUFS': -18, 'perUtteranceNormalization': True, 'bgmTargetLUFS': -34,
        'endingTrack': 'ほのぼのワルツ【リコーダー】', 'endingTargetLUFS': -34,
        'endingLiftAfterDialogue': False, 'endingTrackChange': False, 'endingFadeOutSeconds': 4,
        'premasterPeak': peak, 'masterGain': master_gain, 'soundEvents': sound_events,
        'musicInputs': sources, 'mixedSha256': sha(P / 'public/mixed.wav'),
        'subjectiveListening': False})
    print('MIXED', n / SR, 'seconds; peak', peak, flush=True)


if __name__ == '__main__':
    main()
