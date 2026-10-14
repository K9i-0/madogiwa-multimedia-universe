# Codexで動画まで作る。窓際族物語のAI制作術 — v7

`../script.md` の完成稿120発話を映像化。やめ太郎・たこさんの導入、動画モデルと提供会社、Remotionの文字合成、日本円の生成料金、Gitで制作ノウハウを残す話を反映する。旧v6はGitコミット `d7d55361` から再現でき、旧MP4と採用音声も保持する。

## 正本

- `dialogue.json`：承認済み本文・話者・読み・生成尺・発話後の間。
- `src/edit-manifest.json`：音声実測から作る整数フレームのタイムライン、字幕の分割区間、口パク波形。
- `src/VisualAid.tsx`：v7の発話ごとの資料。`VisualAidLegacy.tsx` は継承する図解部品。旧音声の切替キューは使用しない。
- `src/visual-cues-v7.json`：新しいVOICEVOX音声クエリから求めた発話内の強調位置。Irodori字幕の分割は本文の位置による補助時刻。
- `caption-layout-v7.json`：長文13発話の意味単位の字幕ページ・改行指定。
- `clips_config.json`：第53話の完成例と修復前後、第72話の別実験。作例中はBGM・実況を停止。
- `../voice_record_v7.json`：採用音声のモデル、参照、設定、読み、SHA-256。`../adopted_audio_v7.json` は正本WAVとpublic音声の対応。
- `../scenario_v7.json`、`../sources_v7.json`：モデル、料金、使用素材の根拠。`../youtube_description.txt`：出典・クレジット・公開リポジトリURL。YouTubeへの公開は行わない。

## 音声と字幕

やめ太郎はIrodori v4.1-Small・正典参照・seed 7・本文CFG 5・captionなし・トリムなし。短文0.7、長めの台詞0.85を出発点とし、読み落とし疑いを個別修正する。生成後の早送りは行わない。たこさんはVOICEVOX:中国うさぎ・ノーマル61、速度1.1、音高0、前無音0.10秒・後無音0.20秒。

字幕は29pxを保ち、長文を意味単位で複数画面へ分割する。1画面2行以内・最大770px。VOICEVOXは元クエリのモーラ長と前無音、速度を用いて分割・強調時刻を算出する。ASRの一致や音量の数値だけで主観的な聞き心地を保証しない。

冒頭はBGMを2.5秒先行。本編は第2章から、エンディング曲は第9章から。−18 LUFSの会話、−34 LUFSのBGM、−38 LUFSのUnityを出発点にミックス。末尾クレジットは設けず、静かにフェードする。

## 再現

```sh
../../../.local/Irodori-TTS/.venv/bin/python prepare_v7_voice.py
../../../.local/voicevox-explainer/venv/bin/python finalize_v7_timing.py
npm run typecheck
../../../.local/voicevox-explainer/venv/bin/python validate_timeline.py
node preview_v7.cjs
npm run render -- --output out/review_v7_01.mp4
```

音声を再生成せず復元する場合、`adopted_audio_v7.json` の `file` を `publicAudio` へhardlinkまたはコピーし、SHA-256を照合する。元素材・BGMは既存publicを使い、リポジトリ画面は `../repository_public_v7.png` を `public/` へ配置する。

`prepare_v7_voice.py` は音声の設定と本文をハッシュで識別する。変更後は必ず `finalize_v7_timing.py` を再実行。作例と字幕のタイミングに旧版の秒数を流用しない。

## 検証

```sh
../../../.local/Irodori-TTS/.venv/bin/python audit_v7_audio.py
../../../.local/Irodori-TTS/.venv/bin/python audit_v7_secondpass.py --ids <確認する発話ID>
../../../.local/voicevox-explainer/venv/bin/python audit_video_v7.py --source out/review_v7_03.mp4 --tag v7
../../../.local/voicevox-explainer/venv/bin/python final_checks.py --source ../final_remotion_ai_video_workflow_v7.mp4 --tag v7
```

全字幕ページと強調切替をプレビューし、完成MP4からも発話・作例・切替・末尾を抽出して確認する。全編デコード、尺、音量、音声の重複・欠落を機械的に検査。主観的な通し試聴はこの実行環境では未実施として記録する。

監査後に `adopt_v7_audio.py` で採用WAVと概要欄の実測チャプターを保存する。動画・中間素材・監査画像はGit管理外。採用音声・入力画像・再現コード・記録を追跡する。

## v7完成版

`../final_remotion_ai_video_workflow_v7.mp4`（15分15.3秒、720p）。検証結果は `../delivery_v7.json` と `../review_v7.md`。YouTube未公開。

## v7改訂4：参考画像の連続表示・ニュース全編

参考画像の親要素から発話ごとのフェード・上下移動を削除。字幕切替と独立して表示し、図解内部の意図した強調は維持する。ニュース完成例は900フレーム（30秒）すべてを使う。`clips_config.json` の変更後は `python3 retime_clips.py` で採用音声・字幕の相対タイミングを保持して時系列と概要欄チャプターを更新し、ミックスとレンダーを再実行する。

`node audit_reference_continuity.cjs` は同じ参考画像が続く発話境界の直前・当該・直後を出力する。字幕途中の画像だけでなく、この境界を確認する。完成版は `../final_remotion_ai_video_workflow_v7_04.mp4`、15分36.7秒。

## v7改訂5：白・紺・青・黄の解説画面

`src/theme.ts` に配色とカード・見出しを集約。非注目項目の文字を薄くせず、黄色で強調する。字幕は共通の話者色から濃色を計算し、この作品内だけで適用する。

完成版 `../final_remotion_ai_video_workflow_v7_05.mp4`（15分36.7秒）。配色記録 `../design_v7_05.json`、検査記録 `../review_v7_05.md`。音声・タイムラインを変更しないため、`npm run render -- --skip-mix --output out/review_v7_05.mp4` で書き出す。

## v8：会話・料金・短い締め

`../script.md` と `dialogue.json` が118発話の正本。変更33発話の音声を差し替え、85発話は既存の採用音声を継続使用。Wan 3.0の読みは「ワン、サンテンゼロ」。台詞と中央図解の「道具」は「ツール」に統一する。

通常価格・30％割引価格は説明用の1ドル160円換算。平均約300円／完成30秒に生成約60秒はユーザー提供の制作実績として区別する。最後は3発話・約25秒。

```sh
../../../.local/Irodori-TTS/.venv/bin/python prepare_v8_voice.py
../../../.local/voicevox-explainer/venv/bin/python finalize_v8_timing.py
npm run typecheck
../../../.local/voicevox-explainer/venv/bin/python validate_timeline.py
node preview_v8.cjs
npm run render -- --output out/review_v8_01.mp4
```

採用音声は `../adopted_audio_v8.json` と `../voice_record_v8.json`。`adopt_v8_audio.py` で採用WAVと実測チャプターを保存する。音声検査は `audit_v8_audio.py`、`audit_v8_secondpass.py --ids ...`、ミックス検査は `audit_mix_v8.py`。完成MP4の全編抽出は `audit_video_v8.py`、切替境界は `audit_revision_v7_04.py --source out/review_v8_01.mp4 --tag v8_boundaries`（現行manifestから時刻算出）、最終codec・尺・音量は `final_checks.py --source out/review_v8_01.mp4 --tag v8`。

完成版 `../final_remotion_ai_video_workflow_v8.mp4`、検査記録 `../review_v8.md`。短くしたエンディングの確認用抜粋も作成する。YouTube未公開。

## v9：役割の整理・Irodori補足・冒頭無音作例

`prepare_v9_voice.py` → `finalize_v9_timing.py` → `preview_v9.cjs` → `npm run render`。
`audit_v9_audio.py` / `audit_v9_secondpass.py`で変更音声を照合し、`audit_video_v9.py` / `audit_continuity_v9.py` / `final_checks.py --tag v9`で完成MP4を検査する。
冒頭は`VisualAid.tsx`内の固定フレームSequenceで連続再生し、両方ともmuted。素材と使用範囲は`../sources_v9.json`を参照。
採用動画：`../final_remotion_ai_video_workflow_v9.mp4`。YouTube未公開。

## v10：自己紹介と既存表情の活用

`prepare_expression_assets.py`で共有の32枚をpublicへ配置。`src/expressions-v10.json`で発話ごとに話者／聞き手の表情を指定する。
`prepare_v10_voice.py` → `finalize_v10_timing.py` → `preview_v10.cjs` → `npm run render`。
音声監査は`audit_v10_audio.py` / `audit_v10_secondpass.py --ids v132 v133 v134`。
完成映像は`audit_video_v10.py`、`qa_compare_v10.py`、`final_checks.py --tag v10`で監査。
採用動画：`../final_remotion_ai_video_workflow_v10.mp4`。YouTube未公開。

## v11：導入スライドと言い回し

`prepare_v11_voice.py` → `finalize_v11_timing.py` → `preview_v11.cjs` → `npm run render`。
音声差分はv008・v134のみ。自己紹介スライドの見出しを削除し、テーマを「窓際族物語のような動画」へ広げた。
`audit_v11_audio.py` / `audit_v11_secondpass.py --ids v008 v134`、`audit_video_v11.py` / `qa_compare_v11.py` / `final_checks.py --tag v11`で検証する。
採用動画：`../final_remotion_ai_video_workflow_v11.mp4`。YouTube未公開。
