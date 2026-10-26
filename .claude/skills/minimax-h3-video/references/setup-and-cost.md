# 環境・契約・費用（2026-10-26確認）

## 参考にした同僚実装

https://github.com/sobaya-0141/Seedance_Madogiwa

参照commit: `1d62fc1042a7a797e9dbc0fe0dc277bb4ec54cf5`

- `.claude/skills/local-video/SKILL.md`、`build_h3_workflow.py`、`h3_run.py`
- `.claude/skills/colab-video/SKILL.md`、`h3_colab.ipynb`、`build_h3_run_package.py`

取り入れた点: Macで素材準備/CUDAで生成、GPU世代別量子化、入力順、17k+5フレーム、
重みの都度DL、結果回収、修正版の別名管理。
`build_workflow.py`は同僚版を改修。それ以外の補助スクリプトとノートブックはMMU向けに作成。
リポジトリ全体の同期、同僚の個人設定・音声環境・過去の「検証済み」判定の引継ぎは行わない。

## 現在使える契約

ユーザーはGoogle AI Plus契約済み。公式は**毎月50 Colab Compute Units**。
50時間ではなく、利用時間 = 残CU / 実際のCU毎時。
同じGoogleアカウントでColabの「設定 > 定期購入」とリソース画面を確認する。
Pro/Pro+とAIプランは併用可能で、CU残高に合算される。
まず既存の50 CUを使い、継続利用で不足した場合だけPay As You GoまたはProを比較する。
料金の円表示は購入画面を正本にし、過去の円価格を現行保証値にしない。

- https://support.google.com/googleone/answer/16882689?hl=en
- https://one.google.com/about/
- https://research.google.com/colaboratory/intl/en-GB/faq.html
- https://colab.research.google.com/signup

## ライセンスと配置地域

H3の公開重みはゲートなし（2026-10-26 HF API `gated=false`）。
MiniMaxの従量課金API契約やHFトークンはこの公開重み経路には不要。
ただし公開重みは無条件の利用許諾ではない。

2026-10-26に読んだCommunity License（本文の版日は2026-08-02）は、米国・EU・英国・韓国を
対象地域から除外し、V.4は重みだけでなく出力の使用・配布・表示にも地域条件を適用している。
日本は除外国に含まれないが、Colabの実行場所と作品の公開範囲を別々に確認する。
日本のGoogleアカウント、タイムゾーン、IP位置推測だけでGPUの配置地域を確定しない。
ノートブックはGCE metadataからzone取得を試すが、取得不能なら未確認のまま扱う。
地域条件が解決しない場合は日本等で配置を固定できるCUDA環境か、適用可能な別許諾を検討する。

年間商用売上2,000万USD超には事前の別途書面許諾、商用製品・サービスUIのモデル表示条件がある。
Comfy公式の説明では、対象地域・規模内の自前実行はCommunity Licenseによる商用利用、
Comfy Cloud生成は商用権込みとされる。別ライセンスのProfessionalは月$5,000〜。
小規模な実験にこの契約を自動提案・購入しない。YouTube等の世界向け公開を無条件に可能と断定しない。

Colab FAQにはdeepfake生成の禁止もある。初回検証は人物なしとし、実写メンバーの再現をColabへ
持ち込む際は利用条件との適合を確認する。人物同一性の品質検証とこの利用条件は別問題。

- https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE
- https://docs.comfy.org/tutorials/video/minimax/minimax-h3#commercial-licensing
- https://research.google.com/colaboratory/faq.html
- https://huggingface.co/api/models/Comfy-Org/MiniMax-H3

## 費用比較の方法

同僚の記録ではL4は約2〜3 CU/時、蒸留8stepで動画1秒あたり約1.9分。
これは同僚側の過去実測であり、今回の480p/base20step環境に適用できる保証値ではない。
仮に2〜3 CU/時なら50 CUは約16.7〜25時間。実際の値はColabリソース表示で確認。今回の画面は1.54 CU/時だったので、同じ率なら50 CUは約32.5時間。
今回の検証前に「15秒いくら」「Wanより必ず安い」と確定しない。

比較に残す値:

- GPU・生成解像度・尺・steps・LoRA・seed・実際のCU/時
- セットアップ時間（約54GBのDL・依存関係）、推論時間、待機時間
- 開始/終了CU残高、失敗と再生成回数、採用できた動画秒数
- 円/CU（購入額 / 購入CU）、追加支出と既存特典の消費を区別
- H3: (準備 + 推論 + 待機 + 再生成)の消費CU × 円/CU / 採用秒数
- Wan: 同じ480P・音声条件の公式単価 × 課金対象生成秒数 / 採用秒数

2026-10-26表示のWan 480Pは$0.035/秒（通常$0.05/秒から30%割引）、15秒で$0.525。
割引終了日は未確認。H3の追加課金がゼロでも既存CUは消費するので、追加支出と計算資源コストを分ける。
Wanの現在価格: https://www.qwencloud.com/models/wan3.0-video
H3の技術仕様: https://docs.comfy.org/tutorials/video/minimax/minimax-h3
Google公式Colab CLI: https://github.com/googlecolab/google-colab-cli

## 動作確認状況

- ローカル: arm64 Mac、ffmpeg/ffprobeあり、CUDA/ComfyUI環境なし。
- ユーザーのColab設定画面でGoogle AI Plusが有効であることを確認。
- ローカル検証: スキルvalidator、全Python/ノートブックセル構文、workflow入力検証、模擬ComfyUIでのMP4検査・ジョブ再開・二重送信防止・失敗検知が合格。模擬動画はH3生成結果ではない。
- 実生成: 未実施。ユーザーによるColab利用規約同意後、L4への接続まで成功。VRAM 22.5GB、RAM 53GB、空き193.2GiB、画面の消費率1.54 CU/時。
- 配置地域: `metadata.google.internal`と`169.254.169.254`のGCE zone照会はいずれもHTTP 404。配置地域不明のため重みDL/推論は未開始。検証用ランタイムは接続解除・削除済み。ノートブックと画面証跡は保持。
- 次の条件: 対象地域に固定したCUDA環境、またはこのColab配置に適用できる許諾の確認。単にColab Proを追加購入しても地域条件は解決しない。
- 同僚側で成功した事実は、この環境での成功を意味しない。
