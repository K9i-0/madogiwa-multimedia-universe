"""Phrase-safe captions with VOICEVOX phoneme timing (no synthesis).

Default: update src/edit-manifest-v2.json and write captions-plan-v2.json.
Review v1 without modifying it:
  python prepare_captions_v2.py --input src/edit-manifest.json --plan-only

The local VOICEVOX audio_query endpoint is used only to identify the reading of
a caption prefix. Timing comes from the *saved synthesis query*, never from a
new duration prediction. No external service or new audio generation is used.
"""
from __future__ import annotations

import argparse
import ctypes
import functools
import json
import math
import re
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

P = Path(__file__).resolve().parent
MAX_PAGE = 46.0
MAX_LINE = 28.0
TERMS = [
    'Claude Code', 'Flutter Scene', 'MiniMax H3', 'Three.js', 'VOICEVOX',
    'Codex', 'Blender', 'Cursor', 'Tripo', 'Remotion', 'Studio', 'Python',
    'GitHub', 'API', 'AR', '3D', 'Wan', '福ギュン', '窓際族物語',
]
READINGS = {
    'Tripo': 'トリポ', 'Three.js': 'スリージェイエス', 'Blender': 'ブレンダー',
    'Cursor': 'カーソル', 'Flutter Scene': 'フラッターシーン', 'Studio': 'スタジオ',
    'Python': 'パイソン', '3D': 'スリーディー', 'AR': 'エーアール',
    'Claude Code': 'クロードコード', 'Codex': 'コーデックス', 'Remotion': 'リモーション',
    'Wan 3.0': 'ワン、サンテンゼロ', 'Wan': 'ワン', 'API': 'エーピーアイ',
    'AI': 'エーアイ', 'H3': 'エイチスリー', 'MiniMax': 'ミニマックス',
    '福ギュン': 'ふくぎゅん', 'Web': 'ウェブ', 'GitHub': 'ギットハブ',
}
# Reviewed semantic page boundaries for reused lines. Exact text matching means
# a later rewrite is never accidentally paired with a stale caption plan.
REVIEWED_PAGES = [
    ['基準になるキャラクターシートです。', '顔、体格、服、後ろ姿など、', 'どんなキャラクターを作るのかを決めます。'],
    ['動作自体も、既存のアニメーションを体格に合わせたり、コードで作ったりします。', '形の生成と、動作を作る工程は分けています。'],
    ['次は動画です。いま中央に出しているモデルも、Three.jsで表示し、', 'Remotionの時間に合わせて動かしています。'],
    ['ゲームでも使っています。', '窓際族物語ではFlutter Sceneでモデルを描画し、', '移動やゲームの処理と組み合わせています。'],
    ['まずはWebサイトです。', '今回紹介した3Dモデルは、窓際族物語の公式サイトでも触れるようにしています。'],
    ['この四枚をTripoへ渡します。', 'リポジトリでは、画像の場所や生成設定をファイルに書いて、', 'Pythonのスクリプトから送信しています。'],
    ['この二つの生成工程だけなら、そのくらいです。', 'ただし、キャラクターシートの準備や、作り直し、Codexなどの利用料は含んでいません。'],
]


def width(text):
    return sum(1 if unicodedata.east_asian_width(c) in 'FWA' else .55 for c in text)


class CFRange(ctypes.Structure):
    _fields_ = [('location', ctypes.c_long), ('length', ctypes.c_long)]


class JapaneseWords:
    """macOS system dictionary; no project dependency or package installation."""
    def __init__(self):
        self.cf = None
        try:
            cf = ctypes.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
            signatures = {
                'CFStringCreateWithCString': ([ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32], ctypes.c_void_p),
                'CFLocaleCreate': ([ctypes.c_void_p, ctypes.c_void_p], ctypes.c_void_p),
                'CFStringTokenizerCreate': ([ctypes.c_void_p, ctypes.c_void_p, CFRange, ctypes.c_ulong, ctypes.c_void_p], ctypes.c_void_p),
                'CFStringTokenizerAdvanceToNextToken': ([ctypes.c_void_p], ctypes.c_ulong),
                'CFStringTokenizerGetCurrentTokenRange': ([ctypes.c_void_p], CFRange),
                'CFRelease': ([ctypes.c_void_p], None),
            }
            for name, (args, result) in signatures.items():
                getattr(cf, name).argtypes = args
                getattr(cf, name).restype = result
            self.cf = cf
        except OSError:
            pass

    def tokens(self, text):
        if self.cf is None:
            return [(m.start(), m.end(), m.group()) for m in re.finditer(r'[A-Za-z0-9_.]+|[一-龥々]+[ぁ-ん]*|[ァ-ヴー]+|[ぁ-ん]+', text)]
        cf = self.cf
        raw = text.encode('utf-16-le')
        s = cf.CFStringCreateWithCString(None, text.encode(), 0x08000100)
        ja = cf.CFStringCreateWithCString(None, b'ja', 0x08000100)
        locale = cf.CFLocaleCreate(None, ja)
        tokenizer = cf.CFStringTokenizerCreate(None, s, CFRange(0, len(raw)//2), 0, locale)
        out = []
        try:
            while cf.CFStringTokenizerAdvanceToNextToken(tokenizer):
                r = cf.CFStringTokenizerGetCurrentTokenRange(tokenizer)
                start = len(raw[:r.location*2].decode('utf-16-le'))
                token = raw[r.location*2:(r.location+r.length)*2].decode('utf-16-le')
                out.append((start, start+len(token), token))
        finally:
            for obj in [tokenizer, locale, ja, s]:
                cf.CFRelease(obj)
        return out


WORDS = JapaneseWords()


def safe_breaks(text):
    """Return bunsetsu-like boundaries, prioritizing actual punctuation."""
    breaks = {0: 0, len(text): 0}
    for m in re.finditer(r'[。！？!?]+\s*|[、,：:；;]+\s*', text):
        breaks[m.end()] = 0 if re.search(r'[。！？!?]', m.group()) else 1
    tokens = WORDS.tokens(text)
    particles = {'は', 'が', 'を', 'に', 'へ', 'で', 'と', 'の', 'も', 'から', 'まで', 'より', 'なら', 'ので', 'けど', 'ながら', 'たり'}
    glue = {'て', 'で', 'い', 'いる', 'います', 'ます', 'まし', 'ました', 'です', 'でした', 'する', 'し', 'さ', 'れ', 'れる', 'ない', 'なかっ', 'た', 'だ', 'か', 'くらい', 'ぐらい', '用', '化', '的'}
    for i, (start, end, token) in enumerate(tokens):
        nxt = tokens[i+1][2] if i+1 < len(tokens) else ''
        if token in particles and nxt not in glue and nxt not in particles:
            breaks[end] = min(breaks.get(end, 99), 3)
        # Before a full word is an emergency fallback; never split inflections.
        if start and token not in particles | glue and len(token) >= 2:
            breaks[start] = min(breaks.get(start, 99), 7)
    for term in TERMS:
        for m in re.finditer(re.escape(term), text):
            breaks = {i: cost for i, cost in breaks.items() if not m.start() < i < m.end()}
    # Do not leave punctuation or a closing bracket at the next line's head.
    return {i: cost for i, cost in breaks.items() if i in (0, len(text)) or text[i] not in '、。！？!?）」』】,.;: '}


def wrap(text):
    if width(text) <= MAX_LINE:
        return text
    candidates = []
    for i, cost in safe_breaks(text).items():
        if i in (0, len(text)):
            continue
        left, right = text[:i].rstrip(), text[i:].lstrip()
        if max(width(left), width(right)) <= MAX_LINE:
            candidates.append((cost*1.6 + abs(width(left)-width(right))*.32, i))
    if not candidates:
        raise ValueError(f'No phrase-safe two-line wrap: {text}')
    _, cut = min(candidates)
    return text[:cut].rstrip()+'\n'+text[cut:].lstrip()


def pages_for(text, seconds):
    for pages in REVIEWED_PAGES:
        if ''.join(pages) == text:
            return pages
    if width(text) <= MAX_PAGE and seconds <= 7.2:
        return [text]
    breaks = safe_breaks(text)
    points = sorted(breaks)
    target = min(34, max(22, width(text)/seconds*5.8))
    # Dynamic programming keeps punctuation and text intact, while avoiding a
    # long static caption and a one-word flash such as "そうです。".
    best = {0: (0.0, [])}
    for end in points[1:]:
        options = []
        for start in points:
            if start >= end or start not in best:
                continue
            part = text[start:end].strip()
            w = width(part)
            if w > MAX_PAGE:
                continue
            try:
                wrap(part)
            except ValueError:
                continue
            span_seconds = seconds*w/max(1, width(text))
            # A page turn is stronger than a line break: do not hide a noun's
            # predicate behind the next page merely to balance page lengths.
            boundary_cost = {0: 0, 1: .8, 3: 14, 7: 28}[breaks[end]]
            cost = 2 + ((w-target)/target)**2*6 + boundary_cost
            if span_seconds > 7.5:
                cost += (span_seconds-7.5)**2*3
            if w < 9:
                cost += (9-w)*1.5
            options.append((best[start][0]+cost, best[start][1]+[part]))
        if options:
            best[end] = min(options, key=lambda x: x[0])
    if len(text) not in best:
        raise ValueError(f'Cannot paginate safely: {text}')
    return best[len(text)][1]


@functools.lru_cache(maxsize=None)
def prefix_moras(text):
    spoken = text
    for source, target in READINGS.items():
        spoken = spoken.replace(source, target)
    url = 'http://127.0.0.1:50021/audio_query?' + urllib.parse.urlencode({'speaker': 61, 'text': spoken})
    req = urllib.request.Request(url, data=b'', method='POST')
    with urllib.request.urlopen(req, timeout=10) as response:
        q = json.load(response)
    return [m['text'] for p in q['accent_phrases'] for m in p['moras']]


def query_timeline(query):
    scale = query['speedScale']
    t = query['prePhonemeLength']/scale
    out = []
    for phrase in query['accent_phrases']:
        for mora in phrase['moras']:
            duration = ((mora.get('consonant_length') or 0) + mora['vowel_length'])/scale
            out.append((mora['text'], t, t+duration))
            t += duration
        if phrase.get('pause_mora'):
            t += phrase['pause_mora']['vowel_length']/scale
    return out, t+query['postPhonemeLength']/scale


def fallback_pause(row, fraction, fps):
    """Explicit fallback: a low-energy local pause, not a char-count cut."""
    envelope = row.get('envelope', [])
    estimate = row['durationInFrames']*fraction
    if not envelope:
        return round(estimate), 'estimated-no-envelope'
    peak = max(envelope) or 1
    lo = max(1, round(estimate-.75*fps))
    hi = min(len(envelope)-1, round(estimate+.75*fps))
    candidates = [(sum(envelope[max(0,i-1):i+2])/3/peak + abs(i-estimate)/fps*.04, i) for i in range(lo, hi+1)]
    return min(candidates)[1], 'waveform-pause-estimate'


def caption_row(row, fps):
    pages = row.get('captionPages') or pages_for(row['text'], row['durationInFrames']/fps)
    if ''.join(pages) != row['text']:
        raise ValueError(f'Caption text differs from dialogue: {row["id"]}')
    if len(pages) == 1:
        return [{'startFrame': 0, 'endFrame': row['durationInFrames'], 'text': wrap(pages[0])}], []
    query = row.get('voiceSettings', {}).get('query')
    timing, predicted_total = query_timeline(query) if query else (None, None)
    total = row['durationInFrames']/fps
    # The saved query's total and actual synthesis are within a few frames.
    # Calibrate only this small edge discrepancy, preserving relative phonemes.
    ratio = total/predicted_total if predicted_total and abs(total-predicted_total)<.25 else 1
    starts = [0]
    audit = []
    prefix = ''
    for i, part in enumerate(pages[:-1]):
        prefix += part
        method = None
        detail = {}
        if timing:
            try:
                moras = prefix_moras(prefix)
                all_moras = [m[0] for m in timing]
                if moras != all_moras[:len(moras)]:
                    raise ValueError('prefix reading differs from saved query')
                left = timing[len(moras)-1][2]*ratio
                right = timing[len(moras)][1]*ratio
                # Hold the old caption through its last phoneme; show the next
                # one shortly before the next phrase, in the actual pause.
                cut_seconds = max(left, right-.10) if right-left >= .12 else (left+right)/2
                cut = round(cut_seconds*fps)
                method = 'saved-voicevox-phoneme-boundary'
                detail = {'previousSpeechEnd': round(left, 4), 'nextSpeechStart': round(right, 4)}
            except Exception as exc:
                detail['alignmentWarning'] = str(exc)
        if method is None:
            cut, method = fallback_pause(row, width(prefix)/width(row['text']), fps)
        cut = min(row['durationInFrames']-1, max(starts[-1]+1, cut))
        starts.append(cut)
        audit.append({'page': i+2, 'frame': cut, 'seconds': round(cut/fps, 4), 'method': method, **detail})
    ends = starts[1:]+[row['durationInFrames']]
    segments = [{'startFrame': start, 'endFrame': end, 'text': wrap(page)} for page, start, end in zip(pages, starts, ends)]
    return segments, audit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='src/edit-manifest-v2.json')
    parser.add_argument('--plan', default='captions-plan-v2.json')
    parser.add_argument('--plan-only', action='store_true')
    args = parser.parse_args()
    source = P/args.input
    manifest = json.loads(source.read_text())
    fps = manifest['composition']['fps']
    rows, warnings = [], []
    for row in manifest['dialogue']:
        segments, audit = caption_row(row, fps)
        row['captionSegments'] = segments
        for seg in segments:
            if (seg['endFrame']-seg['startFrame'])/fps < 1.2:
                warnings.append({'id': row['id'], 'reason': 'page under 1.2 seconds', 'text': seg['text']})
            assert max(map(width, seg['text'].split('\n'))) <= MAX_LINE
            assert width(seg['text'].replace('\n', '')) <= MAX_PAGE
        for a in audit:
            if a['method'] != 'saved-voicevox-phoneme-boundary':
                warnings.append({'id': row['id'], **a})
        rows.append({'id': row['id'], 'who': row['who'], 'text': row['text'], 'seconds': row['durationInFrames']/fps, 'pages': [{**s, 'seconds': round((s['endFrame']-s['startFrame'])/fps, 3)} for s in segments], 'boundaries': audit})
    plan = {'source': args.input, 'fontSize': 32, 'captionWidth': 940, 'maxFullwidthEquivalentPerLine': MAX_LINE, 'maxFullwidthEquivalentPerPage': MAX_PAGE, 'alignment': 'Saved VOICEVOX query phoneme durations; waveform fallback explicitly marked.', 'warnings': warnings, 'utterances': rows}
    (P/args.plan).write_text(json.dumps(plan, ensure_ascii=False, indent=2)+'\n')
    if not args.plan_only:
        source.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'rows': len(rows), 'pages': sum(len(r['pages']) for r in rows), 'boundaries': sum(len(r['boundaries']) for r in rows), 'warnings': warnings, 'updatedManifest': not args.plan_only}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
