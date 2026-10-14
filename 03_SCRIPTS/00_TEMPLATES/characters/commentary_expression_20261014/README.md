# 解説立ち絵：表情・発話口の追加

2026-10-14ユーザー指定。内蔵 image_gen で作成し、実送信プロンプトを同梱。

- ゆめみん：happy / blush / x / angry。原点ベースの既存立ち絵を参照、体・鼻・白い後部を維持して目と漫画的記号を変更。
- そば屋：happy_talk / beer_hold_talk / beer_cheers_talk。B案ベースの各ポーズを参照、仮面を装着したまま目・口を変更。白Tシャツの乳首描写禁止を維持。
- 生成画像は差分参照正本。動画ではそば屋の目・口のみを矩形クリップで合成し、再生成された身体の微差を出さない。口開閉中に変わるのは口領域のみ。合成座標はサンプルの ExpressionSample.tsx に記録。
- 更新動画：`03_SCRIPTS/sobaya_yumemin_sprite_sample_20261014/final_remotion_expressions.mp4`。
