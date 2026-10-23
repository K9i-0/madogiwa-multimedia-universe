# 秋のちくわ狩りニュース

2026-10-23。今回はユーザー指定により動画生成不要の部分のみ制作。Wan API実行なし。

## 完成済みパート

`completed_nonvideo_parts.mp4` は完成パートだけを順に並べた確認用コンピレーション。本編完成版ではなく、収穫・専門家の可視発話・そば屋の転倒を省略している。1280×720、30fps、503フレーム、約16.77秒。

|ファイル|内容|フレーム数|
|---|---|---:|
|part_01_intro.mp4|25話から「続いて、季節の話題です」の映像・音声を流用|120|
|part_02_forest.mp4|imagegenの群生画像＋緩やかな寄り＋正典アナウンス|138|
|part_03_comparison.mp4|食用と88話の毒ちくわ比較＋おかやまんの正典音声|143|
|part_04_interruption.mp4|Remotionの中断画面＋正典アナウンス|102|

タイミング正本：`remotion/src/edit-manifest.json`。postproduction=remotion、visual_preset=yume_tele_news_v1。過去映像の右上局ロゴと右下7:00は新しい局ロゴと不透明なニュース帯で隠し、左上19:00へ統一。素材の顔・発話は加工しない。

## 今後の本編

1. 冒頭→山の紹介（完成）
2. よーたん「今年は肉厚ですね。焼き目もきれいについてます」／福ギュン「今夜はおでんですね」。収穫動作の動画は未生成。
3. 研究室のおかやまん：共通導入「そうですね。注意が必要です」。口元の動く動画は未生成。
4. 比較図＋おかやまん「食用と非常によく似ていますので、見た目だけで判断しないでください」（完成）。必要なら本編でその前に毒ちくわ発生の紹介を追加。
5. 福ギュン「こちらも、おいしそうなのが採れました」。88話と同じ紫・黒紫・赤紫・黄緑の毒ちくわ。そば屋が現地へ現れ食べ、「これ、毒ちくわです」。一拍後に倒れ、よーたん「えっ……」。動画は未生成。
6. 中継中断（完成）。

## おかやまん共通素材

`okayaman_expert_clean.png`：正典Okayaman.jpgの顔を基準にimagegenで制作した文字なし16:9研究室画像。チャコールジャケット、灰色シャツ、正面胸上、閉口。今回固有のちくわ・肩書き・文字を持たせていない。今後の導入・聞き姿・反応動画の共通入力として再利用できる。動く共通素材3種はまだ生成していない。

`okayaman_expert_card.png`：Remotionで肩書きを合成した見本。文字なし正本とは区別する。所属「窓際大学大学院 農学研究科 准教授」、専門「森林生物資源学」。映像へ名前等を焼き込まずRemotion側で変更する。

## 音声

今回の新規3発話はIrodori-TTS-v4.1-Small。参照はVOICE_CAST.mdのYumeTeleAnchor_voice.wav（seed2026）とOkayaman_voice.wav（seed42）。caption、本文はgenerate_voices.shが正本。CFG5、duration scale1、自動尺、uncut1、速度変更なし。アナウンサー4.20秒、比較約4.36秒、中断2.72秒。表示フレームは実測音声長に余韻を追加。声の再生成用の正典WAVは02_CHARACTERSに既存追跡済み。

自動文字起こしで3発話を照合。比較・中断は文面一致。山の紹介は「ちくわがり」「再生期」と認識されたが、発音は原文「ちくわ狩り」「最盛期」と同音。ASRのみで実試聴済みとは扱わない。聴感・声質・語尾の最終試聴は未確認。

## 検証

TypeScript型チェック成功。720p/30fps/H.264/AAC、全編デコード成功。群生・比較・肩書き画面をレンダー後に目視し、文字のはみ出し、顔と主要小道具の隠れを確認。imagegenの3入力画像も目視確認済み。

## 再現

`python3 prepare_assets.py` → `cd remotion && npm ci && npm run typecheck && npm run render` → `cd .. && python3 prepare_assets.py`。
Remotion 4.0.538（2026-10-23 npm view確認）。個別の再レンダーはcomposition intro / forest / comparison / interruption。肩書き画像は`npx remotion still src/index.ts ExpertCard out/expert_card.png`。

画像は内蔵imagegen使用。入力プロンプトはprompt_imagegen_*.txt。生成画像のデフォルト保存元はCodex generated_images、正本は本フォルダへコピー済み。
