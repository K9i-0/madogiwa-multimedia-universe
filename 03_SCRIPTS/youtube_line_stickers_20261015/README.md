# Codexで動くLINEスタンプを作ってみた！失敗から学んだ制作のコツ

第一弾・第二弾を作った実例から、人が使える頼み方・選び方・仕上げ方を紹介する掛け合い動画。やめ太郎は普段のIrodori、たこさんはVOICEVOX中国うさぎ。

2026-10-16、完成動画v6はユーザー承認済み。公開タイトルは「Codexで動くLINEスタンプを作ってみた！失敗から学んだ制作のコツ」を採用。サムネイルは実際のLINEスタンプ画像とImagegenで生成した文字・装飾を組み合わせた緑のA案を採用。[投稿用JPEG](thumbnails/thumbnail_youtube.jpg) / [PNG](thumbnails/thumbnail_youtube.png) / [制作記録](thumbnails/README.md)。

## 現行：設定・速度と品質・掛け合いを反映した v6

2026-10-16。普段のIrodoriを使うv5へ、ユーザーの追加FBを反映。

- [完成動画](final_remotion_line_stickers_v6.mp4)：11分16.07秒、1280×720、30fps
- [台本](script.md)・[日本語字幕](subtitles_ja.srt)・[YouTube概要欄](youtube_description.txt)
- [検査記録](review_v6.md)
- [冒頭の抜粋](preview_opening_v6.mp4)・[設定の抜粋](preview_settings_v6.mp4)・[締めの抜粋](preview_ending_v6.mp4)
- [通知への反応の音声比較](remotion/out/v6_intro_candidates/index.html)：前回版→A→B→C。現行はC。

全107発話。変更した19発話を機械検査し、残る88発話はv5の波形と設定を保全。Codex設定は投稿者個人の使い分けとして、GPT 6 Astraの案出し＝effort Light／仕上げ＝effort Ultraを紹介。好みに合わせて変更できると説明し、Imagegenの画質設定とは区別する。8個を1枚にまとめると呼び出し回数を減らせること、人が見比べる間は速度、任せて待てる仕上げでは品質を優先することを加えた。

「よーたんからや！」は喜びを強調しない3候補を生成し、機械検証からCを採用。自然さ・アクセントの主観試聴は未実施。辞令の反応を延ばし、茶番から自己紹介へは画面全体の短い白フェードで切り替える。ChatGPTプラン選びの別動画への言及、そば屋さんの扱いへのツッコミを追加。「案出し」の読みを「あんだし」にし、「道具」を「ツール」に統一。最後は「やっぱやめさんも窓際族ですね」で会話を終える。

第一弾の透過失敗は、当時の不良出力APNGと登録時の報告スクショを引き続き使用。同じ不良画像を白背景→黒背景で見せ、画像処理で修正した実物と比較する。

MP4と確認画像はローカル成果物。YouTubeやMadogiwa Studioへの公開・アップロードは行っていない。

## 正本と出典

- `script.md` / `remotion/dialogue.json`：採用台詞、画面、読み、演技指定、発話間。`voiceCaption` は音声用で字幕とは別。
- `remotion/src/edit-manifest.json`：実測音声から作る整数フレームの時刻、字幕ページ、口パク波形。
- `voice_record.json` / `adopted_audio.json`：採用音声の生成条件・SHA・実測尺。直下の `voice_*.wav` が現行採用音声。
- `voice_audit_v6.json`：差し替え音声のASR/VADと、未変更音声の保全検証。主観的な試聴と区別する。
- `intro_voice_candidates_v6.json`：通知への反応3候補と採用Cの設定・SHA・検証範囲。未採用WAVはGit追跡しない。
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
python3 render.py ../final_remotion_line_stickers_v6.mp4
```

完成検証はリポジトリ直下で `.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/youtube_line_stickers_20261015/verify_delivery_v6.py`。素材SHA・実画素・字幕・音声の保全・フレーム数・全デコードを確認し、抜粋と監査画像を作る。

`remotion/public/` は参照素材・デコードフレーム・音声、`remotion/out/` は監査・中間出力でGit管理しない。完成MP4もローカル保持。採用入力、コード、設定、台詞、採用音声、出典台帳を追跡する。

## 旧版と声の比較

- v5：`final_remotion_line_stickers_v5.mp4`、10分20.27秒。正本Git `bc765980`。透過失敗の実例・採用ツッコミを反映。v6改稿前の入力と退避音声は `remotion/out/v5_before_v6/`。

- v3：`final_remotion_line_stickers_v3.mp4`、9分56.37秒。普段のIrodori版。本版の制作ベース。正本はGit `61f44365`、制作再開時の記録は `4ee5909c`。改稿前の入力は `remotion/out/v3_before_v5/` に保全。
- v4：`final_remotion_line_stickers_v4.mp4`、9分52.1秒。B（玄野武宏）全編比較。正本はGit `83f5cb12`、設定・採用音声は `remotion/out/v4_records/`。現在の制作声はIrodori。
- 比較：`preview_voice_comparison.mp4`。冒頭候補 `preview_voice_current.mp4` / `preview_voice_aoyama.mp4` / `preview_voice_kurono.mp4` / `preview_voice_shirakami.mp4`。VOICEVOX候補は話速1.15・音高0・抑揚1.0で、YouTubeの「なんJ民」に統一設定があるという意味ではない。
- 声の調査・検証：`voice_candidate_research.json` / `voice_candidate_delivery.json`。`VOICE_CAST.md` の正典は変更していない。
- 初稿：`final_remotion_line_stickers.mp4`。v2：`final_remotion_line_stickers_v2.mp4`（10分26.3秒、正本Git `a09eabbf`）。
- v3と復帰時の監査：`review.md` / `voice_audit_v3.json`。旧版の監査を現行v6の合格判定として流用しない。
