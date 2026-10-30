# 窓際BBQ（H3）

採用シナリオと制作条件は [script.md](script.md)。
毒ちくわは第88話のC案（強い紫、黒紫の焼き目、赤紫・黄緑の色むら）。

再現手順：

1. `python3 generate_voices.py`：正典音声から今回のセリフを生成。既存生成は上書きしない。
2. `python3 prepare_generation.py`：採用場面画像＋音声から5カットのimmutable bundleを作成。既存ジョブ上書き禁止。
3. リポジトリの `colab_h3.py run --job …/generated/h3-bbq-v1 --session mmu-bbq-h3-20261030-v1 --gpu A100`：公式CLIで実行、回収、停止。通信断は同一ジョブで再接続。
4. 必要に応じて `python3 collect_partial.py` で完了済みカットだけ先に回収。
5. `remotion/src/edit-manifest.json` に実生成の字幕タイミング・BGM停止フレームを記録。
6. `python3 finish_edit.py`、`cd remotion && npm ci && npm run typecheck && npm run render`。

480p原本は `generated/h3-bbq-v1/results/`。完成720pの最新版はエピソード直下の `final_remotion_bbq_v3.mp4`（36.833秒）。v1/v2も保持。
動画、途中画像、モデル、未採用素材、音声ミックス、BGM本体はGit除外。BGMは `music-credit.txt` の公式配布元から `remotion/public/bgm.mp3` へ取得する。


## 白Tのプロンプト比較（2026-10-30）

`shirt_tests.html` に元の生成と3案。固定した入力・seed・設定は `shirt_test_plan_v1.json`、観測結果は `shirt_prompt_experiment_report.json`。
案①の「plain, undecorated garment / uninterrupted opaque white cotton surface / broad soft lighting gradients / natural fabric folds」が良好。冒頭の比較に加え、乾杯・発覚・転倒でも点状陰影の改善を確認した。案②・③には再発したため、禁止語を消すだけで十分とは結論しない。モデル内部の原因や、他の場面・seedへの普遍性は未検証。

v2は胸元の画像修整なし。4カットを案①で再生成し、食事カットは初版の原本を維持。`prompt_prod*_cloth_v2.txt` と `cloth_production_plan_v2.json` が実入力。生成後の通常リサイズ・字幕・カット・音楽のみ。仮面の描かれた口が動く限界は残る。生成が余分に入れた発話・再度食べる動作はカットと反応アップで処理する。

比較GPUセッションは停止済み。比較3案＋追加3カットを1台のA100で実行。停止後残高100.69 CU、使用率0.00 CU/h、active assignments 0。比較前104.19 CUとの差3.50 CUは残高反映遅延を含みうる観測値で、厳密な請求額ではない。

v1の編集情報は `remotion/src/edit-manifest-v1.json` に保存し、現在の `edit-manifest.json` はv2。v1再現時はmanifestを切り替え、出力名を別途指定する。


v3はユーザー指定の乾杯・発覚の重複カットと、よーたんの「なんか臭い変じゃない？」へのIrodori差し替え。`prepare_dialogue_v3.py`でv2 manifestから再現し、`finish_edit.py`とRemotionで出力する。v2 manifestは`remotion/src/edit-manifest-v2.json`に保存。
