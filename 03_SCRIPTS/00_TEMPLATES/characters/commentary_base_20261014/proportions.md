# そば屋の頭身比較候補

内蔵 image_gen で元の `sobaya_base_v1.png` を編集。いずれも未採用の比率比較用候補。

指定した頭身と生成結果は一致していないため、以下は髪頂部〜顎を1単位にした画像上の目視概算。

| 候補 | 実際の概算 | 画像 | 実送信プロンプト |
|---|---|---|---|
| A | 約2.6頭身 | sobaya_proportion_a.png | prompt_sobaya_3h_v2.txt |
| B | 約3.7頭身 | sobaya_proportion_b.png | prompt_sobaya_3_5h.txt |
| C | 約3.9頭身 | sobaya_proportion_c.png | prompt_sobaya_3h.txt |

Aには周囲の淡いハローが残っており、採用後の完成透過素材にする際は除去が必要。BとCにも輪郭の白い残りがあるため、現段階は頭身確認用。4頭身指定の初回結果はハローが強く、Cと近いため候補から除外（生成元に保持）。元画像とゆめみんは変更していない。
