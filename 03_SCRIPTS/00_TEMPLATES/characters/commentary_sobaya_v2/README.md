# そば屋・解説立ち絵 v2

2026-10-14ユーザー指定：常にビールジョッキを持つ。通常と乾杯の2ポーズを現行セットとし、「ビールを持つ」単独差分は廃止。旧セットは履歴として保持。

- `sobaya_normal.png`：通常。旧 `commentary_sobaya_v1/sobaya_beer_hold.png` を採用。
- `sobaya_beer_cheers.png`：乾杯。旧セットの乾杯を継続。
- `sobaya_normal_talk.png` / `sobaya_beer_cheers_talk.png`：既存の発話素材。画像全体を切り替えず、Remotionで口の範囲だけ合成する。目は常に通常画像の開いた状態。

口領域（x,y,w,h）：通常 `(477,300,64,63)`、乾杯 `(457,402,69,54)`。元PNGと生成プロンプトはv1および `commentary_expression_20261014` に保持。新規画像生成は行わず既存採用素材を再編。
