# 第1弾：全8名のスタンプ

全8点の絵柄・動作を採用済み。動く版と[静止スタンプ版](static/README.md)を収録。LINE未申請。

静止版は申請用PNG8点とメイン画像・タブ画像を作成済み。動く版のメイン画像・タブ画像は未作成。

[全員の確認用GIF](all-members-preview.gif) / [全員の静止画](all-members-still.png) / [セット情報](set.json)

配置は上段がそば屋・たこさん・とーくん・よーたん、下段が福ギュン・やめ太郎・おかやまん・ゆめみん。

| メンバー | セリフ | 採用動作 | 完成ファイル |
|---|---|---|---|
| そば屋 | 酒は友達 | 頭を固定し、手でジョッキを2往復なでて休止 | [GIF](stickers/sobaya/preview.gif) / [APNG](stickers/sobaya/sticker.png) |
| たこさん | 興味深い | 触手は固定し、頭を少し傾ける | [GIF](stickers/takosan/preview.gif) / [APNG](stickers/takosan/sticker.png) |
| とーくん | トークン切れ | 悲しい表情で肩を落とし、涙が動く | [GIF](stickers/tokun/preview.gif) / [APNG](stickers/tokun/sticker.png) |
| よーたん | お前島流し！ | ギターを持ち、左手を右上へ伸ばして指す | [GIF](stickers/yotan/preview.gif) / [APNG](stickers/yotan/sticker.png) |
| 福ギュン | ギュンにチュア | 両こぶしを頬に寄せるギュンポーズ | [GIF](stickers/fukuchan/preview.gif) / [APNG](stickers/fukuchan/sticker.png) |
| やめ太郎 | ごめんやで | 小さくお辞儀する | [GIF](stickers/yametaro/preview.gif) / [APNG](stickers/yametaro/sticker.png) |
| おかやまん | 大変驚いております！ | 手なし。真顔に近い控えめな笑顔のまま全体がアップになる | [GIF](stickers/okayaman/preview.gif) / [APNG](stickers/okayaman/sticker.png) |
| ゆめみん | 起きろ！ | 手なし。短い鼻先で木槌の柄の端を持ち、本体ごと振りかぶって叩く | [GIF](stickers/yumemin/preview.gif) / [APNG](stickers/yumemin/sticker.png) |

## 書き出し仕様

透過APNGは320×270px、1サイクル3秒、再生回数1。そば屋は13フレーム、ほか7名は20フレームで、動作後に休止する。各APNGは1MB未満。個別GIFは400×400px、全員GIFは1280×640pxでループする。文字・汗・集中線を含めた採用版を収録している。

## 素材と再生成

`source/<メンバーID>/` に採用した文字画像、動作原画、装飾、参照画像、生成プロンプトを保存している。おかやまん・ゆめみんは採用静止画から動きを作り、そば屋は4ポーズ、ほか5名は採用キーフレームから書き出す。新たな画像生成API呼び出しや旧候補フォルダは不要。

必要環境：Node.js 22、ImageMagick 7（`magick`）、FFmpeg / ffprobe、Python 3（OpenCV・NumPy・SciPy）。npm依存なし。リポジトリ直下で実行する。

```sh
python3 -m venv 27_LINE_STICKERS/sets/01/.venv
27_LINE_STICKERS/sets/01/.venv/bin/pip install -r 27_LINE_STICKERS/sets/01/tools/requirements.txt
export STICKER_PYTHON="$PWD/27_LINE_STICKERS/sets/01/.venv/bin/python"
node 27_LINE_STICKERS/sets/01/tools/build.mjs
node 27_LINE_STICKERS/sets/01/tools/verify.mjs
node 27_LINE_STICKERS/sets/01/tools/build-static.mjs
node 27_LINE_STICKERS/sets/01/tools/preview-black.mjs
node 27_LINE_STICKERS/sets/01/tools/package.mjs
```

検証では全8点のデコード、APNGの寸法・容量・フレーム数・時間・再生回数、ループ端の一致、文字の固定、全員GIFの寸法・時間を確認する。結果は `reports/` に保存する。

`release.zip` は完成画像・GIF・APNG・README・セット情報・検証結果をまとめた共有用ZIPで、LINE申請用ZIPではない。`build/` と `release.zip` は再作成可能なためGit管理しない。

## 透過処理（2026-10-14修正）

文字は白地から黒インクの被覆率を求め、文字内の閉じた白も透過する。人物はOpenCVの外形マスクで白い服・仮面・泡を保護し、輪郭の白背景混入を補正する。全160作業フレームへ同じ処理を適用。APNGはRGBAで書き出し、半透明の輪郭を保持する。容量抑制のためRGBのみ約6bitへ丸め、アルファは8bitを維持する。

[黒背景の全員GIF](all-members-black-preview.gif)は納品APNGをデコードして合成したもの。[静止版の黒背景一覧](static/preview-black.png)も用意。文字と独立した黒い集中線には約2px（400px原画上）の滑らかな白フチを追加し、暗い背景でも読みやすくする。

文字下の残留断片4か所（そば屋・とーくん・やめ太郎・おかやまん）も原画から除去済み。修正範囲は `reports/caption-cleanup.json` に記録。

[白背景の全員GIF](all-members-white-preview.gif)も納品APNGから作成。黒背景版と同じ配置・寸法・タイミングで比較できる。
