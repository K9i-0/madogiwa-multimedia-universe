# そば屋とゆめみん：立ち絵サンプル

依頼：B案のそば屋と原点画像ベースのゆめみんによるサンプル動画。ゆめみんは今回のみずんだもんを仮配役。

1. ゆめみん：今日は、そば屋さんと立ち絵のテストみん！
2. そば屋：表情も、ポーズも、ばっちりです！
3. ゆめみん：でも、なんでビールを持ってるみん？
4. そば屋：解説には、水分補給が大切です！
5. ゆめみん：それ、水じゃなくてビールみん！
6. そば屋：細かいことは気にせず、乾杯！
7. ゆめみん：仕事は、乾杯してからみん！

## 制作仕様

- 1280×720、30fps。Remotion 4.0.535（npmで安定版確認）。
- そば屋：`commentary_sobaya_v1` のB案派生PNG。白い仮面を維持。左に配置し、画像全体を反転して中央を向く。
- ゆめみん：`commentary_base_20261014/yumemin_base_v1.png`。右に配置。原点の鼻・目・シルエットを維持し、口・手を追加しない。音声RMSに合わせた軽い上下動。
- そば屋の口パクなし。発話時の軽い上下動とポーズ差し替えで発話を示す。
- 正確なセリフはRemotion字幕。メンバー色正本からそば屋赤・ゆめみん水色。
- 白背景、BGMなし。音声と立ち絵の確認用。末尾は余韻と短いフェード。
- 声：そば屋 `Aratako/Irodori-TTS-v4-Large`、正典 `02_CHARACTERS/Sobaya_voice.wav`、seed42、caption空、durationScale1、既定CFG3、既定トリム、必須monsterize後に-18 LUFSへ。
- ゆめみん：VOICEVOX 0.25.1、ずんだもん・ノーマル（style3）、speedScale1.15。仮配役でありキャラクター正典の声設定は変更しない。
- 採用音声はエピソード直下。元生成・クエリ・実行ログは `.local/sobaya-yumemin-sample/`。
- 最終タイミング正本：`remotion/src/edit-manifest.json`。実測音声尺から整数フレーム化、発話間12フレーム。
- 画像素材の輪郭残り・乾杯の淡いにじみは既存素材由来。白背景で確認するためのサンプルであり、透過素材の再仕上げは含めない。

## 再作成

`python3 prepare_voice.py` → `python3 prepare_assets.py` → `npm install --prefix remotion` → `npm run typecheck --prefix remotion` → `npm run render --prefix remotion`。

## 語尾更新

2026-10-14ユーザー指定：ゆめみんの語尾を「〜みん！」へ変更。疑問文は「〜みん？」。ずんだもんの仮声と話速は維持。ゆめみん4行のみ再生成し、そば屋3行は既存音声を保持。旧完成動画も保持。

完成：`final_remotion_sample_min.mp4`、22.5秒、1280×720、30fps、675フレーム。全編デコードと字幕4箇所の視覚確認済み。音声はASR自動照合、通し試聴は未実施。

## ゆめみん仮音声3版

2026-10-14ユーザー指定：雨晴はう（style10）、冥鳴ひまり（style14）、小夜/SAYO（style46）のノーマルで比較。ローカルVOICEVOXのspeakers応答でID確認。語尾・そば屋音声・絵は維持。話速1.15、音高0、抑揚1、-18 LUFS。

`prepare_voice_variants.py` → `render_variants.py` で再生成。タイミング正本は `remotion/src/manifest_{hau,himari,sayo}.json`。比較用音声は未採用素材として `.local/sobaya-yumemin-sample/voice-variants/` に保持。現行のずんだもん版・正典音声設定は変更しない。

確認ページ：`voice_comparison.html`。版ごとのクレジットは `youtube_description_<ID>.txt`。

3版とも720p・30fps、所定フレーム数と全編デコードを検証。冒頭の話者版名・字幕・立ち絵を視覚確認。Whisperによる自動照合済み。特殊語尾「みん」の転記揺れあり、聴感・発音の自然さの通し試聴は未実施。

## 表情・口パク版（2026-10-14）

ユーザーが雨晴はう音声を採用し、音声に問題がないことを確認。採用版と同じ音声・尺を維持し、映像だけを変更。

- ゆめみん：笑顔、照れ、×目、怒り目＋赤い怒りマークの画像差分を会話に合わせて切替。上下動は補助として抑制。
- そば屋：仮面を装着したまま笑い目と黒い発話口を使用。元画像を体の正本とし、画像生成した目・口の領域のみをRemotionで合成。発話口は30fpsの音声RMSと3フレーム単位の開閉で切替、休止中は閉じる。音素別の精密リップシンクではない。
- 笑顔/ジョッキ持ち/乾杯の3ポーズに発話口を追加。姿勢や頭部の位置は口開閉によって変わらない。
- 新規画像：`03_SCRIPTS/00_TEMPLATES/characters/commentary_expression_20261014/`。内蔵画像生成、プロンプト同梱。
- 構成：`Expressive`、実装 `ExpressionSample.tsx`、整数フレーム正本 `manifest_expressions.json`。
- 出力：`final_remotion_expressions.mp4`。前版保持。

## そば屋の目を通常状態へ統一

ユーザー指定により、笑い目の合成を外し、全ポーズで元の開いた目を使用。口パク・ゆめみんの表情・採用音声・尺は維持。`final_remotion_expressions.mp4`へ再書き出し。

## 常時ジョッキ持ち（2026-10-14）

通常姿をジョッキ持ちへ変更。単独のbeer_hold差分は現行定義から外し、通常・乾杯の2ポーズを使用。目は常時開いたまま、口パクと音声は維持。素材正本：`commentary_sobaya_v2`。
