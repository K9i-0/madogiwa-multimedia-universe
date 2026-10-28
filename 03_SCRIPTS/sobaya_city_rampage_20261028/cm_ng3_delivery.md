# THE SOBAYA — 採用CMオチ版

ユーザー採用: 本編の飲酒場面を30秒まで残し、NG3のずぶ濡れ撮影スタジオ映像を3秒追加。NG3の元音声は完全ミュート、既存そば屋商品コールだけを0.2秒遅延で配置し、商品ロゴを重ねる。

- 通常版: `final_the_sobaya_cm_ng3_33s_16x9.mp4`（1280×720）
- ショート: `final_remotion_cm_ng3_33s_9x16.mp4`（720×1280）
- 両方33秒、30fps、990フレーム。通常版は採用プレビューと同一ファイル内容。
- ShortsはTHE SOBAYAタイトル・同期ぼかし背景・横映像全体を保持。通常版のAACをstream copy。
- 投稿準備のみ。YouTubeへのアップロード・既存動画の削除・サイトの差し替えは行っていない。
- 30秒版と旧CM試作は保持。

再現: `node render_cm_ng3.mjs` でプレビュー生成後、通常版名へコピーし、`node render_shorts_cm_ng3.mjs`。
