# Codexで動くLINEスタンプを作る

ユーザー採用の「人が使える頼み方・選び方・直し方」を紹介する解説動画。第一弾の完成品を軸に、第二弾の比較案と試行錯誤も実例として使う。

## 現在の制作ベース：Irodori版 v3（2026-10-16再採用）

ユーザー指示により、B（玄野武宏）の試作後、普段のIrodori版v3を制作ベースへ戻した。編集manifest・採用WAV89個・ミックス・字幕・章時刻・音声生成設定はGit `61f44365` のv3へ復元。今後の修正はこの状態から行う。

- [全編](final_remotion_line_stickers_v3.mp4)：9分56.37秒、1280×720、30fps。
- [案出し・候補選びの抜粋](preview_tips_v3.mp4)：約1分51秒。8個入り案の一覧、複数構図からの選択、椅子案の転用。
- [台本](script.md)・[日本語字幕](subtitles_ja.srt)・[YouTube概要欄](youtube_description.txt)。
- [検査記録](review.md)・[完成ファイル情報](delivery.json)。音声の自動検査と主観的な通し試聴は区別する。

導入から挨拶まで16発話はv2の採用音声・時刻・字幕・演出を維持。本編73発話を採用改稿へ差し替えた。全89発話、111字幕ページ。指示例は全文を追加音読せず、画面で読める間を設ける。

取り上げるコツは、8個まとめの案出し、複数案から選択、決定後の再描画、Pets用スキルの連続原画方式、雰囲気とゴールで動きを依頼、白黒背景での確認、ImagegenとOpenCV・ImageMagickの使い分け。

MP4と確認画像はローカル成果物。公開・アップロードは行っていない。

## やめ太郎の声の比較（2026-10-15制作、10-16にIrodoriへ復帰）

冒頭の茶番〜本編挨拶16発話で、やめ太郎の10発話だけを差し替えた試聴候補。たこさんの6発話・台詞・画面・会話の間・BGM・効果音を揃え、声の実測尺に合わせて字幕・口パクと後続演出を配置する。比較後にBの全編v4を制作したが、現在はv3を再採用している。`VOICE_CAST.md` の正典声は変更していない。

まず [短い比較動画](preview_voice_comparison.mp4)（68.10秒）。同じ最初の3発話を、現行→A→B→Cの順に再生する。各台詞を最後まで含め、LINE通知が鳴る前で区切っている。

- [現行 Irodori](preview_voice_current.mp4)：65.77秒。
- [A：青山龍星・ノーマル](preview_voice_aoyama.mp4)：65.70秒。
- [B：玄野武宏・ノーマル](preview_voice_kurono.mp4)：63.97秒。
- [C：白上虎太郎・ふつう](preview_voice_shirakami.mp4)：66.70秒。

VOICEVOXの3候補は話速1.15・音高0・抑揚1.0、前無音0.10秒／後無音0.20秒、48kHz mono。これは今回の比較設定であり、YouTubeの「なんJ民」に統一された設定という意味ではない。よーたん・やめ太郎の固有名詞は一つのアクセント句にまとめ、生成クエリと変更前後の読みを記録する。音声の一律早送りや語尾カットは行わない。

調査出典と対象範囲は [voice_candidate_research.json](voice_candidate_research.json)。AquesTalkのゆっくり男性声は今回含まれない。公式Mac配布の取得に失敗し、商用候補制作に使えるライセンスも未確認だったため。特定のYouTube動画の声や設定を同定・再現したとは主張しない。

```sh
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/youtube_line_stickers_20261015/remotion/generate_voice_candidates.py
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/youtube_line_stickers_20261015/remotion/prepare_voice_candidate_videos.py current aoyama kurono shirakami
cd 03_SCRIPTS/youtube_line_stickers_20261015/remotion
node render_voice_candidates.mjs current aoyama kurono shirakami
python3 compare_voice_candidates.py
```

比較動画のIrodori基準はGit `61f44365` のmanifestに固定。候補のWAV・全文クエリ・ハッシュ・実測尺・独立manifestは `remotion/out/voice-candidates/<key>/`、再生用音声は `remotion/public/voice-candidates/` に保持する。候補・中間音声はGitへ追加せず、採用前に正典へ昇格しない。声のクレジットは各候補の `VOICEVOX:青山龍星`／`VOICEVOX:玄野武宏`／`VOICEVOX:白上虎太郎` と、共通の `VOICEVOX:中国うさぎ`。音楽はv3の概要欄と同じ。

[検査・ファイル情報](voice_candidate_delivery.json)：全5本のデコードと形式、字幕全文、発話間、原音保持を確認。完成動画から計60フレームを目視し、文字の欠け・重なりなし。最終MP4の音声も予定ミックスとの波形相関で照合した。主観的な通し試聴や声の好み・自然さの判定は未実施。

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

- B（玄野武宏）全編v4：`final_remotion_line_stickers_v4.mp4`（9分52.1秒）、抜粋 `preview_tips_v4.mp4`。比較用に保持。制作正本はGit `83f5cb12`、採用音声・設定・台本・字幕・ミックス等はローカル `remotion/out/v4_records/` に保全。
- `voice_audit_v4.json`、`v4_voice_replacement_reference.json`、`input/voice_b_adopted.json` はv4の履歴。v4専用の `voice_config.json` は退避済みで、現行の `prepare_voice.py` はIrodoriのv3手順を使う。

- 初稿：`final_remotion_line_stickers.mp4`。
- v2：`final_remotion_line_stickers_v2.mp4`。Imagegen説明・やめ太郎4箇所の音声を修正した10分26.3秒版。制作正本はGit `a09eabbf`。
- v2の音声比較：`preview_voice_cleanup.mp4`（21.6秒）。当時の4箇所で、現行v3の音声一覧とは別。
- v2の記録と退役WAVはローカル `remotion/out/v2_records/` にも保全。現行の導入2箇所の修復は引き続き採用。

## 事実と見せ方

第一弾の販売申請はそば屋さんが担当。第二弾の候補画像を第一弾の制作記録と混同しない。肘の動き3候補は全て不採用。OpenAIのPets用スキルを参考にしたもので、OpenAI公式のLINEスタンプ制作法とは説明しない。文字の透過前は実在する白背景付き入力。完成品に汚れを加えた比較は作らない。動画内の説明用ループと元APNGの再生回数は区別する。
