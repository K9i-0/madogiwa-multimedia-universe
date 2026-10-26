---
name: minimax-h3-video
description: MiniMax H3の公開重みをCUDA/Colabで動かす動画制作・環境構築・動作検証。H3、Colabでの低コスト動画、同僚のlocal-video/colab-video方式を明示されたときに使用する。Wan APIを使う通常の動画制作はwan-videoへ。
---

# MiniMax H3動画制作

Macで台本・入力を用意し、Linux NVIDIA CUDA環境でComfyUIのH3を実行する。
同僚の `local-video` / `colab-video` を参考にした独立実装。参照コミットと契約条件は
[setup-and-cost.md](references/setup-and-cost.md)を最初に読む。
**2026-10-26、Colab L4でT2Vの480p実生成・720p出力・動画構造と画の確認に成功。**
I2V/R2V、人物・声の再現性、音声内容の聴取監査は未検証。実測は参照資料へ。

## 環境と契約

- Apple Siliconだけで動くと案内しない。既存のCUDA環境があれば優先し、ColabならL4を費用優先の候補にする。
- Google AI Plusは月50 CU。50時間ではない。既存特典の残高と選択可能GPUを先に確認し、追加契約を自動購入しない。
- H3ライセンスの条件は参照資料として案内する。2026-10-26ユーザー指定: 配置地域不明を理由とする独自の保守的な停止条件は撤廃し、動作確認を優先する。配置地域は取得できる場合のみ記録し、不明ならunknownで継続する。
- モデルは約54GB。Driveは入力・結果だけ。重みは実行ディスクに直接DLし、GCSや有料Driveキャッシュを勝手に追加しない。
- Googleの公式Colab CLIも利用可能。利用するなら公式READMEと現在の認証手順を確認する。ブラウザCookie抽出・非公開APIによる認証の代用をしない。

## CLIでの実行（2026-10-26ユーザー希望の標準経路）

ブラウザでのノートブック操作より[cli.md](references/cli.md)の公式Colab CLIを優先する。
`colab_h3.py`で準備・実行・状態確認・回収・停止を行う。初回OAuth認証だけユーザー操作が必要。
2026-10-26、公式CLI経由のL4確保・H3実生成・結果回収・自動停止も確認済み。
ComfyUI APIはGPU内の127.0.0.1で使い、公開トンネルは不要。
同僚の`h3_run.py`はComfyUI API部分の参考になったが、同僚のColab運用自体はブラウザ前提。

## ノートブックでの動作検証（代替経路）

[assets/mmu_h3_smoke.ipynb](assets/mmu_h3_smoke.ipynb)をColabで開く。
自己完結したノートブックで、DriveマウントやAPIキーは不要。
最初のセルはGPUと配置地域の照会だけ。配置地域の照会結果にかかわらず、窓辺のコーヒーの湯気を1本生成する。
設定は864×480、124フレーム（約5.17秒）、24fps、20step、seed 42。
キャラクターや声の再現性の検証は、この配管テスト合格後に別に実施する。

1. 初期CU残高、CU/時、GPU、配置地域を記録。
2. セットアップと推論を分けて計測。重み・ComfyUIは固定revisionを使用。
3. `run_workflow.py`はprompt_idを出力横の`.job.json`へ保存する。同じコマンドでポーリングを再開できる。通信切断を新規生成として再送しない。
4. MP4の解像度・フレーム数・24fps・音声ストリームを自動確認。別途、冒頭・中間・末尾の画と音を確認。
5. 480p原本と720p版、ログ、workflow、実測を回収。回収を確認してランタイムを削除し、CU消費を止める。失敗時もログを回収して終了する。
6. 生成成功と画・音の合格を制作記録へ追記してから「検証済み」とする。未生成を成功と扱わない。

## 作品の入力と実行

正典キャラクターの人物同一性、実写の顔、`VOICE_CAST.md`の声を維持する。
音声が必要なら既存採用WAVを優先し、新規VOICEVOXは`voicevox-control`、Irodoriは`tools/IRODORI_TTS.md`に従う。
画像生成には`imagegen`を使い、同僚側のDraw Things依存を持ち込まない。

- `t2v`: 画像なし。環境検証向け。人物同一性の検証には使わない。
- `i2v`: 始点・終点画像。`fl2va`モデル。両端が正しくても途中の人物崩れを確認する。
- `r2v`: キャラ参照・音声参照。`ref2va`モデル。画像最大9、音声最大3、合計12。
  `--image`順に`<Picture 1>`、`--audio`順に`<Audio 1>`。参照音声がそのまま波形コピーされるとは保証しない。
- `frames = 17k+5`、24fps。標準124〜362フレーム、短い実験も5以上で指定可能。
- 生成480pを標準とし、32pxグリッドの864×480（縦480×864）を使う。品質不足でも無断で768pへ上げない。
- `--turbo`はT2V/I2Vの8step LoRAを接続する選択肢。単にstep数だけ減らさない。実測前は高速化率や品質同等を断定しない。R2Vはbase 20stepで始める。

```sh
python3 .claude/skills/minimax-h3-video/scripts/build_workflow.py \
  --mode r2v --prompt-file 03_SCRIPTS/<run>/ch1_prompt.txt \
  --frames 124 --image character.png --audio dialogue.wav \
  --out 03_SCRIPTS/<run>/ch1_workflow.json
```

参照入力はworkflowと同じディレクトリに実体で置き、フラットなファイル名を指定する。
CUDA機へ必要なworkflow・入力・`setup_cuda.py`・`run_workflow.py`だけを渡す（.envや認証情報を一括zipしない）。

```sh
python3 setup_cuda.py ch1_workflow.json --root /content/mmu-h3 \
  --territory-evidence '確認した実行リージョンと根拠'
python3 run_workflow.py ch1_workflow.runtime.json --out ch1.mp4
```

setupは専用の新規runtime向け。既存ComfyUIはそのサーバーを`run_workflow.py --server`へ渡し、モデルと入力を配置する。
異なる入力や修正版は出力名も変更する。ジョブ記録の削除による盲目的再送を避ける。

## 監査と納品

台本・実プロンプト・入力・設定・実測記録を`03_SCRIPTS/<run>/`へ。
動画・重み・テスト中間物はGitへ入れない。ゲーム採用動画だけ既存の正典規則に従う。
声の変更・二重発話・別のキャラの口が動く・途中の顔/身体変化を確認する。
字幕と仕上げは`remotion-video`へ委ね、480pから720pへ通常リサイズを一度だけ行う。
864:480は厳密な16:9ではないため、1280×720への仕上げは縦横比を維持して微小余白を足す。

スクリプト変更後は`build_smoke_notebook.py`で埋め込みコードを再生成する。
