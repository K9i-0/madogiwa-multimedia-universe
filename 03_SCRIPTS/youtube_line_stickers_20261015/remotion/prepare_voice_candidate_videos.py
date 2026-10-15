"""Build audition-only opening timelines and mixes without replacing adopted inputs.

The first 16 turns keep their text, visual states, and measured inter-turn gaps.
Only Yametaro's waveforms are substituted; speech is never time-stretched.
Run with the repository's Irodori-TTS virtual environment for numpy/soundfile.
"""
from pathlib import Path
import argparse
import copy
import json
import math
import hashlib
import subprocess
import numpy as np
import soundfile as sf

from prepare_voice import link_or_copy, sha, write_json
from mix_audio import decode, save, fade, loop_to, tones, music_inputs, SR, SAMPLES_PER_FRAME

P = Path(__file__).resolve().parent
FPS = 30
# Auditions compare the original Irodori voice even after a candidate is adopted.
BASELINE_COMMIT = '61f44365'
BASELINE_PATH = '03_SCRIPTS/youtube_line_stickers_20261015/remotion/src/edit-manifest.json'
LABELS = {
    'current': '現行 Irodori',
    'aoyama': 'A 青山龍星（ノーマル）',
    'kurono': 'B 玄野武宏（ノーマル）',
    'shirakami': 'C 白上虎太郎（ふつう）',
}


def make_candidate(key, index, original, source_hash):
    directory = P / 'out/voice-candidates' / key
    directory.mkdir(parents=True, exist_ok=True)
    public = P / 'public/voice-candidates' / key
    public.mkdir(parents=True, exist_ok=True)
    source_rows = original['dialogue'][:16]
    assert source_rows[-1]['id'] == 'main-03'
    overrides = {row['id']: row for row in index['lines']} if index else {}
    if index:
        assert set(overrides) == {row['id'] for row in source_rows if row['who'] == 'yametaro'}
    rows = []
    cursor = source_rows[0]['startFrame']
    for i, source in enumerate(source_rows):
        row = copy.deepcopy(source)
        if row['id'] in overrides:
            replacement = overrides[row['id']]
            assert replacement['text'] == row['text'] and replacement['who'] == row['who']
            audio = Path(replacement['audio'])
            assert sha(audio) == replacement['audioSha256']
            target = public / f'{row["id"]}_{replacement["audioSha256"][:12]}.wav'
            link_or_copy(audio, target)
            wave, sr = sf.read(audio)
            assert wave.ndim == 1 and len(wave) and np.isfinite(wave).all()
            frames = math.ceil(len(wave) / sr * FPS)
            row.update(audio=str(target.relative_to(P / 'public')),
                audioSha256=sha(audio), durationInFrames=frames,
                durationSeconds=len(wave)/sr, sampleRate=sr,
                spoken=replacement['spoken'], kana=replacement.get('kana'),
                voiceSettings={'model':f'VOICEVOX:{index["speakerName"]}',
                    'speakerId':index['speakerId'], 'style':index['style'],
                    'engineVersion':index['engineVersion'], 'query':replacement['query']},
                envelope=[round(float(np.sqrt(np.mean(chunk*chunk))) if len(chunk) else 0, 5)
                    for frame in range(frames)
                    for chunk in [wave[round(frame*sr/FPS):round((frame+1)*sr/FPS)]]])
            for stale in ['generatedAudio','generatedAudioSha256','audioProcessing','reusedFrom']:
                row.pop(stale, None)
        # All opening captions are single pages, so the approved layout remains exact.
        assert len(row['captionSegments']) == 1
        row['captionSegments'][0].update(startFrame=0, endFrame=row['durationInFrames'])
        row['startFrame'] = cursor
        rows.append(row)
        if i+1 < len(source_rows):
            original_gap = source_rows[i+1]['startFrame'] - source['startFrame'] - source['durationInFrames']
            assert original_gap >= 0
            cursor += row['durationInFrames'] + original_gap
    end = rows[-1]['startFrame'] + rows[-1]['durationInFrames'] + 90
    manifest = dict(composition={**original['composition'], 'durationInFrames':end},
        dialogue=rows, clips=[], audioSrc=f'voice-candidates/{key}/mixed.wav',
        mainStartFrame=next(row['startFrame'] for row in rows if row['id']=='main-01'),
        endingStartFrame=end, creditsStartFrame=end, creditsInDescription=True,
        auditionOnly=True, sourceManifestSha256=source_hash, sourceCommit=BASELINE_COMMIT)
    n = end*SAMPLES_PER_FRAME
    sources = music_inputs()
    voice = np.zeros((n,2), np.float32)
    for row in rows:
        audio = P/'public'/row['audio']
        assert sha(audio) == row['audioSha256']
        sound = decode(audio, 'loudnorm=I=-18:TP=-2:LRA=11')
        assert len(sound) <= row['durationInFrames']*SAMPLES_PER_FRAME + SAMPLES_PER_FRAME
        start = row['startFrame']*SAMPLES_PER_FRAME
        assert start + len(sound) <= n
        voice[start:start+len(sound)] += sound
    save(directory/'voice_unmixed.wav', voice)
    voice = decode(directory/'voice_unmixed.wav','loudnorm=I=-18:TP=-2:LRA=11')[:n]
    if len(voice) < n:
        voice = np.pad(voice, ((0,n-len(voice)),(0,0)))
    bgm = np.zeros((n,2),np.float32)
    main_start = manifest['mainStartFrame']*SAMPLES_PER_FRAME
    intro = decode(P/'public/intro.mp3','loudnorm=I=-34:TP=-3:LRA=11')
    bgm[:main_start] = fade(loop_to(intro,main_start),SR//2,SR)
    main = decode(P/'public/main.wav','loudnorm=I=-34:TP=-3:LRA=11')
    bgm[main_start:] = fade(loop_to(main,n-main_start),round(.6*SR),4*SR)
    effects = np.zeros((n,2),np.float32)
    notification = next(row['startFrame'] for row in rows if row['id']=='intro-04')-12
    final_intro = next(row for row in rows if row['id']=='intro-13')
    title = final_intro['startFrame']+final_intro['durationInFrames']+24
    events = [
        ('notification',notification,tones([(0,880,.5,.045),(.14,1174.66,.6,.04)],.8)),
        ('title',title,tones([(0,523.25,.65,.03),(.18,659.25,.7,.028),(.36,783.99,1.1,.026)],2)),
    ]
    for name,frame,sound in events:
        start = frame*SAMPLES_PER_FRAME
        effects[start:start+len(sound)] += sound
        if name=='title':
            bgm[start:start+len(sound)] *= .2
    mixed = voice+bgm+effects
    peak = float(np.max(np.abs(mixed)))
    gain = min(1,.95/peak)
    mixed *= gain
    save(public/'mixed.wav',mixed)
    label = LABELS.get(key,index.get('label',key) if index else key)
    props = {'manifest':manifest,'candidateLabel':label}
    write_json(directory/'props.json',props)
    write_json(directory/'mix_record.json',{'candidate':key,'label':label,
        'sourceManifestSha256':manifest['sourceManifestSha256'],
        'mixSha256':sha(public/'mixed.wav'),'musicInputs':sources,
        'voiceTargetLUFS':-18,'bgmTargetLUFS':-34,'sampleRate':SR,
        'premasterPeak':peak,'masterGain':gain,
        'soundEvents':[{'name':name,'startFrame':frame} for name,frame,_ in events],
        'currentTakosanAudioUnchanged':all(row['audioSha256']==source['audioSha256']
            for row,source in zip(rows,source_rows) if row['who']=='takosan'),
        'speechTimeStretch':False,'additionalPostSynthesisVoiceCuts':False,
        'subjectiveListening':False})
    print(f'READY {key} {end/FPS:.3f}s {directory / "props.json"}',flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('candidates',nargs='+',help='current or a key with out/voice-candidates/<key>/index.json')
    args=parser.parse_args()
    baseline=subprocess.check_output(['git','show',f'{BASELINE_COMMIT}:{BASELINE_PATH}'],cwd=P)
    original=json.loads(baseline)
    source_hash=hashlib.sha256(baseline).hexdigest()
    assert all('Irodori' in row['voiceSettings']['model'] for row in original['dialogue'][:16] if row['who']=='yametaro')
    manifest_hash=sha(P/'src/edit-manifest.json')
    master_hash=sha(P/'public/mixed.wav')
    for key in args.candidates:
        assert key.replace('_','').isalnum()
        index=None if key=='current' else json.loads((P/'out/voice-candidates'/key/'index.json').read_text())
        make_candidate(key,index,original,source_hash)
    assert sha(P/'src/edit-manifest.json')==manifest_hash
    assert sha(P/'public/mixed.wav')==master_hash


if __name__=='__main__':
    main()
