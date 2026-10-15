# 制作方式と履歴の参照先

全パスはリポジトリルート基準。記録は2026-10-15時点。採用状態は対象セットの最新README・set.json・コードを優先する。

## 第一弾で実際に使った方法

| 対象 | 証拠 | 実際の扱い |
|---|---|---|
| そば屋 | `27_LINE_STICKERS/sets/01/source/sobaya/prompt.txt` | 4列×3行、12ポーズを1枚へ生成する依頼。頭・ジョッキを保ち、前腕と手でなでる |
| 採用原画 | 同 `source/sobaya/poses/00.png`〜`03.png` | 現存する採用原画は4枚。生成依頼枚数と採用枚数を区別する |
| 再生処理 | 同 `tools/build.mjs` | `0,1,2,3,2,1,0,1,2,3,2,1` を各90ms、最後に開始姿勢を1920ms保持。計13フレーム・3秒 |
| よーたん | 同 `source/yotan/keyframes.png`・`prompt.txt`、`tools/motion.mjs` | 3列×2行の6原画を切り出して使用 |
| ほかの方式 | 同 `tools/build.mjs`・`motion.mjs` | たこさん・とーくん・福ギュン・やめ太郎は4原画＋FFmpeg `minterpolate`。おかやまんは全体の拡大、ゆめみんは本体＋木槌の剛体回転 |

「第一弾全員が同じ方式」「第一弾は一切補間なし」「そば屋の12原画がそのまま採用された」は誤り。継承する核は**参照絵から連続した姿勢を描かせ、選んだ原画を切り出して組み立てること**。過去コードの補間設定まで自動的に継承しない。

透過の根拠は同 `tools/matte.py` と `README.md` の「透過処理」。文字内の閉じた白、白い服・仮面・泡、白背景が混ざった半透明輪郭を別々に扱う。`tools/build-static.mjs` は処理済みRGBAを再マット処理しない。`reports/caption-cleanup.json` は文字下の断片除去記録。

第一弾は開始姿勢へ戻る設計で、`tools/verify.mjs` も先頭・末尾の一致を検査する。この検査を異なる芝居へ無条件にコピーしない。

## 第二弾での失敗と現在の正本

`27_LINE_STICKERS/sets/02/ANIMATION_REWORK.md` に再制作の理由が残る。単一静止画へ局所変位場を与える `cv2.remap` は形式検査を通っても、不自然な関節・輪郭・身体の伸縮になった。現行の第二弾は身体ワープ・光学補間を使わず、描かれた姿勢を採用する。

| 用途 | 参照先（`27_LINE_STICKERS/sets/02/` 内） |
|---|---|
| 採用状態・仕様 | `README.md`、`set.json` |
| 実際の生成指示・参照 | `source/animation-manifest.json`、`source/animation/<ID>/prompt*.txt`・`reference*.png` |
| 採用連続原画 | `source/animation/<ID>/keyframes.png` |
| 追加の中間姿勢 | `source/animation/05_ichiryu/finish-keyframes.png` |
| 整列後の原画・記録 | 各IDの `poses/`、`registration.json` |
| 採用順・保持時間 | `tools/build.py`、`reports/render.json`。`source/motion.json` も更新する |
| main/tab | `tools/build-listing.py`、`reports/listing-source.json` |
| 検査・納品ZIP | `tools/verify.py`、`tools/review-package.py`、`reports/validation.json` |

以下は本番入力と混ぜない。

- `reserve/rejected-warp/`：不採用の身体変形スクリプト。
- `reserve/02_kanpai/`：今後用に退避した乾杯の原画。旧動く版は不採用方式。
- `source/<ID>/art-generated.png`：以前の静止画再描画の履歴。現在の動く版は `source/animation/` を確認。
- `drafts/`：比較候補・試作。腕固定3案などは採用されていない。
- `ANIMATION_REWORK.md` 後半：着手時点の記録。「差し替え待ち」等を最新状態として扱わない。

## 判断に残す実例

- 「働いてるか？」：頭だけ寄る／腕を固定して胸だけ動く試作は意図と合わなかった。「馴れ馴れしい先輩」という雰囲気を、肩・胸・頭がつながる小さな傾きと返事待ちの間へ翻訳。6原画から動きの大きい1枚を外し、5原画を採用。
- 「一流」：不足した中間姿勢は追加原画で解消。伸縮で埋めない。
- 「飲みに行こう」：投げた紙が最後に束へ戻る生成ミスを修正。物の状態が時間順に続くことを確認する。
- 「冷えてる。待遇も。」：飛び出した窓柱を遠近に沿う直線で切り、人物と白い息のマスクを分けて狭めた。上端周辺は全原画で同一画素。`tools/build.py` の `trim_window_top()` と `reports/window-trim.json`。
- 「二日酔い」：背景固定で古い手足や小道具が残る試作を不採用にした。固定合成を目的化しない。現在は原画を保ち、頭を抱える間を長くしている。椅子・床の小さな原画差は `reports/final-art-review.json` に明記。

第二弾は最後のジェスチャーを保持する1回再生。確認GIFが再ループするときの先頭への切り替わりと、APNG内の不自然な継ぎ目は別問題として扱う。
