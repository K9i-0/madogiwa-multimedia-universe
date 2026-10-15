# Codexで動くLINEスタンプを作る

ユーザー採用の「人が使える頼み方・選び方・直し方」を紹介する解説動画。第一弾の完成品を軸に、第二弾の比較案と試行錯誤も実例として使う。

## 実践のコツ版 v3（2026-10-15）

- [全編](final_remotion_line_stickers_v3.mp4)：9分56.37秒、1280×720、30fps。
- [案出し・候補選びの抜粋](preview_tips_v3.mp4)：約1分51秒。8個入り案の一覧、複数構図からの選択、椅子案の転用。
- [台本](script.md)・[日本語字幕](subtitles_ja.srt)・[YouTube概要欄](youtube_description.txt)。
- [検査記録](review.md)・[完成ファイル情報](delivery.json)。音声の自動検査と主観的な通し試聴は区別する。

導入から挨拶まで16発話はv2の採用音声・時刻・字幕・演出を維持。本編73発話を採用改稿へ差し替えた。全89発話、111字幕ページ。指示例は全文を追加音読せず、画面で読める間を設ける。

取り上げるコツは、8個まとめの案出し、複数案から選択、決定後の再描画、Pets用スキルの連続原画方式、雰囲気とゴールで動きを依頼、白黒背景での確認、ImagegenとOpenCV・ImageMagickの使い分け。

MP4と確認画像はローカル成果物。公開・アップロードは行っていない。

## 正本

- `script.md` / `remotion/dialogue.json`：採用台詞・画面・音声用の読み・発話間。
- `remotion/tip-prompts.json`：表示する6種類の指示例。React側と本文一致を検査。
- `remotion/src/edit-manifest.json`：音声実測から作る整数フレームの正本。字幕ページと口パク用波形を含む。
- `intro_reference_v2.json`：変更しない導入16発話の台詞・音声SHA・時刻・字幕。
- `voice_audit_v3.json`：新しいやめ太郎音声のASR・VAD・語尾比較、導入保持、字幕・音量の検証。
- `voice_record.json` / `adopted_audio.json`：採用音声の生成設定・ハッシュ・実測尺。エピソード直下の `voice_*.wav` が採用音声。
- `remotion/voice_cleanup.json`：導入の既存2カット。未加工原音は `input/voice_uncut/`。新本文の音声は個別の生成条件で調整する。
- `asset_sources.json`：第一弾の完成APNG・正典・立ち絵の参照先。
- `asset_sources_v3.json` / `remotion/src/tips-assets.json`：実際の比較案・再描画・動き・透過前後の出典、SHA、切出し範囲、再生時間。
- `input/tips/`：今回の映像に採用した制作途中資料。元画素を保ち、故意の劣化や汚れを加えない。
- `fact_check_imagegen.md` / `fact_check_pets.md`：説明の一次資料と表現範囲。

## 再現

リポジトリ直下で実行。Python環境は既存の `.local/Irodori-TTS/.venv`（音声）と `27_LINE_STICKERS/sets/02/.venv`（画像）を使用する。VOICEVOX Engineは `127.0.0.1:50021`。正典声は `02_CHARACTERS/VOICE_CAST.md`、Irodori手順は `tools/IRODORI_TTS.md` を参照。

```sh
python3 03_SCRIPTS/youtube_line_stickers_20261015/prepare_assets.py
27_LINE_STICKERS/sets/02/.venv/bin/python 03_SCRIPTS/youtube_line_stickers_20261015/prepare_tips_assets.py
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/youtube_line_stickers_20261015/remotion/prepare_voice.py
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/youtube_line_stickers_20261015/remotion/finalize_voice_timing.py
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/youtube_line_stickers_20261015/remotion/mix_audio.py
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/youtube_line_stickers_20261015/remotion/validate_audio_timeline.py
cd 03_SCRIPTS/youtube_line_stickers_20261015/remotion
npm ci
npm run typecheck
python3 render.py ../final_remotion_line_stickers_v3.mp4
python3 ../verify_delivery_v3.py --video final_remotion_line_stickers_v3.mp4
```

`voice_overrides.json` は個別生成条件、`caption_layout.json` は意味の切れ目を優先した字幕。`voice_timeline_config.json` の終了開始IDは `close-01`。音声は採用ハッシュと生成設定を照合して再利用する。

`remotion/public/` は参照素材・デコードフレーム・音声、`remotion/out/` は監査・中間出力でGit管理しない。完成MP4もローカル保持する。採用入力、コード、設定、台詞、音声、出典台帳を追跡する。

## 比較用の旧版

- 初稿：`final_remotion_line_stickers.mp4`。
- v2：`final_remotion_line_stickers_v2.mp4`。Imagegen説明・やめ太郎4箇所の音声を修正した10分26.3秒版。制作正本はGit `a09eabbf`。
- v2の音声比較：`preview_voice_cleanup.mp4`（21.6秒）。当時の4箇所で、現行v3の音声一覧とは別。
- v2の記録と退役WAVはローカル `remotion/out/v2_records/` にも保全。現行の導入2箇所の修復は引き続き採用。

## 事実と見せ方

第一弾の販売申請はそば屋さんが担当。第二弾の候補画像を第一弾の制作記録と混同しない。肘の動き3候補は全て不採用。OpenAIのPets用スキルを参考にしたもので、OpenAI公式のLINEスタンプ制作法とは説明しない。文字の透過前は実在する白背景付き入力。完成品に汚れを加えた比較は作らない。動画内の説明用ループと元APNGの再生回数は区別する。
