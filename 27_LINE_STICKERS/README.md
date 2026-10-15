# 窓際族物語 LINEスタンプ

スタンプを販売セット単位で管理する。第1弾の8点を採用済み、第2弾のそば屋オンリー8点は採用済み構図から連続ポーズ方式で完成。

| セット | 内容・状態 | 確認用 |
|---|---|---|
| [第1弾](sets/01/README.md) | 全8名・動く版＋[静止版](sets/01/static/README.md)。LINE未申請 | [全員GIF](sets/01/all-members-preview.gif) / [静止画](sets/01/all-members-still.png) |
| [第2弾](sets/02/README.md) | そば屋オンリー8点。連続ポーズ方式で動く版・静止版を書き出し済み。LINE未申請 | [白背景GIF](sets/02/all-members-white-preview.gif) / [黒背景GIF](sets/02/all-members-black-preview.gif) |

## ファイルの見方

各セットの `stickers/<メンバーID>/` に動く版と確認用静止画、`static/images/` に静止スタンプの申請用PNGを置く。

- `preview.gif`：Slackなどで動きを確認するループGIF。
- `sticker.png`：透過APNG。拡張子はPNGだがアニメーションを含む。
- `still.png`：透過補正・白フチ適用済みのRGBA静止画。

`source/` は採用版の再生成に必要な素材・プロンプト、`tools/` は書き出し・検証ツール、`reports/` は検証結果。途中フレームの `build/` と配布用の `release.zip` はGit管理対象外。

## 第2弾以降の追加

第2弾は `sets/02/`、第3弾は `sets/03/` と追加する。各セットに `README.md` と `set.json` を置き、この一覧へ追加する。メンバーIDは共通で使い、福ギュンの内部IDは `fukuchan` を維持する。

各セットは素材とツールを含めて独立させ、別セットや旧候補フォルダに依存させない。制作中の候補は採用版と混在させず、採用確定時に不採用版・中間成果物を削除する。採用版の修正は同じセット内で更新し、履歴はGitに残す。`v1`・`v2` の候補フォルダを完成版の置き場にしない。

販売用メイン画像・タブ画像の作成、申請状況は各セットのREADMEで管理する。

第1弾の[黒背景・動作確認GIF](sets/01/all-members-black-preview.gif)／[静止版の黒背景一覧](sets/01/static/preview-black.png)。
