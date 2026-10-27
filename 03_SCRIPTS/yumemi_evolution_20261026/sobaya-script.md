# ゆめみん＋そば屋 ツッコミ比較版

ユーザー指定：やめ太郎のセリフをそのままそば屋の声・立ち絵へ置換して試す。直前の追加字幕なしを継承。ゆめみん単独版は保持。

## セリフ

そば屋：公式が何してんねん！
そば屋：本業どこ行ったんや！
そば屋：しかも売れとるんかい！
そば屋：そっちに進化すな！

ゆめみんのアナウンサー原音4行は既存のものを使用。

## 編集

元動画を全画面にし、左ゆめみん、右そば屋の立ち絵を直接重ねる。追加字幕なし。元映像内の説明文字は保持。そば屋は `commentary_sobaya_v2` のビール保持通常立ち絵と口領域だけの発話差分を使用。仮面・目・体・ジョッキを固定し、発話口は音量包絡に合わせる。

アナウンサーの語尾へ食い気味に重ね、次の説明へすぐつなぐ。元動画の場面別速度を音声実測尺へ合わせる。

## 音声

`Aratako/Irodori-TTS-v4-Large`、正典 `02_CHARACTERS/Sobaya_voice.wav`、seed42、caption「食い気味に、勢いよくツッコむ。」、CFG3、自動尺倍率1、既定トリム。生成後 `tools/sobaya_monsterize.sh` による正典加工（pitch -5 semitones / tremolo70Hz）。やめ太郎用の尺倍率0.70は適用しない。

生成元・SHA・尺は `sobaya-generation.json`、編集配置は `remotion/src/sobaya-manifest.json` を正本にする。原音・未採用候補・ASR・生成ログは `.local/yumemi_evolution_20261026/sobaya/`。

## 再現

Composition `YumemiSobaya`、`SobayaDuo.tsx`。出力 `final_remotion_sobaya_tsukkomi.mp4`。

`npx remotion render src/index.ts YumemiSobaya ../final_remotion_sobaya_tsukkomi.mp4 --codec=h264 --crf=16`

聴感はユーザー試聴待ち。ASRと機械検証を試聴合格と区別する。

## 確認記録

25.8667秒（776フレーム）、1080p、30fps。全4セリフの「！」を保持。TypeScriptと話者・音声・4か所の重なり・映像区間の整合性を検証。追加字幕とやめ太郎アセットが含まれないことを確認。
