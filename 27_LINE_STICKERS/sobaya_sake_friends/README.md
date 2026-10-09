# 酒は友達

2026-10-09ユーザー採用: **首振りなし・中央案（小さく2往復）**。

- `sticker.png`: 透過APNG、320×270、13コマ、1回3秒。LINE用の個別スタンプ。
- `preview.gif`: Slack共有用、水色背景、3秒周期の無限ループ。
- 動作: 手で小さく2往復（90ms×12コマ＝1.08秒）、その後1.92秒静止。頭は全コマ固定。
- 絵柄: 白い仮面とグレー肌のそば屋が、取っ手付きの透明なビールジョッキを抱く。「酒は友達」は固定表示。
- `adoption.json`: 採用日、仕様、採用時の検証記録。

## 再書き出し

Node.js、ImageMagick、FFmpegが必要。

```sh
node 27_LINE_STICKERS/sobaya_sake_friends/build.mjs
```

既定ではGit対象外の `build/` に出力し、採用済みファイルを上書きしない。別の出力先は `--out /absolute/path` で指定できる。

`inputs/00.png`〜`03.png` は採用された4ポーズ。全コマの頭領域を同一画素で固定し、文字も合成済み。再生順は `0,1,2,3,2,1,0,1,2,3,2,1,0`。最後のコマを1.92秒保持する。APNGは全コマ共通の256色パレットを使用する。

## 画像生成の記録

元のユーザー添付は `inputs/original-reference.png`。built-in image_genで缶をジョッキに直した参照画像が `inputs/mug-reference.png`。対応する実送信プロンプトは `prompts/prompt-mug.txt` と `prompts/prompt-hand.txt`。採用した4ポーズのみを再書き出し入力として保存し、他のポーズ・不採用候補・比較GIF・作業中間物は整理済み。

この個別スタンプはLINE未申請。販売セット・メイン画像・タブ画像は別途必要。
