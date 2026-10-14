# 解説用立ち絵：そば屋・ゆめみん 基本画像初稿

2026-10-14、内蔵 image_gen で生成。表情差分制作前の確認用。既存正典の差し替えは行わない。

- `sobaya_base_v1.png`: 既存たこさん・やめ太郎の3Dトイ調を参考にデフォルメ。左向き、通常、全身、白い仮面とグレー肌、白Tシャツ、両手を下げた基本姿勢。
- `yumemin_base_v1.png`: `02_CHARACTERS/Yumemin.jpg` を直接参照。原点の2D輪郭、青い丸い体、白い後部、短い鼻を基本にした通常姿。
- 各画像は透過PNG。実送信プロンプトは `prompt_sobaya.txt` と `prompt_yumemin.txt`。

後続差分の対応予定は既存 `commentary_duo_v1` と同じ normal / happy / surprise / worry / bored / angry / sad / smug の8種。今回は基本画像のみ作成。ゆめみんには腕や手を追加せず、そば屋は仮面を装着したまま表情・ポーズを設計する。
