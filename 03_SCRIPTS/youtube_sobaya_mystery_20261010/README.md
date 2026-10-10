# めたんのミステリー研究所：そば屋

2026-10-10、チャットで確定した方向性を初稿として動画化。

- 正本台本：`script.md`。発話・演出：`remotion/dialogue.json`。
- タイミング：`remotion/src/edit-manifest.json`。全開始位置・尺は30fpsの整数フレーム。
- 完成動画：`final_remotion_sobaya_mystery.mp4`（ローカル保持）。
- 画面：1280×720。坂本アヒル式の立ち絵、波形に基づく口パク、まばたき、日本語字幕、資料写真、図解、無音の資料動画抜粋。
- 今回のオカルト指定に合わせ、従来の明るい楽曲ではなく、本作用の静かな自作アンビエントを使用。生成元は `mix_audio.py`、外部音楽素材は使用していない。
- 既存動画の音声は新しい解説と混ぜない。語句の途中で切れる原音、先に正体を明かす台詞を避け、資料抜粋は解説の下に無音で配置。
- 人事部への照会、研究史と研究所は、この番組のための架空の再構成。エピソードの事実と解説上の仮説は台詞中で区別。
- 既存64話の缶は過去の映像資料として引用。新規商品の描画基準には流用していない。
- 公開・Studio登録は行っていない。

## 再生成

ローカルVOICEVOX 0.25.1を `127.0.0.1:50021` で起動。

```sh
cd 03_SCRIPTS/youtube_sobaya_mystery_20261010/remotion
npm ci
../../../.local/voicevox-explainer/venv/bin/python prepare_assets.py
../../../.local/voicevox-explainer/venv/bin/python prepare_voice.py
npm run typecheck
npm run render
```

Remotion 4.0.534（制作時 `npm view remotion version` で確認）と関連パッケージを同一固定版で使用。資料映像と立ち絵のローカル原本は `asset_sources.json` を参照。

`public/`、`out/`、生成動画、node_modulesはGit対象外。VOICEVOXクエリのハッシュは話者・エンジン版・全クエリを含む。読み・字幕・間を変更した場合、再実行して実測尺を更新する。

## 初稿の完成仕様

- 10分47.233秒、19,417フレーム、1280×720・30fps。
- 122発話。動画内字幕と `subtitles_ja.srt` は同じ実測タイムライン。
- `chapters.txt` に章ごとの開始時刻。
- 冒頭・終盤の確認用動画は `remotion/out/opening_preview.mp4` と `remotion/out/ending_preview.mp4`。
- 全中央レイアウトの静止画を確認。顔・図解・字幕の切れを点検し、背景の残存文字、重複見出し、培養槽の資料フレームを修正。
- 音声の通し試聴は利用可能な手段がなく未実施。機械的な検査とは区別する。最終デコード結果は `qa_record.json`。
