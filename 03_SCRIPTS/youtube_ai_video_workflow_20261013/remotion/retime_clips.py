"""Rebuild absolute timing after clip edits, preserving adopted audio and local cues."""
from pathlib import Path
from collections import defaultdict
import json
import re

P = Path(__file__).resolve().parent
m = json.loads((P / 'src/edit-manifest.json').read_text())
clips_after = defaultdict(list)
for clip in json.loads((P / 'clips_config.json').read_text()):
    clips_after[clip['afterId']].append(clip)
assert set(clips_after) <= {d['id'] for d in m['dialogue']}
cursor = 75
clips = []
for d in m['dialogue']:
    d['startFrame'] = cursor
    cursor += d['durationInFrames'] + d.get('pause', 9)
    for c in clips_after[d['id']]:
        cursor += c.get('pauseBeforeFrames', 0)
        clips.append(dict(c, startFrame=cursor))
        cursor += c['durationInFrames'] + c.get('pauseAfterFrames', 15)
m['clips'] = clips
m['composition']['durationInFrames'] = cursor + 60
m['creditsStartFrame'] = cursor + 60
m['mainStartFrame'] = next(d['startFrame'] for d in m['dialogue'] if d['id'] == 'v015')
m['endingStartFrame'] = next(d['startFrame'] for d in m['dialogue'] if d['id'] == 'v110')
(P / 'src/edit-manifest.json').write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n')

chapters = []
for d in m['dialogue']:
    if not any(c['chapter'] == d['chapter'] for c in chapters):
        f = d['startFrame'] if chapters else 0
        secs = f // 30
        chapters.append({'chapter': d['chapter'], 'startFrame': f, 'youtubeTime': f'{secs//60:02}:{secs%60:02}'})
(P.parent / 'chapters_v7.json').write_text(json.dumps(chapters, ensure_ascii=False, indent=2) + '\n')
p = P.parent / 'youtube_description.txt'
s = p.read_text()
a, b = s.index('チャプター\n'), s.index('\n制作リポジトリ')
p.write_text(s[:a] + 'チャプター\n' + '\n'.join(c['youtubeTime'] + ' ' + re.sub(r'^\d+\. ', '', c['chapter']) for c in chapters) + '\n' + s[b:])
print('Retimed:', m['composition']['durationInFrames'], 'frames;', m['composition']['durationInFrames'] / 30, 'seconds')
