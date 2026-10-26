# 公式Colab CLIでH3を使う

2026-10-26: `google-colab-cli==0.7.5`をMacへ導入。
ブラウザ版のH3実生成は確認済み。CLIラッパーの模擬ライフサイクル・通信失敗時の再開テストは合格。
**CLIからL4確保→入力転送→H3生成→480p/720p回収→ハッシュ照合→自動停止まで実機確認済み。**

2026-10-26実測: 864×480、22frames / 24fps（0.9167秒）、base20step。
セットアップ内部計測248.34秒、生成・取得検査211.08秒、リモート全工程495.84秒。
720p版は1280×720・22frames・24fps、両動画にAAC32kHz stereo。
実行中の`status`とログのダウンロードも成功。終了後`usage`でActive assignments=0 / Usage rate=0を確認。
残高表示180.60→180.48 CU（反映遅延があるため厳密な全消費ではない）。
初回認証後の実行にブラウザ操作なし。CLI実行中の通信断からの回復は模擬テストのみ。
実機結果は`.local/h3-cli-test/results/`、実行コードrevision `627e63de`。

## 同僚実装との関係

- [colab-video](https://github.com/sobaya-0141/Seedance_Madogiwa/blob/main/.claude/skills/colab-video/SKILL.md): 入力ZIP、実行単位・修正版管理が参考になる。現行はユーザーがColabセルをブラウザで実行する方式。
- [h3_run.py](https://github.com/sobaya-0141/Seedance_Madogiwa/blob/main/.claude/skills/local-video/h3_run.py): ComfyUI `/prompt`→`/history`→`/view`のAPI経路。この経路はMMUの`run_workflow.py`へ導入済みで、ジョブID保存・再送防止・MP4検査を追加した。
- GPUの確保と転送は[Google公式Colab CLI](https://github.com/googlecolab/google-colab-cli)を使用。非公開APIの独自再実装・ブラウザCookie抽出・公開ComfyUIトンネルを使わない。

## 初回だけ

```sh
uv tool install google-colab-cli==0.7.5
colab --auth oauth2 usage
```

CLIが表示するGoogle認証URLを開き、AI Plusと同じアカウントでログインし、表示されたコードを**手元のCLIへ**貼る。
チャットへコードを送らない。認証後はCLIの保存済み認証情報を利用する。
この処理はColab CLI用OAuthであり、VMへGCP権限を付与する`colab auth`とは別。
新たなGCP課金契約、MiniMax APIキー、Driveマウントは不要。既存ColabのCUを消費する。

## 普段の操作

例の`workflow.json`は`build_workflow.py`で作る。参照PNG/WAVは同じディレクトリにフラット名で置く。
ジョブフォルダは新規のものを指定する。`generated/`等のGit除外ディレクトリを推奨。

```sh
python3 .claude/skills/minimax-h3-video/scripts/colab_h3.py prepare \
  03_SCRIPTS/<run>/workflow.json --job 03_SCRIPTS/<run>/generated/h3-job

python3 .claude/skills/minimax-h3-video/scripts/colab_h3.py run \
  --job 03_SCRIPTS/<run>/generated/h3-job --session mmu-h3-unique-run --gpu L4
```

実行内容: L4確保→入力ZIP転送→固定版ComfyUI/重みセットアップ→生成→720p化→ZIP回収→SHA256照合→GPU停止。
`results/video_480p.mp4`、`results/video_720p.mp4`とJSON/ログが残る。
ローカルの`job.json`はセッション名・状態・入力ハッシュを保持。認証トークンを含めない。
CLIには実行タイムアウト10800秒を指定し、リモート側は10秒毎に進行中の表示を出す。
生成ジョブの上限は従来どおり7200秒。時間切れ時は同じジョブを再開する。

```sh
# 稼働中の状態（生成を追加しない）
python3 .claude/skills/minimax-h3-video/scripts/colab_h3.py status --job <job-dir>
# 通信断後の再開。同じジョブ・prompt_idを使う
python3 .claude/skills/minimax-h3-video/scripts/colab_h3.py run --job <job-dir>
# 完了済み結果だけを再回収する
python3 .claude/skills/minimax-h3-video/scripts/colab_h3.py fetch --job <job-dir>
# fetch後、またはrun --keepで残したGPUを停止
python3 .claude/skills/minimax-h3-video/scripts/colab_h3.py stop --job <job-dir>
colab --auth oauth2 usage
```

通信失敗時はGPUを自動破棄せず保持するため、CU消費は続く。回収・再開または明示停止まで処理を完了させる。
失敗ログは`colab download -s SESSION /content/SESSION/results.zip ./failed-results.zip`で回収できる。
続行しない失敗ランはログ回収後に`colab stop -s SESSION`。
セッション自体が失われた場合、生成の再開はできない。新しいジョブとして作り直す。
`allocating`で止まった場合は`colab sessions`で割当結果を確認し、既存セッションとjob.jsonを照合する。

## APIとして使う場合

既存CUDAマシン上でComfyUIを起動している場合は、既存のAPIクライアントを直接使える:

```sh
python3 .claude/skills/minimax-h3-video/scripts/run_workflow.py \
  workflow.runtime.json --server http://127.0.0.1:8188 --out video.mp4
```

MacからColabを使う場合は、上のCLIをプログラムから`subprocess`で呼び、job.json/resultsを読む。
追加のWeb APIサーバーや常時公開エンドポイントは不要。
