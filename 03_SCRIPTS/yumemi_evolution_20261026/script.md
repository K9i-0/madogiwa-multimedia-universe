# ゆめみ、進化の過程 — アナウンサーナレーション試作

2026-10-26。ユーザー指定：Remotion + Irodori、ゆめテレアナウンサー。

## 完成原稿

進化を続ける、ゆめみ。
大喜利から、芸能事務所へ。
そして、AIドラマにグッズ展開。
目指すは、テック業界の吉本興業。

## 編集

- postproduction=remotion / composition=MadogiwaEdit
- 入力：リポジトリ直下 `b00add6f490fbcdb0005bb2f101e92f4.MP4`
- 出力：`final_remotion_narration.mp4`、1920×1080・30fps・465フレーム（15.5秒）。元素材の1080pを保持。
- 原画・文字・速度を保持。追加字幕・ニュース帯・BGMなし。
- ゆめテレの声だけを採用する紹介映像。ニュース番組の画面には変更しない。
- 音声の生成条件は `voice-generation.json`、フレームの配置・切り出しは `remotion/src/edit-manifest.json` が正本。
- 生成全体の無音区間で文を分けて配置。発話の速度・ピッチを変更せず、冒頭へ「進化を続ける、ゆめみ」を移動。
- 採用候補音声：`clip1_line1_yume_tele_anchor.wav`。未採用テイク・ログ・ASRは `.local/yumemi_evolution_20261026/`。

## 再現

`remotion/public/input.mp4` に元素材のhardlink、`remotion/public/narration.wav` に上記WAVを配置して、`npm ci`、`npm run typecheck`、`npm run render`。

## 確認

機械的な音声全文照合・音声区間・映像検証を実施する。実際の通し試聴は本環境では実施できないため、声の自然さはユーザー試聴待ち。機械照合を聴感合格としない。

## 読み修復と検証結果

- 最終文はSmallの機械照合で「吉本興業」に一致しなかったため、同じ正典参照・seed 2026でIrodori v4 Largeを使用して全文を再生成。3.560042秒、`clip1_line2_yume_tele_anchor.wav`。音韻として「よしもとこうぎょう」が一致（ASR表記は「吉本工業」）。
- 全クリップを一定ゲイン0.85で配置し、ピークに余裕を確保。
- TypeScript、manifest validator、465フレーム全編デコードに合格。元映像との全編SSIM 0.993008、クロップ・速度変更なし。
- 元動画・中間音声・レンダーはGitへ追加しない。再現素材は `python3 remotion/prepare_assets.py` で配置可能。
- 完成MP4のASR：進化を続ける夢見／大喜利から芸能事務所へ／そしてAIドラマにグッズ展開／目指すはテック業界の吉本工業。固有名詞の漢字表記以外は全文一致。

## 2026-10-26 定番SE＋文間調整試作
- 出力: `final_remotion_yumemin_familiar.mp4` / Remotion `YumemiFamiliar`、1920×1080、30fps、649frames（21.633秒）。
- 既存ゆめみん単独版の採用音声を維持。a1/a2/a3後へ8/7/10framesの間、末尾へ20framesの余韻を追加。文中の間と音声速度は変更せず、各背景シーンの再生速度を尺に合わせた。
- 効果音ラボ https://soundeffect-lab.info/sound/anime/ の和太鼓でドドン、パフ、レベルアップ、金額表示、ちゃんちゃん♪2を使用。利用規約 https://soundeffect-lab.info/agreement/ 確認。素材はpublic/familiar-localにローカル保持しGit除外、再配布しない。
- タイミング正本: relaxed-manifest.json / familiar-sfx-manifest.json。再取得と仕様再構築: remotion/prepare_familiar.py。
- TypeScript検証、649フレームのレンダー、全編デコード、静止画確認済み。実音の通し試聴は未実施（環境の音声入力非対応）。
