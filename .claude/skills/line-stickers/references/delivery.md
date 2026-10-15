# 規格と納品

## 公式規格の確認先

2026-10-15に確認した下記ガイドを基準にする。新しい申請用一式、規格調査の依頼、古い記録からの再開では現行ページを再確認し日付を記録する。同じ作業内の単純な再書き出しごとに調べ直す必要はない。

- 動く版：<https://creator.line.me/ja/guideline/animationsticker/>
- 時間・先頭コマ：<https://creator.line.me/ja/guideline/animationsticker/detail/>
- 静止版：<https://creator.line.me/ja/guideline/sticker/>

| 画像 | 動く版 | 静止版 |
|---|---|---|
| main（1枚） | 240×240px、APNG、拡張子 `.png` | 240×240px、PNG |
| 本体 | 8/16/24枚、最大320×270pxのAPNG。幅または高さが270px以上 | 8/16/24/32/40枚、最大370×320pxのPNG |
| tab（1枚） | 96×74px、静止PNG | 96×74px、静止PNG |

RGB系・背景透過・各画像1MB以下、ZIPは60MB以下。動く版は5〜20フレーム、再生時間は1/2/3/4秒、1〜4回再生で合計4秒以内。mainも5コマ・3秒・1回等を満たすAPNGにする。**mainへ本体の270px以上条件を適用しない**。

先頭コマはショップ等で静止表示される。tabの再生記号はLINE側が追加するので描かない。静止版は偶数寸法・72dpi以上が公式指定、外周約10pxは制作上の目安。動く版へ余白10pxを一律の必須条件として持ち込まない。

第一弾 `static/images/main.png` は静止用で、動く版mainの作成済み証拠にはならない。

ローカルにmain/tabや提出用ZIPがないことから、未申請・未販売と推定しない。第一弾の動く版はそば屋さんが申請し、[LINE STOREで販売中](https://store.line.me/stickershop/product/37292753/ja)（2026-10-15ユーザー共有・販売ページ確認）。提出版main/tabはリポジトリに未収録。制作素材の収録状況、申請担当、販売URL・確認日をセットのREADMEと台帳に分けて記録する。

## main/tabの制作

mainは顔や代表ポーズが読める構図を選ぶ。tabは小さいので文字・背景を減らし、顔と特徴的な小道具を見せる。既存原画の共通crop・等比縮小で足りれば新規生成しない。新しく描く場合は画像生成で同一性を保つ。

第二弾 `tools/build-listing.py` は「働いてるか？」の5原画を共通範囲で240pxへ縮小し、tabを先頭原画の顔＋ジョッキから切り出す例。新セットへこのキャラや座標を自動適用しない。

## ファイルと検証

本プロジェクトの画像ZIPの慣例は、直下に `main.png`、`tab.png`、`01.png`〜を置く形。上記公式公開ページでファイル名規則の明記は確認できていないため、命名慣例と公式寸法要件を区別する。フォルダ・確認GIF・資料・OS管理ファイルは画像ZIPへ入れない。

- `line-submission.zip`：main/tabと規定数の本体だけ。画像アップロード用。
- `animated-stickers.zip`：第二弾では本体8枚だけ。単体を申請画像一式と案内しない。
- `release.zip`：原画・スクリプト・確認GIF・README・報告を含む制作資料。LINEへ上げるZIPではない。

実ファイルの寸法・形式・透過・容量、APNGの実フレーム数・各フレーム寸法・総時間・再生回数・デコード、ZIPのファイル数・ルート配置・CRCを確認する。APNG合成・量子化後の絵も見る。黒白プレビューは最終APNGから作る。

第二弾の再書き出しはリポジトリルートで実行する。

```sh
27_LINE_STICKERS/sets/02/.venv/bin/python 27_LINE_STICKERS/sets/02/tools/build.py
27_LINE_STICKERS/sets/02/.venv/bin/python 27_LINE_STICKERS/sets/02/tools/build-listing.py
27_LINE_STICKERS/sets/02/.venv/bin/python 27_LINE_STICKERS/sets/02/tools/verify.py
27_LINE_STICKERS/sets/02/.venv/bin/python 27_LINE_STICKERS/sets/02/tools/review-package.py
```

`.venv` がなければ同セットの `tools/requirements.txt` から構築する。macOSのヒラギノを使うため別環境ではフォントを確認。main/tabだけの修正なら先頭の全8枚buildを省ける。他セットへハードコードされたコマ数・座標・ID・検査条件を無確認で移植しない。

「本体はそのまま」と指定されたmain/tab限定作業では、本体APNGの作業前後のハッシュとZIP内画像の一致を確認する。変更範囲が守られたことをファイル単位で確かめる。

制作完了時はREADME・set.jsonと報告を更新し、画像ZIP、必要なら個別main/tab、白黒プレビューへリンクする。規格適合・ローカル検証と、LINEのアップロード受付・審査通過を混同しない。
