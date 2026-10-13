# Codexで動画まで作る。窓際族物語のAI制作術 — v6

> 次回制作のシナリオ完成稿は `../script.md`（v7）。v7はまだ音声生成・動画化していない。このディレクトリのdialogue・manifest・描画コードは完成動画v6の再現用。v6の旧台本はGitコミット `1334d02c` で参照できる。

やめ太郎の「ネタはあるのに、編集の操作で止まる」という悩みから、いつものAIで動画を作る流れを紹介する。導入は共感→第53話の完成例→内容の全容。本編は会話の欲求・失敗から道具の説明へ進め、参照画像の情報設計、部分音声修復、費用、制作ログからのスキル改善まで扱う。

完成版：`../final_remotion_ai_video_workflow_v6.mp4`。実測仕様：`../delivery_v6.json`。確認・修正記録：`../review_v6.md`。旧版MP4と記録は保持する。v4コードはGit履歴で再現可能。YouTubeへの公開・アップロードは行わない。

## v6の画面方針

会話はv5の123発話と採用音声を維持。中央の解説画面を `src/VisualAid.tsx` に刷新し、重複する説明文・見出し・出典を減らした。画像比較、料金の棒、音声区間、短い工程図を用い、今の話題を強調する。細かな出典・クレジットは概要欄と `sources.json` に保持する。

`src/visual-cues-v6.json` は発話内の整数フレーム。主要な説明の切替は採用VOICEVOXクエリのモーラ時間（前無音を含み、速度1.1で換算）を参照した。語句ごとの主観的な聞き取り検証とは区別する。台詞を変更したらキューも再設定する。

静止画プレビュー：`node preview_visuals_v6.cjs`。音声の再生成は不要で、既存 `public/mixed.wav` を使う場合は `npm run render -- --skip-mix --output out/review_v6_01.mp4`。

## 正本

- `dialogue.json`：本文・話者・読み・字幕改行・発話後の間・Irodoriの生成尺補正。
- `clips_config.json`：ニュース作例と音声修復比較の範囲、原音・BGM停止。
- `src/edit-manifest.json`：採用音声から算出した整数フレームのタイムラインと口パク波形。
- `../voice_record_v5.json`：モデル・参照・seed・VOICEVOXクエリ・実測尺・音声ハッシュ。
- `../adopted_audio_v5.json`、`../v5_*.wav`：採用セリフとpublic内ファイルとの対応。
- `../script.md`：章・会話・画面指示・完成版の発話開始時刻。
- `../sources.json`、`../evidence_v2.json`：料金・過去の制作ログ・台本構成の参考記事。
- `../youtube_description.txt`：概要欄用クレジットと出典。専用の末尾カードは表示しない。

## 配役・音響

やめ太郎は左で左右反転、たこさんは右。既存の採用立ち絵を維持する。白レンズを維持し、やめ太郎にまばたきを付けない。字幕色は `00_TEMPLATES/subtitles/member-colors.ts` が正本。

- やめ太郎：Irodori-TTS v4.1-Small、正典 `Yametaro_voice.wav`、seed 7、captionなし、本文CFG 5、トリムなし。短文の生成尺0.7を出発点に、台詞ごとに0.85 / 1.0へ調整。生成後の早送りはしない。変更のない採用音声は再利用。
- たこさん：VOICEVOX:中国うさぎ・ノーマル、speaker 61、速度1.1、音高0、抑揚1、音量1、48kHz mono。掛け合い用に前無音0.10秒・後無音0.20秒。発話間はタイムライン側で管理する。
- 通常の発話後は9〜12フレーム、オチは18フレーム等。字幕を縮小しすぎず、意味の切れ目で2行以内に分ける。
- 各セリフを−18 LUFSへ整えてミックス。BGMは−34 LUFS、Unityは−38 LUFSを出発点とし、締めで持ち上げない。原音比較中はBGMと実況を止める。最終48kHz stereo。

## 再現

このディレクトリで実行する。ローカルIrodori、VOICEVOX（127.0.0.1:50021）、元素材、FFmpegが必要。

```sh
npm ci
../../../.local/Irodori-TTS/.venv/bin/python prepare_voice.py
npm run typecheck
../../../.local/voicevox-explainer/venv/bin/python validate_timeline.py
npm run render -- --output out/review_v6_01.mp4
```

`prepare_v5_voice.py`は生成本文・設定・モデル・参照ハッシュをキャッシュ識別へ含める。進捗は`out/v5_progress.json`。台詞変更後の古い音声流用を防ぐ。導入だけの候補は`preview_v5.py`で生成可能。

採用WAVをpublicへ復元する場合は `adopted_audio_v5.json` の `file` → `publicAudio` へhardlinkし、SHA-256を確認する。音声合成環境の版が異なる場合は、再生成と採用WAVの復元を区別する。

## 監査

```sh
../../../.local/Irodori-TTS/.venv/bin/python audit_v5_audio.py
../../../.local/Irodori-TTS/.venv/bin/python audit_v5_secondpass.py
../../../.local/voicevox-explainer/venv/bin/python audit_video.py --source out/review_v6_01.mp4 --tag v6_01
../../../.local/voicevox-explainer/venv/bin/python final_checks.py --source out/review_v6_01.mp4 --tag v6_01
```

全発話、資料映像の開始・中間・終了、図解の切替、末尾をMP4から抽出して確認する。ASRは本文をプロンプトで教えずにスクリーニングし、不確かな発音は別のモデルでも照合する。ASRや数値検査で主観的な聞き心地を保証しない。今回、主観的な通し試聴は実施できないため、機械的な検査と視覚確認を分けて報告する。

v5の音声採用時は `adopt_v5_audio.py` で採用WAV・対応表・章時刻・概要欄・出典情報を保存した。画面のみのv6改修では実行不要（同スクリプトはv5の台本ヘッダーを再生成するため）。動画、中間WAV、監査画像、旧候補はGit管理外。採用セリフWAVと再現コードを追跡する。

旧v5の全編確認後の資料表示修正は `render_visual_patches.py` と `../visual_revision_v5.json` に記録。通常の再現は更新済みmanifestから全編レンダーすればよい。部分差し替えは既存の候補MP4がある場合だけ使用する。
