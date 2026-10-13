"""Adopt the v8 voice inputs and measured chapters without duplicating old WAVs."""
from pathlib import Path
import hashlib
import json
import os
import re

P = Path(__file__).resolve().parent
m = json.loads((P / 'src/edit-manifest.json').read_text())
previous = {}
for file in P.parent.glob('*adopted_audio*.json'):
    for item in json.loads(file.read_text()).get('audio', []):
        previous[item['sha256']] = item['file']
items = []
for d in m['dialogue']:
    src = P / 'public' / d['audio']
    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    dst = P.parent / previous.get(digest, f"v8_{d['id']}_{d['who']}.wav")
    if dst.exists():
        assert hashlib.sha256(dst.read_bytes()).hexdigest() == digest
    else:
        os.link(src, dst)
    items.append({'id': d['id'], 'file': dst.name, 'publicAudio': d['audio'], 'sha256': digest, 'who': d['who']})
(P.parent / 'adopted_audio_v8.json').write_text(json.dumps({'version': 8, 'audio': items}, ensure_ascii=False, indent=2) + '\n')
chapters = []
for d in m['dialogue']:
    if not any(c['chapter'] == d['chapter'] for c in chapters):
        frame = d['startFrame'] if chapters else 0
        seconds = frame // 30
        chapters.append({'chapter': d['chapter'], 'startFrame': frame, 'youtubeTime': f'{seconds//60:02}:{seconds%60:02}'})
(P.parent / 'chapters_v8.json').write_text(json.dumps(chapters, ensure_ascii=False, indent=2) + '\n')
path = P.parent / 'youtube_description.txt'
s = path.read_text()
a, b = s.index('チャプター\n'), s.index('\n制作リポジトリ')
s = s[:a] + 'チャプター\n' + '\n'.join(c['youtubeTime'] + ' ' + re.sub(r'^\d+\. ', '', c['chapter']) for c in chapters) + '\n' + s[b:]
s = s.replace('完成稿v7。', '完成稿v8。')
a, b = s.index('説明用の固定換算'), s.index('本編の金額は動画生成分のみ。')
s = s[:a] + '''説明用の固定換算1ドル160円で、30秒あたり通常価格は約240円／480円／960円。
確認時点では30%引きの表示があり、割引価格は480p $0.035/秒、720p $0.07/秒、1080p $0.14/秒。同じ換算で30秒あたり約168円／336円／672円です。
適用条件・最新料金は利用時に確認してください。実際の請求額は為替・割引・決済条件等で変わります。
窓際族物語の制作実績では、30秒の完成動画1本に平均約300円、作り直しを含む生成量は約60秒分が目安です。厳密な料金表の試算とは別の概算実績で、スキルの改善や必要部分だけの再生成で費用を抑えています。
''' + s[b:]
path.write_text(s)
sources = json.loads((P.parent / 'sources_v8.json').read_text())
sources['chapters'] = chapters
sources['delivery'].update(durationInFrames=m['composition']['durationInFrames'], durationSeconds=m['composition']['durationInFrames']/30)
(P.parent / 'sources_v8.json').write_text(json.dumps(sources, ensure_ascii=False, indent=2) + '\n')
print('Adopted', len(items), 'voices;', m['composition']['durationInFrames']/30, 'seconds')
