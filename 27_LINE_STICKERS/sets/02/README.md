# 第2弾：そば屋オンリー8個

採用済みA案の構図をもとに8点を個別に描き直し、キャラクターシートを優先して仮面の輪郭・黒い目の穴・丸端の細い口・赤い模様を修正。第一弾の太い黒線とセル塗りを継承。最終の描き直し・動きは確認待ち。LINE未申請。

[白背景の8点GIF](all-members-white-preview.gif) / [黒背景の8点GIF](all-members-black-preview.gif)

[白背景静止一覧](all-members-white-still.png) / [黒背景静止一覧](all-members-black-still.png) / [顔の拡大確認](reports/face-review.png)

| # | セリフ | 動き | 個別ファイル |
|---|---|---|---|
| 1 | おはよう | 手を振り、口元の輝きが明滅 | [PNG](stickers/01_ohayo/master.png) / [GIF](stickers/01_ohayo/preview.gif) / [APNG](stickers/01_ohayo/sticker.png) |
| 2 | 乾杯！ | 乾杯のジャンプを2回 | [PNG](stickers/02_kanpai/master.png) / [GIF](stickers/02_kanpai/preview.gif) / [APNG](stickers/02_kanpai/sticker.png) |
| 3 | 冷えてる。待遇も。 | 上半身が寒さで震え、雪が流れる | [PNG](stickers/03_hieteru/master.png) / [GIF](stickers/03_hieteru/preview.gif) / [APNG](stickers/03_hieteru/sticker.png) |
| 4 | 窓際に追い込まれているうちは二流 | 仮面を固定したまま腕組みした肩がわずかに上下 | [PNG](stickers/04_niryu/master.png) / [GIF](stickers/04_niryu/preview.gif) / [APNG](stickers/04_niryu/sticker.png) |
| 5 | 一流の窓際族は窓際を作り出す | ドリルと手元が小刻みに振動 | [PNG](stickers/05_ichiryu/master.png) / [GIF](stickers/05_ichiryu/preview.gif) / [APNG](stickers/05_ichiryu/sticker.png) |
| 6 | 二日酔い | 横たわった胸が小さく呼吸し、頭上の線が揺れる | [PNG](stickers/06_futsukayoi/master.png) / [GIF](stickers/06_futsukayoi/preview.gif) / [APNG](stickers/06_futsukayoi/sticker.png) |
| 7 | 飲みに行こう | 手招きし、投げた書類がひらひら動く | [PNG](stickers/07_nomini/master.png) / [GIF](stickers/07_nomini/preview.gif) / [APNG](stickers/07_nomini/sticker.png) |
| 8 | 禁酒中 | 点滴の滴とビールの泡が動き、ゆっくり呼吸 | [PNG](stickers/08_kinshu/master.png) / [GIF](stickers/08_kinshu/preview.gif) / [APNG](stickers/08_kinshu/sticker.png) |

## 納品・編集用ファイル

- `stickers/<ID>/master.png`：1200×1200pxの透過静止マスター。
- `stickers/<ID>/still.png`：400×400pxの透過確認用静止画。
- `stickers/<ID>/sticker.png`：320×270pxの透過APNG。3秒、再生回数1、23〜24フレーム、1MB未満。
- `stickers/<ID>/preview.gif`：400×400px、白背景、3秒ループ。
- `all-members-{white,black}-preview.gif`：納品APNGを時間に合わせてデコードし、4列×2行へ合成。1280×540px、3秒ループ。
- `static/images/01.png`〜`08.png`：370×320pxの透過静止画像。メイン・タブ画像は未作成。
- `source/<ID>/art-generated.png`：顔を修正した生成原画。`art.png`：輪郭の透過処理後。`caption.png`：独立した透過文字レイヤー。
- `source/motion.json`：部分変形の範囲・強度・速度、効果の位置。再生成時の正本は `tools/build.py` の `MOTIONS`。
- `source/references/`：正典キャラクターシートと第一弾絵柄参照。セット内に同梱。
- `source/redraw-manifest.json`、`face-correction.json`、各`prompt*.txt`：内蔵image_genの生成・顔修正プロンプト。API/CLIでの画像生成は不使用。
- `reports/validation.json`：最終出力の検証結果。
- `release.zip`：PNG・APNG・GIF・編集元・再生成ツールを含む共有用ZIP。LINE申請用ZIPではない。

構図の正本：おはようは会社でビール片手に挨拶し、通常の口の横に✨。冷えてるは第63話の真冬の高層ビル外ベランダ席。一流は既存オフィスの中央で独立した窓枠だけを設置。飲みに行こうはジャケットなしで書類を投げ捨てる。禁酒中は病院のベッドでビールジョッキから点滴がつながる。

## 透過とアニメーション

文字はヒラギノ角ゴシックW9を高解像度RGBAへ直接描画するため、字の穴・文字間・行間は完全透過。約2px/400pxの白フチを付け、全フレームで固定する。

原画は元のアルファを保持し、孤立した微小断片を除去。半透明境界の白・青い色混入を近傍の不透明色で補正し、輪郭へ細い白フチを付ける。仮面・白Tシャツ・泡・雪は不透明のまま保護する。白と黒の確認GIFは最終APNGから作成し、GIF自体には背景を付ける。

動作は生成原画への局所変形、ジャンプの移動・拡縮、輝き・雪・点滴のレイヤーで作る控えめなループ。連続ポーズを画像生成した方式ではない。文字を動かさず、顔の表情や仮面の口を変形させない。画像補間はプリマルチプライドアルファで行い、透明縁の黒ずみを防ぐ。

## 再生成

Python 3、macOSのヒラギノ角ゴシックW9、FFmpegを使用。

```sh
python3 -m venv 27_LINE_STICKERS/sets/02/.venv
27_LINE_STICKERS/sets/02/.venv/bin/pip install -r 27_LINE_STICKERS/sets/02/tools/requirements.txt
27_LINE_STICKERS/sets/02/.venv/bin/python 27_LINE_STICKERS/sets/02/tools/build.py
27_LINE_STICKERS/sets/02/.venv/bin/python 27_LINE_STICKERS/sets/02/tools/verify.py
```

画像生成を再実行せずに原画から全出力を作れる。`build/`、`.venv/`、比較候補`drafts/`、`release.zip`はローカル保持・Git対象外。
