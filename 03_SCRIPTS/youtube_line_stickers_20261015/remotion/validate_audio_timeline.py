"""Verify delivered waveforms, caption text, and integer-frame voice placement."""
from pathlib import Path
import hashlib
import json
import math
import wave
from PIL import ImageFont
from prepare_voice import write_json

P = Path(__file__).resolve().parent
m = json.loads((P / 'src/edit-manifest.json').read_text())
fps = m['composition']['fps']
assert fps == 30
assert m['audioSrc'] == 'mixed.wav'
ids = [row['id'] for row in m['dialogue']]
assert len(ids) == len(set(ids))
previous_end = 0
items = []
font = ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc', 29)
for row in m['dialogue']:
    assert isinstance(row['startFrame'], int) and row['startFrame'] >= previous_end
    source = P / 'public' / row['audio']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row['audioSha256']
    with wave.open(str(source)) as wav:
        seconds = wav.getnframes() / wav.getframerate()
        assert wav.getnchannels() == 1
    assert math.ceil(seconds * fps) == row['durationInFrames']
    assert len(row['envelope']) == row['durationInFrames']
    segments = row['captionSegments']
    assert ''.join(segment['text'].replace('\n', '') for segment in segments) == row['text']
    end = 0
    widths = []
    for segment in segments:
        assert segment['startFrame'] == end
        assert segment['endFrame'] > end
        assert len(segment['text'].splitlines()) <= 2
        end = segment['endFrame']
        widths.extend(font.getlength(line) for line in segment['text'].splitlines())
    assert end == row['durationInFrames']
    assert max(widths) <= 770
    previous_end = row['startFrame'] + row['durationInFrames']
    items.append({'id': row['id'], 'durationSeconds': seconds, 'maxCaptionWidth': max(widths), 'captionPages': len(segments)})
assert 0 < m['mainStartFrame'] < m['endingStartFrame'] < m['composition']['durationInFrames']
assert previous_end < m['composition']['durationInFrames']
with wave.open(str(P / 'public/mixed.wav')) as wav:
    assert wav.getnchannels() == 2 and wav.getframerate() == 48000
    assert wav.getnframes() == m['composition']['durationInFrames'] * 1600
write_json(P / 'out/audio_timeline_validation.json', {'passed': True, 'utterances': len(items),
    'durationSeconds': m['composition']['durationInFrames']/fps, 'maxCaptionWidth': max(item['maxCaptionWidth'] for item in items),
    'captionTextMatches': True, 'noDialogueOverlaps': True, 'waveformHashesMatch': True,
    'subjectiveListening': False, 'items': items})
print('PASS', len(items), 'utterances;', m['composition']['durationInFrames']/fps, 'seconds')
