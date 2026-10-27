# H3採用構成と実測（2026-10-27）

H3指定の既定は`480p-turbo`。他の選択肢は`768p-turbo`と`768p-base`。すべて純正Ref2VAを基準にする。Singularity・Hybridは比較記録だけ残し、通常の選択肢にしない。

## 固定レシピ

| profile | 横解像度 | LoRA | step | sampler / scheduler | video/audio shift |
|---|---|---|---|---|---|
| 480p-turbo | 864×480 | Ref2V Turbo 8step v1.0 768p、強度1 | 8 | euler / beta | 12 / 3 |
| 768p-turbo | 1344×768 | 同上 | 8 | euler / beta | 12 / 3 |
| 768p-base | 1344×768 | なし | 20 | res_multistep / simple | 追加ノードなし |

Turboの結線はUNET→MiniMaxH3SigmaShift→LoraLoaderModelOnly→BasicGuider/BasicScheduler。CFGはBasicGuider（追加CFGなし）。ref_image_size=matchなので480pでは内部参照画像処理も縮小される。

- 純正: `Comfy-Org/MiniMax-H3` revision `e5eb578a89295337b8ff433a035929ce0279e0b6`、A100では`minimax_h3_ref2va_pruned_int8_convrot.safetensors`。
- LoRA: `lightx2v/Minimax-h3-Turbo` revision `30f485ed874aa44c8183348ad361c5eabad318da`、`minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors`。
- LoRA SHA-256: `6a56f41ab4229c9dd845b9501bbd475ee57e112d846cf2e819d534a1ae928c5a`。約1.96GB。768p向けの同じLoRAを480pでも実測して採用。480p専用品に変更したわけではない。
- ComfyUI: `fe298e4e20f1ff26d30e8639267bbd0b57811390`。A100、1worker、SageAttentionなし、fast flagsなし。
- T2V/I2Vでは同じ版の`fl2v` LoRAを使う。対応する重みの取得・構文は用意しているが、今回の3構成比較はR2V。人物・音声品質まで他モードへ一般化しない。
- LoRAとサンプラー・shiftはセット。勝手に4stepや別バージョンへ変えない。指定があれば別実験として記録する。

## ビルドと実行

```sh
# profile省略も480p-turbo。ファイル名は入力フォルダ内のbasename。
python3 .claude/skills/minimax-h3-video/scripts/build_workflow.py \
  --mode r2v --profile 480p-turbo --frames 362 \
  --prompt-file prompt.txt --image character.png --audio dialogue.wav --out workflow.json
```

`--profile 768p-turbo` / `--profile 768p-base`に置き換えて選択する。縦はwidth/heightを反転指定。明示寸法はprofileの寸法を上書きできるため、実際のJSON寸法を記録する。Turboのstepsは8のみ。旧smokeノートブックは再現用の20stepを明示指定して保持する。

`setup_cuda.py`はLoRAをLightX2Vの固定revisionから取得・SHA検証し、Comfy-Orgの通常重みと区別する。CUDA実機のobject_infoで必要ノードの存在を確認する。CLIのprepareで設定と入力を束ね、runをA100で実行する（手順はcli.md）。GPU確保・セットアップもCUを消費する。

解像度に合った原本名`video_480p.mp4` / `video_768p.mp4`で回収。480pは720pに一度だけLanczos拡大し、768pは縮小せず`video_final.mp4`へ保持する。正確な字幕はRemotionで最終解像度に描く。モデル生成の文字や細部の品質は別途判断する。

## 計測結果

54話「等身大そば屋フィギュア通販」、同じ参照画像・Irodori WAV・プロンプト・seed、24fps・362frames×2章（仕上げは360×2=30秒）。各章は生成ジョブ全体（読込・参照処理・サンプリング・decode・回収検査）を計測。

| 構成 | 生成合計 | リモート実行（セットアップ等込み） | 観測CU残高差 |
|---|---|---|---|
| 480p Turbo | 512.91秒（8分33秒） | 906.41秒（15分6秒） | 1.48 |
| 768p Turbo | 2269.89秒（37分50秒） | 2662.07秒（44分22秒） | 5.01（準備時の復旧分を含む） |
| 768p通常 | 5301.04秒（88分21秒） | 5498.41秒（91分38秒） | 10.45 |

CU表示は更新遅延・セッションごとの料金差があり、固定料金として扱わない。セットアップ時のDL速度も変動する。既存生成結果を再利用した別セッション間比較であり、GPU個体・環境差もある。480p Turboは768p Turboに対し約4.43倍、純正768p通常に対し約10.3倍速。将来の題材の速度保証ではない。

実測記録（リポジトリルートから）:
- `03_SCRIPTS/54_yumemi_group_sobaya_figure_shopping/h3_768p/generation-result.json`
- `03_SCRIPTS/54_yumemi_group_sobaya_figure_shopping/h3_turbo8_20261027/comparison-result.json`
- `03_SCRIPTS/54_yumemi_group_sobaya_figure_shopping/h3_turbo8_480p_20261027/comparison-result.json`

ユーザー評価: 派生モデルは改善なし。768p Turboは若干気になる点があるが速さが魅力。480p Turboは品質は低いが高速で、動きの少ない動画には十分な場合がある。この判断を全動画の品質保証や自動的な高解像度再生成の根拠にしない。
