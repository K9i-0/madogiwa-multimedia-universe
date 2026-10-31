# Colab × MiniMax H3：動画資料 v2

制作日・調査日：2026-10-31。ユーザー確認用v3。公開・YouTube登録は未実施。
実行指示書：[workflow.md](workflow.md)。発話正本：[remotion/dialogue.txt](remotion/dialogue.txt)。
公開後に制作ページ・YouTube・実行指示書の絶対URLへ更新する。

## 今回の内容

対象は、AIツールを使ったことはあるが、動画モデルの自力実行・Colab・Hugging Face・GPUは初めての人。前回のWan解説を見ていなくてもよい。

1. H3で、どんな動画が作れる？ — 作例、Seedance 2.5・Wan 3.0・H3の使用感、Klingの未使用注記。
2. 高いPCがなくても動かせる？ — 公開重み、Hugging Face、GPU、Colabの役割。
3. 窓際族は、どう作っている？ — そば屋が開拓した方法、実行の流れ、480pとTurbo LoRA。
4. 結局、いくらかかる？ — Google AIのCU枠、30秒の費用、Dreamina年契約の条件。
5. 使う前に知っておきたいこと — GPU可用性、解像度、地域条件。fal.aiは未使用の余談。

各章に2秒のタイトルと問い・導入を付ける。詳細なCLI・生成パラメーターは下の設定と実行指示書に記載。

配役と見た目はユーザー指定のFlutter解説・プロジェクト紹介を参照。ずんだもんが左、めたんが右。単純な背景、中央の図表・資料映像、下部字幕。旧Wan解説のExcel外枠は適用しない。

## 料金の前提

生成する映像30秒分。2026-10-31確認、ドルは1ドル160円で換算。解像度と支払方式が異なる。参考動画入力などの追加課金と、やり直しは除外。完成品30秒を必ずこの金額で作れるという意味ではない。

| 経路 | 30秒相当 | 条件 |
|---|---:|---|
| H3 + Colab | 約17円 | 480p Turbo、A100、1.48 CUの測定例。100 CU＝1,179円換算 |
| Wan 3.0 / Qwen Cloud | 168円（通常240円） | 480p、調査時30%割引 |
| Wan 3.0 / Qwen Cloud | 336円（通常480円） | 720p、調査時30%割引 |
| Seedance 2.5 / Dreamina | 約1,360円 | 720p、1,440クレジット、Basic月契約の更新料金 |
| 同・年契約の例 | 約620円 | Advanced月28,137クレジット、初年度145,043円、通常消費。月枠は30秒×19本分 |
| 同・年契約＋期間限定特典 | 約370円 | 同年契約＋消費約40%減。月枠換算約32本。2026-10-27〜11-06の特典レート |

Dreaminaはクレジットを全量使った場合の配賦額。契約料が実際の支払いで、動画ごとの従量請求額ではない。初年度年契約と短期の消費割引は別であり、特典レートが一年間固定されるわけではない。例の翌年更新は290,086円。枠超過の追加クレジットは購入時の別価格。60本の無料5秒動画特典は上の30秒換算へ含めていない。

細かい値、計算式、観測経路は [research/pricing.json](research/pricing.json)。

## 実例と設定

- そば屋が整備したlocal-video / colab-videoを参考に、MMU側はGoogle公式Colab CLIへ適応。そば屋をH3本体やTurbo LoRAの開発者と紹介しない。
- R2V、864×480、24fps、A100 1worker、LightX2V Ref2V Turbo v1.0、8step、euler/beta、video/audio shift 12/3。
- 採用LoRAは768p表記のファイル。480p専用のLoRAがあるという説明ではない。
- 通販題材30秒の生成512.91秒、準備等込み906.41秒、観測1.48 CU。残高反映の遅れやセッション差がある。
- 参照コント：窓際BBQ v3。参照ニュース：ビール盗難、重複読みを編集した11.5秒版。
- 元生成480p、完成編集720p。拡大しても生成時の解像度が上がるわけではない。

## 品質について

Seedance 2.5の最高の表現力、Wan 3.0の品質・費用のバランス、H3のコントでの使いやすさはユーザーの制作体験に基づく感想。同一入力の客観ベンチマークではない。Kling 4.0は未使用で比較対象外。ワイプ用途とfal.aiは未使用の提案・紹介として区別する。

## 出典

- [Google Colab FAQ](https://research.google.com/colaboratory/faq.html)：Python実行、CU、動的な利用上限、GPUの非保証。
- [Google AIプラン比較](https://one.google.com/intl/ja_jp/about/google-ai-plans/)：Plus 50 / Pro 200 / Ultra 5x 1000 / Ultra 20x 2000 CU/月。無料体験・ストレージ契約と区別。
- [Colab購入画面](https://colab.research.google.com/signup)：日本の100 CU 1,179円。
- [Qwen Cloud Wan 3.0](https://www.qwencloud.com/models/wan3.0-video)、[課金方式](https://docs.qwencloud.com/developer-guides/getting-started/model-prices)。
- [Dreamina料金](https://dreamina.capcut.com/pricing/dreamina-price)：日本のライブ画面と公式キャンペーン注記を参照。国別クレジット数を混ぜない。
- [Hugging Face Hub](https://huggingface.co/docs/hub/index)：モデル・データセット・デモのプラットフォーム。
- [MiniMax H3モデルカード](https://huggingface.co/MiniMaxAI/MiniMax-H3)：公開H3-Baseとホスト版の違い。
- [MiniMax動画API](https://platform.minimax.io/docs/api-reference/video-generation-v2-create)：768P / 2K等。
- [H3ライセンス](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)：米国・EU・英国・韓国を除くTerritoryの定義等。無料版の単純な機能差とは区別。
- [Turboモデル](https://huggingface.co/lightx2v/Minimax-h3-Turbo)：利用したファイルは制作プロファイルの固定revisionを正本とする。
- [そば屋の制作リポジトリ](https://github.com/sobaya-0141/Seedance_Madogiwa)。
- [Kuaishou公式Kling 4.0発表](https://ir.kuaishou.com/news-releases/news-release-details/kling-ai-officially-launches-next-generation-kling-40-raising/)：2026-10-15公開。
- [fal H3 Max](https://fal.ai/learn/devs/introducing-h3-max-by-fal)：5秒768pを2.78秒とする提供元紹介値。MMUによる実測ではない。

## 音声・音楽クレジット

VOICEVOX:ずんだもん／VOICEVOX:四国めたん。立ち絵：坂本アヒル。
ロゴ表示：LobeHub Icons（@lobehub/icons-static-svg、MIT）。各ロゴは各社の商標で、紹介・識別目的で表示。WanはAlibabaのモデル、料金はQwen Cloud、SeedanceはByteDance、DreaminaはCapCutの表示。
昼下がり気分／KK：https://opentracks.com/bgm/detail/4695
ほのぼのワルツ【リコーダー】／エクシエ：https://commons.nicovideo.jp/works/nc116360
Music: TheFatRat - Unity
Watch the official music video: https://www.youtube.com/watch?v=n8X9_MgEdCg
利用条件確認：https://www.thefatrat.com/terms-and-conditions
資料映像に焼き込まれた字幕・音楽は既存作品の完成版に由来する。

挿入BBQの音楽："Corncob" Kevin MacLeod (incompetech.com)。CC BY 4.0：https://creativecommons.org/licenses/by/4.0/ 。出典：https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100565 。本解説では抜粋と音量調整を実施。
