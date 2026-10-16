#!/usr/bin/env python3
"""Refresh the requested Markdown after all newly edited Shorts pass integration."""
import json
from pathlib import Path
from collections import Counter
B=Path(__file__).resolve().parents[1];R=B.parents[1]
read=lambda p:json.loads(p.read_text())
rows=read(B/'site-inventory-source.json')['episodes'];new=read(B/'queue.json')
assert len(new)==34 and all(r['status'] in ('ready','published') for r in new)
N={r['slug']:r for r in new}
def length(n):return f'{int(n)//60}:{n%60:05.2f}'
def site(r):return f"[{r['title']}](https://madogiwa.work/episodes/{r['slug']})"
def prompt(r):return 'あり' if r['prompt_available'] else 'なし'
def category(r):
 if r['slug'] in N:return '今回編集・自動投稿待ち'
 if r['slug']=='php-prompt-pun-yumemin':return '元動画が縦型・公開済み'
 if r['category']=='公開済み':return '既存ショート公開済み'
 if r['category']=='作成済み・未アップロード':return '既存ショート作成済み・投稿待ち'
 if r['source_duration_seconds_youtube']>101:return '今回対象外：101秒超'
 if not r['prompt_available']:return '今回対象外：プロンプトなし'
 raise RuntimeError('Unclassified '+r['slug'])
C=Counter(category(r) for r in rows);assert sum(C.values())==94
lines=['# 公式サイト掲載動画のショート対応一覧','','更新日：2026-10-16。Studio登録97作品のうち、公式サイト掲載中の94作品を作品単位で集計。','','対象条件は **元動画が1分41秒以下、制作プロンプトあり**。元動画を1分41秒で切る意味ではない。','','## 内訳','','| 状態 | 作品数 |','|---|---:|']
for c in ['既存ショート公開済み','元動画が縦型・公開済み','既存ショート作成済み・投稿待ち','今回編集・自動投稿待ち','今回対象外：101秒超','今回対象外：プロンプトなし']:lines.append(f'| {c} | {C[c]} |')
lines += ['| **合計** | **94** |','','今回34本を編集・検証して自動投稿リストへ追加。従来分36本と合わせて投稿待ちは70本。今回の新規分はそば屋さん31本・K9i3本。元から縦型だったゆめみんのPHP回は重複投稿しない。','','「データがなく復元不可能」と確定した作品は0本。今回の対象34本はすべて素材を取得できた。101秒超の対象外作品まで復元テストを行ったという意味ではない。','','## 今回完成した34本','','この表の尺は取得した元メディアの実測値。全編を720×1280へ編集し、元fps・フレーム数・圧縮音声を保持。短い不明瞭な発話は推測字幕を足さず、原音を残している。','','| 作品 | 作者 | 元尺 | 完成動画 |','|---|---|---:|---|']
for r in new:
 orig=next(x for x in rows if x['slug']==r['slug']);who='K9i' if r['creator']=='k9i' else 'そば屋さん';out=Path(r['output']).relative_to('03_SCRIPTS');lines.append(f'| {site(orig)} | {who} | {length(r["eligibility"]["sourceDurationSeconds"])} | [MP4]({out}) |')
for cat in ['既存ショート公開済み','元動画が縦型・公開済み','既存ショート作成済み・投稿待ち','今回対象外：101秒超','今回対象外：プロンプトなし']:
 lines+=['',f'## {cat}（{C[cat]}本）','','この表の元尺はYouTubeメタデータ値。','','| 作品 | 元尺 | プロンプト | 備考 |','|---|---:|---|---|']
 for r in rows:
  if category(r)!=cat:continue
  note=''
  if cat=='既存ショート公開済み':note=' / '.join(f'[Shorts](https://www.youtube.com/shorts/{i})' for i in r['shorts_ids'])
  if cat=='元動画が縦型・公開済み':note=f'1080×1920・[公開動画](https://www.youtube.com/watch?v={r["youtube_id"]})'
  if cat=='今回対象外：101秒超' and not r['prompt_available']:note='プロンプトもなし'
  lines.append(f'| {site(r)} | {length(r["source_duration_seconds_youtube"])} | {prompt(r)} | {note} |')
lines+=['','## 自動投稿の順番','','直近に公開した管理対象ショートの作者と逆の作者から選び、そば屋さん→K9iを交互に投稿する。現在の70本はそば屋さん31本・K9i39本で、交互に31周した後、残るK9i8本を続ける。各作者内では既存のリスト順を維持する。','','毎日23:00 JST、その日に公開済み動画も当日予約公開もなければ1本投稿する既存ルールを維持。編集完了・リスト追加と、YouTubeへの実際の公開は別の状態。今回の作業では即時投稿しない。','','詳細：[制作・検証記録](shorts_sobaya_20261016/README.md)、[投稿処理](../tools/shorts-nightly/README.md)。','']
(R/'03_SCRIPTS/shorts_site_inventory_20261016.md').write_text('\n'.join(lines))
print(dict(C))
