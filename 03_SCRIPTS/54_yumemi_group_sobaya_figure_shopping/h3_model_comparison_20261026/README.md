# H3 R2V checkpoint comparison — 2026-10-26

ユーザー依頼: 約30秒の同一題材で派生モデルを比較。品質の採否はユーザーが判断し、生成時間を計測する。

## 比較条件

- 題材: 54話「ゆめみグループ — 等身大そば屋フィギュア通販」。
- 純正Ref2VAは同日直前の採用生成を再利用（`h3_768p/generation-result.json`）。新しい同一セッションで純正を再生成した比較ではない。
- 追加生成: Singularity V2 pruned INT8、smhfacct Hybrid b20–49 INT8。モデルの固定revision・SHA-256は`models.json`。
- 1344×768、24fps、362フレーム×2章。比較動画は各360フレーム、合計30秒。
- A100、ComfyUI `fe298e4e20f1ff26d30e8639267bbd0b57811390`、20step、res_multistep / simple、LoRAなし。
- 入力画像・Irodori WAV・プロンプト・画像順・音声順・seed 54076801 / 54076802・ref_image_size=matchは純正と同一。
- 変更はUNETLoaderのモデルファイル名とSaveVideoの出力名だけ。モデルごとにComfyUIを再起動し、一章目の読込キャッシュ条件を揃える。二章目は同モデルのキャッシュを利用。
- これはモデル本体の比較。各モデル推奨のTurboや専用設定を含む最速構成の比較ではない。
- 追加の品質リトライや結果の選別は行わない。

## 計測

共通環境セットアップ、モデルのダウンロード、ハッシュ照合、各章の生成ジョブを別計測。生成ジョブ時間にはモデル読込・参照処理・サンプリング・VAE decode・MP4回収検査を含む。GPUの性能差・実行揺らぎはあり、同一seedでも別モデルで同じ構図になる保証はない。

純正は前半2568.40秒、後半2732.64秒、生成合計5301.04秒（88分21秒）。セットアップ等込み5498.41秒（91分38秒）、10.45 CU。

開始残高158.68 CU。新規2モデルを順番に生成し、回収・ハッシュ検証後にColabを停止。終了残高と実測は`comparison-result.json`へ記録。

## 成果物

エピソード直下へ出力する（動画はGit管理外）。

- `final_h3_compare_pure.mp4`
- `final_h3_compare_singularity_v2.mp4`
- `final_h3_compare_hybrid_b20.mp4`
- `final_h3_compare_side_by_side.mp4` — 左から純正・Singularity V2・Hybrid b20–49。全体を同じ縮小率で表示する比較プレビュー。細部は原寸の各動画で確認。
- `h3_compare_raw_<model>.mp4` — H3が生成した音声を残した版。

`final_*`の音声は全て同じ既採用Irodori・伴奏マスター。テロップ・クロップ・速度変更・AI超解像・破綻隠しは施さない。全編デコード、1344×768・24fps・720フレームを機械検証し、映像品質・演技・音声同期の優劣はユーザーに委ねる。

## 再現・進行管理

`prepare.py`は直前の入力ZIPを再利用して比較ジョブを作る。`remote.py`は固定revisionの重みを取得・SHA照合し、各モデルで同一workflowを実行する。`finish.py <results-dir>`は比較動画と計測JSONを作る。

ローカル進行管理: `.local/h3-model-comparison-20261026/controller.py`。公式Colab CLI経由で実行し、10分おきの状態取得、回収・停止、比較動画作成まで自動で行う。品質は選別しない。セッション `mmu-h3-modelcompare-20261026`。
