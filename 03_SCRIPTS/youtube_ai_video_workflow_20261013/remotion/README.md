# Codexで動画まで作る。窓際族物語のAI制作術 — やめ太郎＆たこさん版

やめ太郎が「ワイも動画を作ってみたい」と質問し、たこさんが実際の制作例で解説する。ユーザー指定の3台詞を導入に使い、第53話を主線とする説明、キャラクターシート、音声修復、料金、スキルの改善過程を引き継ぐ。

今回の完成版は `../final_remotion_ai_video_workflow_v3.mp4`。仕様と実測尺は `../delivery_v3.json`、確認結果は `../review_v3.md`。旧VOICEVOX版の完成MP4と確認記録は保存する。旧版のコード一式はGitコミット `9aa43d7f` で再現できる。

## 正本

- `dialogue.json`：111発話の本文、話者、字幕改行、発音用文面、必要な生成尺調整。
- `clips_config.json`：作例と音声比較の挿入位置、範囲、BGM停止。
- `src/edit-manifest.json`：生成音声から算出したフレーム単位のタイムラインと口パク波形。
- `../duo_adopted_audio.json`、エピソード直下の `duo_v3_*.wav`：採用音声と復元用の対応表。
- `../duo_voice_record.json`：Irodoriモデル、正典参照、seed、設定、音声ハッシュ。
- `../asset_sources.json`、`../inputs/duo/`：採用立ち絵6枚と由来。既存差分の目・口部分だけCSSマスクで使用し、全身の位置を固定する。
- `../sources.json`、`../evidence_v2.json`：解説に使う制作ログ・価格・実例の根拠。配役変更で実例の生成履歴は変更しない。

やめ太郎は左で左右反転、たこさんは右。白レンズを維持し、やめ太郎にまばたきを追加しない。字幕色は共通の `00_TEMPLATES/subtitles/member-colors.ts` を参照する。

## 音声

Irodori-TTS v4.1-Smallを正典参照で新規合成する。既存動画内の声を修正する工程とは別であり、音声修復用Largeへ自動的に切り替えない。

- やめ太郎：`02_CHARACTERS/Yametaro_voice.wav`、seed 7。
- たこさん：`02_CHARACTERS/Takosan_voice.wav`、seed 43。
- captionなし、本文CFG 5、40 steps、トリムなし、生成後の速度変更なし。
- やめ太郎の短文は生成尺倍率0.70を出発点とする。長めの台詞は自動尺、個別に調整した台詞は `durationScale` を指定する。たこさんは自動尺。
- 原文と発音用文面を分ける。専門用語と数値を読める表記にし、ユーザー指定の台詞の字幕本文を保持する。

## 再現

このディレクトリで実行する。Node.js、ffmpeg、ローカルIrodori環境と元素材が必要。モデルを一回読み込み、発話ごとに逐次生成する。GUI操作や新しいWan有料生成は行わない。

```sh
npm ci
../../../.local/voicevox-explainer/venv/bin/python prepare_assets.py
../../../.local/Irodori-TTS/.venv/bin/python prepare_voice.py
../../../.local/Irodori-TTS/.venv/bin/python audit_audio.py
npm run typecheck
../../../.local/voicevox-explainer/venv/bin/python validate_timeline.py
npm run render -- --output out/review_v3_01.mp4
```

`prepare_voice.py` は現在の配役用 `prepare_duo_voice.py` を呼び出す。モデル、参照ハッシュ、本文、seed、生成尺倍率などをキャッシュ識別へ含める。`--ids u003` などで部分生成も可能。未生成行が残る場合は完成マニフェストを更新しない。生成進捗は `out/duo_progress.json`。`audit_audio.py` は未照合のWAVを順次確認するため、生成中に別プロセスで開始してもよい。

`mix_audio.py` は各新規発話を−18 LUFSへ調整したうえで合成し、全体を整える。比較映像ではBGM・実況を止める。通常BGMは−34 LUFS、Unityは−38 LUFSを出発点に、締めで持ち上げず4秒フェードする。出力は48kHz stereo。

映像のみの修正は `render.py --skip-mix` で既存ミックスを利用できる。候補は別名へ書き出す。導入確認用 `preview_duo.py` は最初の8発話から短いMP4を作る。

## 監査・採用

```sh
../../../.local/voicevox-explainer/venv/bin/python audit_video.py --source out/review_v3_01.mp4 --tag v3_01
../../../.local/voicevox-explainer/venv/bin/python final_checks.py --source out/review_v3_01.mp4 --tag v3_01
../../../.local/Irodori-TTS/.venv/bin/python audit_mix.py
```

全発話の表示中、引用の開始・中間・終了、図解の変化後、締めをMP4から抽出し、文字・顔・素材との対応を目視する。ASRは自動スクリーニングであり、自然さ・声質・精密な口元同期の合格と同一視しない。主観的な通し試聴をできなかった場合は記録する。

候補を採用後、完成名へ保存して最終検査する。既存の完成ファイルは暗黙に上書きしない。

```sh
cp -n out/review_v3_01.mp4 ../final_remotion_ai_video_workflow_v3.mp4
../../../.local/voicevox-explainer/venv/bin/python final_checks.py --tag v3
../../../.local/voicevox-explainer/venv/bin/python adopt_duo_audio.py --version v3
```

動画・中間音声・監査画像はGit管理外。採用したセリフWAVだけエピソード直下へ保存し、参照ハッシュ・設定・コードとともに管理する。元動画・BGMにはローカル保持の素材があるため、Gitだけで全素材がそろうわけではない。公開・アップロードは別作業。
