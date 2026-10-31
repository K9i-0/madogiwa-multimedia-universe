# BBQホラー：肉みつけた

台本はscript.md、素材一覧はpreview.html。
H3 480p Turbo、A100 1worker、4カットを同一GPUで順次生成。開始時残高100.69CU。
生成設定・参照入力はchapter_plan.jsonとprompt_ch01〜04_v1.txt、workflow JSON。

- 音声: generate_voices.py（正典Irodori参照、そば屋Large＋monsterize、ほかSmall、やめ太郎尺倍率0.70）
- 準備: prepare_generation.py（新規jobのみ、上書き拒否）
- 実行: colab_h3.py run --job generated/h3-horror-v1 --session mmu-bbq-horror-20261030-v1 --gpu A100
- 原本: generated/h3-horror-v1/results/ch01〜04_480p.mp4
- 編集: remotion/src/edit-manifest.json → finish_edit.py → remotionでnpm ci、npm run typecheck、npm run render
- BGM: music-credit.txt、前作採用Corncobを冒頭だけ使用、森以降は環境音のみ。

生成物・監査画像・音声マスター・BGM・node_modulesはGit除外。本番画像・採用セリフ・プロンプト・編集コードと記録を追跡。

## 完成版 v1

`final_remotion_bbq_horror_v1.mp4`：34.0417秒、1280×720、24fps。捕獲カットは6.5秒で切り、会場へ戻す。セリフ3行をメンバーカラー字幕にし、Corncobは冒頭のみ。生成されたやめ太郎の寄りをラストに採用（よーたんの振り返り案から変更）。

全4カットのコンタクトシートと白Tの原寸フレームを確認。指定3行は自動文字起こしと照合。聴取による発音品質の保証はしていない。マスクは外れないが口の模様が少し動く。ゆめみんの調理・食事・損傷描写なし。

Colab A100初回4カット、残高100.69→98.94 CU（1.75 CU）、停止とactive assignments 0を確認。入力と原本ハッシュはproduction-report.json。

## 完成版 v2（2026-10-31）

ユーザー指定で、ゆめみん単独浮遊のch02を全削除（v1の10.833〜17.417秒、158フレーム）。退場からそば屋登場・捕獲へ直接接続。以降の映像・音声・字幕を同じ158フレームだけ前へ移動。完成版は `final_remotion_bbq_horror_v2.mp4`、659フレーム・27.4583秒。v1動画と `remotion/src/edit-manifest-v1.json` を保持。追加生成なし。
