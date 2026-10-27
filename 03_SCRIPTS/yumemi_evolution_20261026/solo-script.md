# ゆめみん単独版（追加字幕なし）

ユーザー指定：やめ太郎の声・立ち絵を外し、ゆめみんだけに変更。今回の追加字幕は不要。

- ゆめみんの立ち絵を全画面の元動画へ直接重ねる。
- 元動画内の説明文字は保持し、Remotionの会話字幕を全て除去。
- 既存のゆめテレアナウンサー音声4行を継続使用。やめ太郎の音声を含めない。
- ツッコミ枠を除去して説明を続け、各場面の再生速度を再計算。音声の速度・ピッチは維持。
- 20.133秒、604フレーム、1920×1080、30fps。
- 正本：`remotion/src/solo-manifest.json`、`Solo.tsx`、composition `YumemiSolo`。
- 出力：`final_remotion_yumemin_only.mp4`。

再レンダー：`npx remotion render src/index.ts YumemiSolo ../final_remotion_yumemin_only.mp4 --codec=h264 --crf=16`

音声設定は `duo-generation.json` のanchorの4行を参照。前版の動画・コードは保持。
