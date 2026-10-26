# 純正H3 + 同僚のTurbo 8step構成の比較

2026-10-27ユーザー依頼。既存30秒の通販動画と同じ入力・seed・1344×768・362フレーム×2章。純正20stepの既存結果と比較する。音声は既採用Irodoriマスター、別途H3生音声版も残す。品質の採否はユーザーが判断する。

参照: https://github.com/sobaya-0141/Seedance_Madogiwa/blob/main/.claude/skills/colab-video/h3_colab.ipynb （2026-10-27取得）。モデル・LoRAのrevisionとSHAはrecipe.json。

純正Ref2VA INT8 + LightX2V Ref2V Turbo 8step v1.0 768p LoRA。strength 1.0。UNET→SigmaShift(video=12/audio=3)→LoRAの結線、euler/beta/8stepは同僚コードと同じ。起動済みComfyUIのobject_infoで入力名を検証する。schema_helpers.pyは同僚ノートブックのスキーマ検証ヘルパを使用。

A100、SageAttentionなし、fast flagsなし。長尺の並列VAEデコード失敗記録に合わせworkers=1を使用（同僚の自動設定はA100で2）。ComfyUIは前回比較と同じ固定revision。入力制作工程は再実行せず、採用画像・音声を再利用する。これは同僚の高速化レシピの検証であり、同僚の全制作環境の複製ではない。

.local/h3-turbo8-20261027/launch-detached.pyが公式Colab CLIから独立プロセスを起動し、monitor.pyが1分ごとに状態取得。結果回収・ハッシュ検証・GPU停止後、finish.pyで30秒版と純正との左右比較を出力する。品質リトライなし。セットアップ・LoRA取得・各章の時間とCU残高を別記録する。

初回セットアップ中にバンドルの起動ファイル名の誤りを検出し、停止・修正した。次のセッションではCLI接続が切れ、実行先フォルダ未作成・生成未開始を確認してから独立プロセス方式に変更した。初期残高125.71 CUからの差分にはこの準備時の消費も含める。
