"""Readable two-line captions, aligned to VOICEVOX mora lengths where available."""
from pathlib import Path
import json
import re
import urllib.parse
import urllib.request
from PIL import ImageFont
from prepare_voice import replacements, write_json

P = Path(__file__).resolve().parent
font = ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc', 29)
cachefile = P / 'out/prefix_queries.json'
cache = json.loads(cachefile.read_text()) if cachefile.exists() else {}


def mora_count(text):
    for a, b in replacements.items():
        text = text.replace(a, b)
    if text not in cache:
        url = 'http://127.0.0.1:50021/audio_query?' + urllib.parse.urlencode({'speaker': 61, 'text': text})
        query = json.load(urllib.request.urlopen(urllib.request.Request(url, data=b'', method='POST')))
        cache[text] = sum(len(phrase['moras']) for phrase in query['accent_phrases'])
    return cache[text]


def frame_at(row, position):
    if position <= 0:
        return 0
    if position >= len(row['text']):
        return row['durationInFrames']
    query = row['voiceSettings'].get('query')
    if not query:
        return round(row['durationInFrames'] * position / len(row['text']))
    target = mora_count(row['text'][:position])
    seconds = query['prePhonemeLength']
    count = 0
    for phrase in query['accent_phrases']:
        for mora in phrase['moras']:
            if count >= target:
                return min(row['durationInFrames'] - 1, round(seconds / query['speedScale'] * 30))
            seconds += (mora.get('consonant_length', 0) or 0) + mora['vowel_length']
            count += 1
        if phrase.get('pause_mora'):
            seconds += phrase['pause_mora']['vowel_length']
    return min(row['durationInFrames'] - 1, round(seconds / query['speedScale'] * 30))


def wrap(text):
    if font.getlength(text) <= 770:
        return text
    candidates = []
    protected_spans = [match.span() for token in ['Codex Pets', 'Imagegen', 'OpenAI', 'OpenCV', 'ImageMagick', 'こういう'] for match in re.finditer(re.escape(token), text)]
    for i in range(1, len(text)):
        if any(start < i < end for start, end in protected_spans):
            continue
        if text[i] in '、。！？）」』…' or text[i-1] in '「『（':
            continue
        if re.match(r'[A-Za-z0-9]', text[i-1]) and re.match(r'[A-Za-z0-9]', text[i]):
            continue
        widths = [font.getlength(text[:i]), font.getlength(text[i:])]
        if max(widths) > 770:
            continue
        score = max(widths) + abs(widths[0] - widths[1]) * .2 - (1000 if text[i-1] in '。！？' else 800 if text[i-1] in '、' else 200 if text[i-1] in 'はがをにでとへもや' else 0)
        candidates.append((score, i))
    if not candidates:
        return None
    i = min(candidates)[1]
    return text[:i] + '\n' + text[i:]


def split(text):
    if wrap(text):
        return [text]
    positions = [match.end() for match in re.finditer('[。！？、]', text) if match.end() < len(text)]
    choices = [i for i in positions if wrap(text[:i])]
    sentence_choices = [i for i in choices if text[i-1] in '。！？']
    i = max(sentence_choices or choices) if choices else max(i for i in range(1, len(text)) if wrap(text[:i]))
    return [text[:i]] + split(text[i:])


def main():
    m = json.loads((P / 'src/edit-manifest.json').read_text())
    overrides_file = P / 'caption_layout.json'
    overrides = json.loads(overrides_file.read_text()) if overrides_file.exists() else {}
    for row in m['dialogue']:
        segments = []
        position = 0
        for chunk in overrides.get(row['id'], split(row['text'])):
            start = frame_at(row, position)
            position += len(chunk.replace('\n', ''))
            segments.append({'startFrame': start, 'endFrame': frame_at(row, position), 'text': chunk if '\n' in chunk else wrap(chunk)})
        assert ''.join(segment['text'].replace('\n', '') for segment in segments) == row['text']
        assert all(segment['endFrame'] > segment['startFrame'] for segment in segments)
        assert all(len(segment['text'].splitlines()) <= 2 for segment in segments)
        row.update(captionSegments=segments, caption=segments[0]['text'], captionFontSize=29)
    write_json(P / 'src/edit-manifest.json', m)
    write_json(cachefile, cache)
    chapters = []
    for row in m['dialogue']:
        if not any(chapter['chapter'] == row['chapter'] for chapter in chapters):
            chapters.append({'chapter': row['chapter'], 'startFrame': row['startFrame'] if chapters else 0})
    for i, chapter in enumerate(chapters):
        chapter['durationInFrames'] = (chapters[i+1]['startFrame'] if i+1 < len(chapters) else m['composition']['durationInFrames']) - chapter['startFrame']
    write_json(P.parent / 'chapters.json', chapters)
    print('CAPTIONS', sum(len(row['captionSegments']) for row in m['dialogue']), 'CHAPTERS', chapters)


if __name__ == '__main__':
    main()
