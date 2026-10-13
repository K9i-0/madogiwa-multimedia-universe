# Codexで動画まで作る。窓際族物語のAI制作術 — v2

CodexやClaude Codeでものづくりをしている人向けの、ずんだもん・四国めたんによる解説。第53話のニュース制作を軸に、人物資料、音声修復、編集、費用、制作スキルの継続改善を扱う。

完成版は `../final_remotion_ai_video_workflow_v2.mp4`。1280×720 / 30fps / 18,481フレーム、10分16.033秒。旧版 `../final_remotion_ai_video_workflow.mp4` は比較用に保存し、上書きしない。

## 編集の正本

- `dialogue.json`：110発話の台本・字幕改行・画面・章。
- `clips_config.json`：作例と原音比較の挿入位置、素材内の範囲、BGMを止める指定。
- `src/edit-manifest.json`：VOICEVOXの読み、実測音声長、フレーム単位の完成タイムライン。
- `../asset_sources.json`：ローカル素材、抽出フレームの時刻、SHA-256。
- `../evidence_v2.json`：制作ログの根拠、音声比較の範囲、別実験の区別。
- `../sources.json`：料金・制作手順・過去エピソードの出典。

Remotion 4.0.535 / React 19.2.3。VOICEVOX 0.25.1、四国めたん2・ずんだもん3。立ち絵と静かなBGMは採用済み解説テンプレを継承する。

## 再現とレビュー候補の書き出し

以下はこの `remotion/` ディレクトリで実行する。Node.js、ffmpeg・ffprobe、ローカル素材、既存のPython環境が必要。VOICEVOXを `127.0.0.1:50021` で起動しておく。

```sh
npm ci
../../../.local/voicevox-explainer/venv/bin/python prepare_assets.py
../../../.local/voicevox-explainer/venv/bin/python prepare_voice.py
npm run typecheck
../../../.local/voicevox-explainer/venv/bin/python validate_timeline.py
npm run render -- --output out/review_v2_01.mp4 --concurrency 4
```

`prepare_assets.py` は元素材を変更せずhardlinkし、指定時刻から実フレームを抽出する。既存の公開用ファイルが宣言した素材と異なる場合は停止する。素材にはGit管理外のローカル動画・立ち絵・BGMがあるため、Gitだけでは再現に必要な全ファイルはそろわない。

`prepare_voice.py` はエンジン版・話者・音声クエリのSHA-256でキャッシュを照合し、変更した発話だけ合成する。音声とクリップの実測長からマニフェストを再生成するため、実測尺を確認する。

`render.py` はタイムライン検証、音声ミックス、映像レンダー、AAC音声とのmuxを実行する。引数なしの出力は `out/review_v2_01.mp4`。映像のみ直した場合は `--skip-mix` で既存の `public/mixed.wav` を使用できる。比較する候補は `review_v2_02.mp4` など別名へ書き出す。完成MP4への暗黙の上書きは行わない。

この解説の再現では既存作品を使い、新しいWan動画生成・有料API送信は行わない。

## 監査と採用

```sh
../../../.local/voicevox-explainer/venv/bin/python audit_video.py --source out/review_v2_01.mp4 --tag v2_01
../../../.local/voicevox-explainer/venv/bin/python final_checks.py --source out/review_v2_01.mp4 --tag v2_01
```

`--source` はこのディレクトリからの相対パス、または絶対パス。`--tag` を変えると、候補ごとの `out/audit_<tag>/` と `../delivery_<tag>.json` を保存できる。`audit_video.py` は全110発話の表示中・各クリップの開始／中間／終了・動く図解の後半・締めを抽出し、全編をデコードする。候補と現行タイムラインが異なる場合は、候補保存時のマニフェストを `--manifest out/候補のmanifest.json` で指定する。コンタクトシートと個別フレームを目視する。`final_checks.py` は720p、30fps、18,481フレーム、48kHz stereo、全編デコード、ピーク超過、ファイルハッシュを検証する。

字幕は文の切れ目で2行までにし、通常29px、長文2件のみ26px。立ち絵の間の790px内に収める。字幕本文・幅・音声尺・原音クリップとの重なりは `out/timeline_validation.json` に記録する。音声の自動照合は別環境で実行する。

```sh
../../../.local/Irodori-TTS/.venv/bin/python audit_audio.py
../../../.local/Irodori-TTS/.venv/bin/python audit_mix.py
```

ASRは発音確認の補助で、聴感や完全リップシンクの合格判定にはしない。VOICEVOXの読み、ASRの疑義、画面と話す内容の対応、引用音声とBGMの切替を確認し、改善点があれば候補を再出力する。

レビュー済み候補を採用するときだけ、ファイル名を固定する。以下の候補名は実際に採用したものへ置き換える。

```sh
cp -n out/review_v2_01.mp4 ../final_remotion_ai_video_workflow_v2.mp4
../../../.local/voicevox-explainer/venv/bin/python audit_video.py --source ../final_remotion_ai_video_workflow_v2.mp4 --tag v2
../../../.local/voicevox-explainer/venv/bin/python final_checks.py --source ../final_remotion_ai_video_workflow_v2.mp4 --tag v2
```

`cp -n` は既存の完成版を上書きしない。すでに同名がある場合は、採用版のハッシュを確認し、別候補の監査結果と取り違えない。最終の確認内容と限界は `../review_v2.md`、`../delivery_v2.json` に記録する。音量の詳細記録 `out/final_loudness.json` は最後の検査で更新され、候補ごとの値は各delivery JSONにも保存される。

## 実例の扱い

第53話の「速報です」は `news_raw.mp4` と `news_fixed.mp4` の各0〜2.1秒を比較する。両者の映像ストリームは同一。比較区間ごとに音量を合わせ、BGMと二人の解説を止める。

第72話の `voice_patch_comparison.mp4` は完成本編とは別の部分修復実験。全310フレームで、前半155フレームが元音声、後半155フレームが修正候補。下部の比較ラベルは素材へ焼き込まれている。この福ギュンの実験はIrodori Smallによるもの。後日のおかやまんでの比較を受けたLargeの運用採用と区別する。根拠は `../evidence_v2.json` と `../../72_tokyo_madogiwa_park/voice_patch_experiment.md`、`../../72_tokyo_madogiwa_park/okayaman_large_patch.md`。

第53話のAPI失敗記録は参照音声の各尺・合計尺を事前検査する理由として使用し、失敗時の課金額は断言しない。タスクIDやAPI応答全文は画面に出さない。

料金は2026年10月13日確認の通常表示価格を基準にする。720pの完成書き出しと480pの生成料金を混同しない。動画はローカル保存で、公開・アップロードは別作業。概要欄とクレジットは `../youtube_description.txt`。
