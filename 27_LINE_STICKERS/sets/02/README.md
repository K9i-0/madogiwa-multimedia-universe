# 第2弾：そば屋オンリー8個

2026-10-15完成版。第一弾と同じく、imagegenで生成した連続ポーズシートを切り出してアニメーション化。各姿勢は描かれた原画で、身体の局所変形・モーフィング・オプティカルフロー補間は使用していない。LINE未申請。

[白背景の8点GIF](all-members-white-preview.gif) / [黒背景の8点GIF](all-members-black-preview.gif)

[白背景静止一覧](all-members-white-still.png) / [黒背景静止一覧](all-members-black-still.png) / [動作コマ一覧](reports/motion-review.png)

| # | セリフ | 動き | 個別プレビュー |
|---|---|---|---|
| 1 | おはよう | 下ろした手を挨拶の位置まで上げ、口元の✨が光る | [GIF](stickers/01_ohayo/preview.gif) |
| 2 | ちゃんと働いてるか？ | B案。寄りを抑え、空いた腕をパーティションに置いて馴れ馴れしくもたれる | [GIF](stickers/02_hataraiteruka/preview.gif) |
| 3 | 冷えてる。待遇も。 | 真冬のベランダ席で肩をすくめ、白い息を吐く。雪が降る | [GIF](stickers/03_hieteru/preview.gif) |
| 4 | 窓際に追い込まれているうちは二流 | アーロンチュアに座り、頭は固定してこちらへ指差す。頭の回転なし | [GIF](stickers/04_niryu/preview.gif) |
| 5 | 一流の窓際族は窓際を作り出す | オフィス中央の窓をドリルで締め、ドリルを引いて窓を見る | [GIF](stickers/05_ichiryu/preview.gif) |
| 6 | 二日酔い | 両手で頭を抱え、脚を引き寄せて横向きに丸くなる | [GIF](stickers/06_futsukayoi/preview.gif) |
| 7 | 飲みに行こう | 書類を投げ、手招きして帰る方向へ体を向ける。ジャケットなし | [GIF](stickers/07_nomini/preview.gif) |
| 8 | 禁酒中 | ビールの点滴をつないだまま、空いた手を上げてサムズアップ | [GIF](stickers/08_kinshu/preview.gif) |

## 完成ファイル

- `stickers/<ID>/sticker.png`：透過APNG、320×270px、3秒、再生回数1、6〜12フレーム、各1MB未満。
- `stickers/<ID>/preview.gif`：400×400px、白背景、3秒ループ。
- `stickers/<ID>/master.png`：1200×1200pxの代表ポーズ静止画像。`still.png`：400×400px。`start.png` / `end.png`：開始／終了ポーズ。
- `all-members-{white,black}-preview.gif`：実際の納品APNGを時刻同期して合成した4列×2行GIF。1280×540px。
- `static/images/01.png`〜`08.png`：370×320pxの透過静止画像。
- `animated-stickers.zip`：完成APNG8点を `01.png`〜`08.png` としてまとめたもの。
- `release.zip`：完成画像・プレビュー・連続原画・加工ツール・検証結果を収録。メイン画像・タブ画像を含むLINE申請一式ではない。

## 制作方式

正本は `source/animation/<ID>/keyframes.png` と `source/animation-manifest.json`。各3列×2行の6連続ポーズ。「一流」は急な姿勢変化を避けるため `finish-keyframes.png` の中間ポーズも使用。

セルを切り出して背景の固定部分から平行移動だけで位置合わせし、動かない部分を共通原画で合成。全コマ共通の切り抜き範囲・倍率で配置する。人物を部分的に伸縮する処理はない。星と雪、椅子の名前は独立して合成する。

文字はヒラギノ角ゴシックW9から透過RGBAへ直接描画し、文字の穴も透明。白フチを付け、黒背景でも読めるようにしている。人物の白い仮面・服・泡を保ち、輪郭の色にじみと隣のセルの断片を除去。仮面の丸い目・赤い模様・丸端の横長の口を維持する。

動作の最後は長めに保持。強制的な逆再生や開始ポーズへの復帰は入れていない。GIFは確認用にループするため、休止後に次の再生の開始ポーズへ切り替わる。APNGは1回再生。

生成は内蔵image_genを使用。実際のプロンプト・参照・採用シート・整列したポーズ・位置合わせ記録を `source/animation/` に保存。旧静止画再描画の入力は `source/` に履歴として保持。

## 再生成と検証

```sh
27_LINE_STICKERS/sets/02/.venv/bin/python 27_LINE_STICKERS/sets/02/tools/build.py
27_LINE_STICKERS/sets/02/.venv/bin/python 27_LINE_STICKERS/sets/02/tools/verify.py
27_LINE_STICKERS/sets/02/.venv/bin/python 27_LINE_STICKERS/sets/02/tools/review-package.py
```

依存は `tools/requirements.txt`。フォントはmacOS標準。検証は寸法・フレーム数・3秒・1回再生・容量・透過余白・文字固定・動作差分・最終ポーズの保持・FFmpegでのデコードを確認。完成コマの目視確認は `reports/motion-review.png`、形式検証は `reports/validation.json`。

「乾杯！」は今後用に [reserve/02_kanpai](reserve/02_kanpai/README.md) へ退避。そこにある旧動く版は不採用の部分変形方式なので、再利用する場合は原画から動きを作り直す。旧変形スクリプトも `reserve/rejected-warp/` の履歴であり、本番生成には使用しない。
