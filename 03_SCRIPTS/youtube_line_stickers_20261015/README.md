# Codexで動くLINEスタンプを作る

ユーザーがチャットで採用した導入とシナリオを使った、約10分の初回動画。第一弾の採用素材・制作コードを題材に、やめ太郎とたこさんが解説する。

## 修正版 v2（2026-10-15）

- [全編](final_remotion_line_stickers_v2.mp4)：10分26.3秒、1280×720、30fps、H.264 / AAC、約37 MB。
- [導入と本編挨拶の抜粋](preview_intro.mp4)：1分3.3秒。Outlookの辞令、廃村エンジニアの掛け合い、タイトル転換、挨拶を含む。
- [やめ太郎の修正前後4箇所](preview_voice_cleanup.mp4)：各ペアの音量基準をそろえた比較。
- [Imagegen説明の抜粋](preview_imagegen_v2.mp4)：役割図と利用枠の説明。
- [日本語字幕](subtitles_ja.srt)：114ページ。
- [検査記録](review.md)・[完成ファイル情報](delivery.json)。全編デコード・字幕照合・完成映像の抽出フレーム検査を実施。音声は自動検査済みで、主観的な通し試聴は未実施。

初稿 `final_remotion_line_stickers.mp4` は比較用に保持。v2ではImagegenの説明3発話と役割図、やめ太郎の余分な声・長い語尾4箇所を修正した。

MP4と検査画像はローカル成果物。公開・アップロードは行っていない。

## 正本

- `script.md`：演出・配役・採用したセリフ。
- `remotion/dialogue.json`：表示用本文・音声用読み・画面・発話間。
- `remotion/src/edit-manifest.json`：音声実測から作る整数フレームの正本。字幕ページ・口パク用波形を含む。
- `voice_record.json`：音声生成設定、参照音声、ハッシュ、実測尺。エピソード直下の `voice_*.wav` が採用音声。
- `remotion/voice_cleanup.json`：やめ太郎の4発話に適用するカットとフェード。未加工の入力は `input/voice_uncut/` に保持する。
- `asset_sources.json`：スタンプ原画、完成APNG、立ち絵、実物販売画像の参照先・ハッシュ。
- `fact_check_imagegen.md`：ImagegenとCodex、ChatGPTプランの利用枠についての公式確認と改稿理由。
- `youtube_description.txt`：販売リンク、制作資料、声・音楽のクレジット。公開操作は依頼範囲外。

## 再現

リポジトリ直下から実行する。Pythonの画像準備にはPillow、音声処理にはNumPy・SoundFile・Pillowが必要。Irodoriはリポジトリの既存 `.local/Irodori-TTS/.venv` と正典参照を使用し、VOICEVOX Engineは `127.0.0.1:50021` で起動する。詳細は `tools/IRODORI_TTS.md` と `02_CHARACTERS/VOICE_CAST.md`。

```sh
python3 03_SCRIPTS/youtube_line_stickers_20261015/prepare_assets.py
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/youtube_line_stickers_20261015/remotion/prepare_voice.py
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/youtube_line_stickers_20261015/remotion/finalize_voice_timing.py
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/youtube_line_stickers_20261015/remotion/mix_audio.py
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/youtube_line_stickers_20261015/remotion/validate_audio_timeline.py
cd 03_SCRIPTS/youtube_line_stickers_20261015/remotion
npm ci
npm run typecheck
python3 render.py ../final_remotion_line_stickers_v2.mp4
python3 ../verify_delivery.py --video final_remotion_line_stickers_v2.mp4 --section-excerpt preview_imagegen_v2.mp4
```

音声の個別生成設定は `voice_overrides.json`、カット処理は `voice_cleanup.json` を参照。カットは未加工音声から再適用し、処理済み音声を再度削らない。採用音声と処理の履歴を保持していれば、同じ設定の音声を再利用する。

`remotion/public/` は参照素材と音声のhardlink・再生成フレーム、`.asset-cache/` は取得元HTMLと画像、`remotion/out/` は検査・途中出力でありGit管理しない。完成MP4もローカル保持。採用音声・制作コード・設定・資料の参照先を追跡する。

## 表現と事実

- 冒頭のメッセージとOutlook辞令は劇中の架空UI。実際のメール操作や送信は行わない。
- 最後の「実例いらんねん！」からタイトルへ画面転換し、挨拶で本編を開始する。
- 「廃村」は音声では「ハイソン」、字幕は「廃村（ハイソン）」。Pythonとの掛け合いを保持する。
- そば屋は採用4原画→13フレーム・3秒。原依頼12姿勢のシートを捏造しない。実物シートはよーたん3×2。
- 第一弾は全員同じ動かし方ではない。補間・全体拡大・回転の併用も説明する。
- 第一弾はそば屋さんが申請し、商品37292753として販売中。ローカルの提出main/tab未収録と販売状態は別。
- 音声の機械検査・字幕照合と、主観的な通し試聴は分けて監査記録に残す。
