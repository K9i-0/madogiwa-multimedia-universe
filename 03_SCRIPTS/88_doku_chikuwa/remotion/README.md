# 毒ちくわ 最終編集 v4

再現: リポジトリルートで `.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/88_doku_chikuwa/prepare_v4.py`、本ディレクトリで `npm ci && npm run typecheck && npm run render`。

`src/edit-manifest.json` が整数フレームの編集正本。1491フレーム、30fps、1280×720。生成動画はローカル保持。publicは再構築用でGit対象外。入力動画・入力画像・採用音声はエピソード直下。マスター音声はprepare_v4.pyで再作成。

## 現行 v5（自然な音声）

7セリフを演技指定なし・通常設定で各1回生成。ASR・読みの最適化・音声の速度調整なし。1528フレーム、30fps、1280×720。

既存のv4素材作成後、リポジトリルートで `.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/88_doku_chikuwa/prepare_v5.py`。本ディレクトリで `npm run typecheck` と `npx remotion render src/index.ts DokuChikuwaNatural ../final_remotion_doku_chikuwa_v5.mp4 --codec=h264 --concurrency=2 --overwrite`。編集正本は `src/edit-manifest-v5.json`。採用WAVはエピソード直下の `*_v5.wav`。

## v6 刑事ドラマ演出

v5素材作成後、ルートで `.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/88_doku_chikuwa/prepare_v6.py`。本ディレクトリで `npm run typecheck`、`npx remotion render src/index.ts DokuChikuwaDrama ../final_remotion_doku_chikuwa_v6.mp4 --codec=h264 --concurrency=2 --overwrite`。v5台詞を維持し、福ギュン発話のカットアウェイ、通常おでんの終幕、冒頭場所時刻、色調とオリジナル合成の音楽・現場音を追加。

## v7 侵入短縮・新しいリアクション

v6素材と採用済みreaction_v7.wavから、ルートで `.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/88_doku_chikuwa/prepare_v7.py`。本ディレクトリで `npm run typecheck`、`npx remotion render src/index.ts DokuChikuwaTight ../final_remotion_doku_chikuwa_v7.mp4 --codec=h264 --concurrency=2 --overwrite`。1445フレーム。音声生成条件はedit_v7_record.json。

## v8 現場記録テロップ・ラストアップ

v7素材をそのまま使用。`npx remotion render src/index.ts DokuChikuwaRecords ../final_remotion_doku_chikuwa_v8.mp4 --codec=h264 --concurrency=2 --overwrite`。Composition.tsxのrecordsオプションで冒頭2カットの現場記録テロップとラスト1.85倍固定アップを適用。音声と1445フレームの尺はv7と同じ。

## v9 現場画像と後ろ姿

v7音声と既存動画を用い、ルートで `python3 03_SCRIPTS/88_doku_chikuwa/prepare_v9.py`。本ディレクトリで `npm run typecheck`、`npx remotion render src/index.ts DokuChikuwaEvidence ../final_remotion_doku_chikuwa_v9.mp4 --codec=h264 --concurrency=2 --overwrite`。編集正本edit-manifest-v9.json。enhancedオプションで新規静止画への軽い寄りと既存人物カットの床を除くクロップ。

## v10 略語前の間

ルートで `.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/88_doku_chikuwa/prepare_v10.py`。本ディレクトリで `npx remotion render src/index.ts DokuChikuwaPause ../final_remotion_doku_chikuwa_v10.mp4 --codec=h264 --concurrency=2 --overwrite`。0.5秒の間を追加、全1460フレーム。

## v11 室内再制作

新規Wan3本とempty_table_hold_v11.png、v10音声を用いる。ルートで `python3 03_SCRIPTS/88_doku_chikuwa/prepare_v11.py`。本ディレクトリで `npm run typecheck`、`npx remotion render src/index.ts DokuChikuwaInterior ../final_remotion_doku_chikuwa_v11.mp4 --codec=h264 --concurrency=2 --overwrite`。不採用区間と制限はedit_v11_record.json。
