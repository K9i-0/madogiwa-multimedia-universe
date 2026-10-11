# 2026-10-11採用仕様と再実行

共有実装：`03_SCRIPTS/shorts_queue_20261011/remotion/src/index.tsx`。
回別正本：各エピソード直下`shorts-manifest.json`。
一括キュー：`03_SCRIPTS/shorts_queue_20261011/queue.json`。
パイロット5本の従来コードも残すが、追加回は共有実装を使ってデザインの分岐を防ぐ。

## 座標

720×1280。背景blur34px、拡大1.13、opacity0.47と縦gradient。
タイトルx32〜688、y92、高さ220。小見出し30px、letterSpacing2、margin-bottom20。
本文62px（10字超46px、15字超40px）、line-height1.22、letter-spacing-1、色#fff2d4、影0 4px 12px #0008。
本編x0,y350,w720,h480へcontain。標準16:9なら実映像の高さ405。
字幕x40〜632、y876。名前28px・margin-bottom12。本文38px、line-height1.5。
名前と本文の右側を空け、下端1110px以内を目安にする。

## 再実行（リポジトリルートから）

```bash
python3 03_SCRIPTS/shorts_queue_20261011/prepare_inputs.py
```

Remotionディレクトリで`npm ci`、`npm run typecheck`後：

```bash
node render.mjs <slug>
node render.mjs --still <slug>
```

引数なしはキュー全件。既存採用ファイルを変更したくない場合はslugを必ず指定する。
字幕なし映像の再作成はキューフォルダREADMEと`clean-jobs.json`。採用音声は必ず元完成版から保持する。

```bash
python3 03_SCRIPTS/shorts_queue_20261011/audit.py
python3 03_SCRIPTS/shorts_queue_20261011/publish_batch.py --batch 1
```

`publish_batch.py`は既定dry-run。ユーザーから登録指示があるときだけ`--upload`を付ける。毎週5本という目安であり、cron等は作成しない。別キューを作るときは日付別フォルダへ複製し、元の投稿記録を絶対に上書きしない。
