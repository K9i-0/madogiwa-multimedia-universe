# そば屋 B：解説用表情・ポーズ差分

2026-10-14。ユーザー選択の `../commentary_base_20261014/sobaya_proportion_b.png` を直接参照し、内蔵 image_gen で作成。比較用の再描画画像 `lineup_b.png` は生成参照に使っていない。

## 差分

- `sobaya_normal.png`： 通常
- `sobaya_happy.png`： 喜び
- `sobaya_surprise.png`： 驚き
- `sobaya_worry.png`： 困り
- `sobaya_bored.png`： 呆れ
- `sobaya_angry.png`： 怒り
- `sobaya_sad.png`： 落ち込み
- `sobaya_smug.png`： 得意げ
- `sobaya_beer_hold.png`： ジョッキを持つ
- `sobaya_beer_cheers.png`： 乾杯

各画像の実送信プロンプトは `prompt_<ID>.txt`。ジョッキ2種のみ `../character_sobaya_basic_sheet.png` を持ち物の参照として追加。全身、画面左向き、白い仮面を着けたまま、白Tシャツ・黒パンツ・白スニーカー。口パク・まばたきレイヤーは本セットには含めない。仮面を固定し、ポーズで感情を表す。

`index.html` で個別PNGの一覧を確認できる。各PNGは生成の原寸を保持。ポーズで位置に多少の差があり、動画組み込み時は足元基準で配置する。輪郭には白い残りがあるため、暗背景で使用する場合は仕上げ確認が必要。

乾杯のみ1024×1536、その他9枚は1164×1351。乾杯の外周には広い淡色のにじみが残る。`prompt_beer_cheers_alpha.txt` で除去を試したが改善せず、体型の変化もあったため修正版は不採用として初回画像を保持した。現状は差分初稿セットで、完全に仕上げた透過素材ではない。全10枚のPNG・寸法・アルファ有無を `validation.json` に記録。

2026-10-14ユーザー修正：ボディランゲージだけに限定せず、仮面を着けたまま目の形・口の開閉で表情と発話を表す。`commentary_expression_20261014` の差分と更新サンプルを参照。

現行セットは `../commentary_sobaya_v2/`。常にビール持ちの通常姿＋乾杯へ変更。このv1は旧版として保持。
