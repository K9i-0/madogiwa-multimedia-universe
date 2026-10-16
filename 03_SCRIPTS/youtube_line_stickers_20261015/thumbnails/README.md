# サムネ候補 v1

2026-10-16。ユーザー採用タイトル：**Codexで動くLINEスタンプを作ってみた！失敗から学んだ制作のコツ**。

実際の第一弾スタンプの透過PNGに、内蔵 `image_gen` で作った文字・背景を合成した3案。動画v6はユーザー承認済み。サムネは選定中で、公開やアップロードは未実施。

| 案 | 狙い | 画像 | Imagegen入力 |
|---|---|---|---|
| A | 制作テーマを大きく見せる、緑と白 | [PNG](../remotion/out/thumbnails_v1/thumbnail_a.png) / [JPEG](../remotion/out/thumbnails_v1/thumbnail_a.jpg) | [プロンプト](prompts/a_v1.txt) |
| B | 失敗から学ぶコツ、紺と黄色 | [PNG](../remotion/out/thumbnails_v1/thumbnail_b.png) / [JPEG](../remotion/out/thumbnails_v1/thumbnail_b.jpg) | [プロンプト](prompts/b_v1.txt) |
| C | 完成スタンプを並べて紹介、青と黄色 | [PNG](../remotion/out/thumbnails_v1/thumbnail_c.png) / [JPEG](../remotion/out/thumbnails_v1/thumbnail_c.jpg) | [プロンプト](prompts/c_v1.txt) |

[3案比較](../remotion/out/thumbnails_v1/comparison.jpg)。各候補は1280×720。比較画像のA/B/Cラベルは候補画像の外に置いている。

目視確認：1280×720と320×180で誤字、文字の欠け、重なり、キャラクターの同一性を確認。原本3枚のSHA256一致と全レイヤーが画面内に収まることも確認。Aは題材と制作のコツが縮小時にも読めるため推奨。最終採用はユーザー選定待ち。

## 素材と処理

- 実スタンプは `27_LINE_STICKERS/sets/01/stickers/{sobaya,yametaro,yotan}/still.png`。各400×400の完成透過PNG。
- Imagegenは文字・背景・装飾のみを新規生成。内蔵ツールを3回使用。API/CLIによる追加生成は使っていない。
- 生成元は `/Users/kotahayashi/.codex/generated_images/01a13ae8-4f13-79e3-a6e1-550b7a0af48d/`。A=`exec-76101f17-fac5-4139-91fb-a0c2e913ae76.png`、B=`exec-a23b7e2f-61f6-40af-a3f8-fc761136c97a.png`、C=`exec-b92f02ea-3118-4137-b270-34c4c29d167d.png`。
- 生成した背景はプロジェクト内 `remotion/out/thumbnails_v1/plate_{a,b,c}.png` に複製済み。
- 合成はImageMagick。完成スタンプPNGをLanczosで縮小・配置。キャラクターやスタンプ内の文字は元画像のもの。原本への書き込みなし。
- 配置、素材SHA256、生成背景と出力のSHA256は [candidates_v1.json](candidates_v1.json)。

## 再合成

リポジトリ直下から `node 03_SCRIPTS/youtube_line_stickers_20261015/thumbnails/compose.mjs`。

ローカルに3枚の生成背景が必要。候補と中間画像はGit追跡せず、プロンプト・合成コード・出典記録を追跡。採用後に必要な入力画像と完成画像を正式に配置する。
