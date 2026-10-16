# Codexで動くLINEスタンプを作る

第一弾・第二弾を作った実例から、人が使える頼み方・選び方・仕上げ方を紹介する掛け合い動画。やめ太郎は普段のIrodori、たこさんはVOICEVOX中国うさぎ。

## 現行：実例と掛け合い版 v5

2026-10-16。Irodori版v3をベースに、ユーザーのFBを反映して改稿・動画化。

- [完成動画](final_remotion_line_stickers_v5.mp4)：10分20.27秒、1280×720、30fps
- [台本](script.md)・[日本語字幕](subtitles_ja.srt)・[YouTube概要欄](youtube_description.txt)
- [検査記録](review_v5.md)・[完成ファイル情報](delivery.json)
- [冒頭の抜粋](preview_opening_v5.mp4)・[候補選びの抜粋](preview_tips_v5.mp4)・[透過失敗と修正の抜粋](preview_alpha_v5.mp4)

全96発話。冒頭タイトルを「窓際族LINEスタンプ第一弾」にし、茶番は「Pythonエンジニアみたいに言うな！」まで。短いタイトル転換後に自己紹介し、第二弾のそば屋8個も紹介する。

「馴れ馴れしかったものを選びました」「どういう選定基準やねん」、椅子案の窓際への転用に謎に誇らしげな「さすがそば屋さんや！」、白Tシャツ保護の説明で「そば屋さんが脱ぐとか誰得」を採用。通知への反応も新しく生成。変更のない74発話はv3の採用WAVを維持する。

第一弾の透過失敗には、当時の不良出力APNGと登録時の報告スクショを使用。同じ不良画像を白背景→黒背景で見せ、画像処理で修正した実物と比較する。生成前の白背景素材とは区別する。

取り上げるコツは、8個まとめの案出し、複数案から選択、決定後の再描画、Pets用スキルの連続原画方式、雰囲気とゴールで動きを依頼、完成品の白黒背景チェック、ImagegenとOpenCV・ImageMagickの使い分け。

MP4と確認画像はローカル成果物。YouTubeやMadogiwa Studioへの公開・アップロードは行っていない。

## 正本と出典

- `script.md` / `remotion/dialogue.json`：採用台詞、画面、読み、演技指定、発話間。`voiceCaption` は音声用で字幕とは別。
- `remotion/src/edit-manifest.json`：実測音声から作る整数フレームの時刻、字幕ページ、口パク波形。
- `voice_record.json` / `adopted_audio.json`：採用音声の生成条件・SHA・実測尺。直下の `voice_*.wav` が現行採用音声。
- `voice_audit_v5.json`：差し替え音声のASR/VADと、未変更音声の保全検証。主観的な試聴と区別する。
- `remotion/voice_cleanup.json`：現行で維持するintro-07の採用済みカット。旧intro-04の原音・設定はv3アーカイブへ保全。
- `remotion/voice_overrides.json`：生成時の個別条件。`caption_layout.json`：意味の切れ目を優先した字幕。
- `remotion/tip-prompts.json`：6種類の表示用指示例。音読せず読む間を設ける。
- `asset_sources.json`：第一弾完成品・正典・立ち絵の出典。
- `asset_sources_v3.json`：継続利用する案出し・候補・再描画・動きの制作資料。
- `asset_sources_v5.json` / `prepare_history_assets.py`：当時の不良出力・修正後・スクショ、第二弾完成8個の出典と処理。
- `first_set_alpha_history.json`：Git・セッションで確認した経緯。採用資料は `input/alpha-history/`。元セッションは編集せず、会話全体は公開しない。
- `fact_check_imagegen.md` / `fact_check_pets.md`：一次資料と説明範囲。2026-10-16にも公式ページを再確認。

第一弾の申請担当はそば屋さん。第二弾の候補を第一弾の制作記録と混同しない。肘の動き3候補は全不採用。OpenAIのPets用スキルを参考にしたもので、OpenAI公式のLINEスタンプ制作法とは説明しない。修正後の均一な細い文字白フチは可読性のための意図した装飾。消し残しとは区別する。説明用ループと元APNGの再生回数も区別する。

## 再現

リポジトリ直下で実行。Pythonは既存の `.local/Irodori-TTS/.venv`（音声）と `27_LINE_STICKERS/sets/02/.venv`（画像）。VOICEVOX Engineは `127.0.0.1:50021`。正典声は `02_CHARACTERS/VOICE_CAST.md`、Irodori手順は `tools/IRODORI_TTS.md`。

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
python3 render.py ../final_remotion_line_stickers_v5.mp4
```

完成検証はリポジトリ直下で `.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/youtube_line_stickers_20261015/verify_delivery_v5.py`。素材SHA・実画素・字幕・音声の保全・フレーム数・全デコードを確認し、抜粋と監査画像を作る。

`remotion/public/` は参照素材・デコードフレーム・音声、`remotion/out/` は監査・中間出力でGit管理しない。完成MP4もローカル保持。採用入力、コード、設定、台詞、採用音声、出典台帳を追跡する。

## 旧版と声の比較

- v3：`final_remotion_line_stickers_v3.mp4`、9分56.37秒。普段のIrodori版。本版の制作ベース。正本はGit `61f44365`、制作再開時の記録は `4ee5909c`。改稿前の入力は `remotion/out/v3_before_v5/` に保全。
- v4：`final_remotion_line_stickers_v4.mp4`、9分52.1秒。B（玄野武宏）全編比較。正本はGit `83f5cb12`、設定・採用音声は `remotion/out/v4_records/`。現在の制作声はIrodori。
- 比較：`preview_voice_comparison.mp4`。冒頭候補 `preview_voice_current.mp4` / `preview_voice_aoyama.mp4` / `preview_voice_kurono.mp4` / `preview_voice_shirakami.mp4`。VOICEVOX候補は話速1.15・音高0・抑揚1.0で、YouTubeの「なんJ民」に統一設定があるという意味ではない。
- 声の調査・検証：`voice_candidate_research.json` / `voice_candidate_delivery.json`。`VOICE_CAST.md` の正典は変更していない。
- 初稿：`final_remotion_line_stickers.mp4`。v2：`final_remotion_line_stickers_v2.mp4`（10分26.3秒、正本Git `a09eabbf`）。
- v3と復帰時の監査：`review.md` / `voice_audit_v3.json`。旧版の監査を新しいv5の合格判定として流用しない。
