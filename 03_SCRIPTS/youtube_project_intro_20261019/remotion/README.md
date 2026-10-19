# 窓際族物語 プロジェクト紹介・初稿

台本は `../script.md`、機械入力は `dialogue.txt`。タイミングの正本は `src/edit-manifest.json`。VOICEVOXの字幕原文・発音指定・最終クエリ・WAVを分離して保存する。

リポジトリルートで実行：

```sh
.local/voicevox-explainer/venv/bin/python 03_SCRIPTS/youtube_project_intro_20261019/remotion/prepare_assets.py
.local/voicevox-explainer/venv/bin/python 03_SCRIPTS/youtube_project_intro_20261019/remotion/prepare_voice.py
.local/voicevox-explainer/venv/bin/python 03_SCRIPTS/youtube_project_intro_20261019/remotion/export_metadata.py
.local/voicevox-explainer/venv/bin/python 03_SCRIPTS/youtube_project_intro_20261019/remotion/check_structure.py
```

`remotion/`内で `npm ci`、`npm run typecheck`、`npm run render`。音声は48kHz stereoへミックス、Remotionを720p/30fpsでレンダーしAACとmuxする。完成MP4はエピソード直下。

`prepare_assets.py`は既存作品・素材の必要分だけをpublicへhardlinkし、冒頭の短縮無音版とスタンプ再生用MP4を派生生成する。元のファイルを上書きしない。動画と第三者立ち絵・BGM・中間出力はローカル保持。公式サイトとゲームの採用スクリーンショットはpublic内で追跡する。

サイト再取得用 `capture_site.cjs` / `capture_prompt.cjs` はリポジトリルートから実行。既存3D解説のPlaywrightを使い、Chrome headlessで撮影する。`capture_games.cjs`は、定時ダッシュのdist/clientを8892、ギュンギュン・クエストのdistを8891で配信して実行する。外部サイトは将来表示が変わり得るため、今回の採用画像を保存する。

監査：`node audit_frames.cjs`、`check_structure.py`、`audit_output.py`。任意のASR補助確認は `.local/Irodori-TTS/.venv/bin/python .../audit_full_audio.py`。ASR・デコード検査を主観的な通し試聴とみなさない。

初稿は公開・Studio登録していない。宣伝用紹介動画のため、技術解説テンプレのTheFatRat - Unityは引き継がず、本編と終了は既存採用曲「ほのぼのワルツ【リコーダー】」を低音量で使用。冒頭の作品原音・BGMは無音。
