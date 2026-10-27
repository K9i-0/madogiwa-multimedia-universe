# アクシデンチュア 新入社員向けeラーニング

「窓際マナー研修」全5問。内容の正本は `content.json`、演出と制作条件は `script.md`。
人物映像はH3、講座画面・字幕・設問・音楽ミックス・完成映像はRemotion。

## 再現

リポジトリルートから正典音声環境を用いて実行する。

```sh
python3 03_SCRIPTS/accidenchua_manners_elearning_20261027/generate_voices.py
python3 03_SCRIPTS/accidenchua_manners_elearning_20261027/build_h3.py
python3 .claude/skills/minimax-h3-video/scripts/colab_h3.py run --job 03_SCRIPTS/accidenchua_manners_elearning_20261027/generated/h3-job --session UNIQUE_SESSION --gpu A100
```

`build_h3.py`は新規ジョブ専用。すでに生成済みの場合は再送せず、既存ジョブの`status`/`fetch`または同じ`run --job`で回収・再開する。Colabは結果照合後に自動停止する。

第2・3問は、視線を遮る構図と福ギュンの顔が入る構図へ撮り直した版を採用。再生成が必要な場合のみ、次のジョブを実行する。

```sh
python3 03_SCRIPTS/accidenchua_manners_elearning_20261027/build_retry.py
python3 .claude/skills/minimax-h3-video/scripts/colab_h3.py run --job 03_SCRIPTS/accidenchua_manners_elearning_20261027/generated/h3-retry --session UNIQUE_RETRY_SESSION --gpu A100
```

第1問の白Tに生成された点状陰影は、元動画を保持して`retouch_video.py`で局所補修する。第2・3問はH3音声の繰り返しを除くため、採用済み正典WAVに差し替える。開始フレームと編集尺は`edit-overrides.json`が正本。

```sh
python3 03_SCRIPTS/accidenchua_manners_elearning_20261027/retouch_video.py
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/accidenchua_manners_elearning_20261027/audit_audio.py 03_SCRIPTS/accidenchua_manners_elearning_20261027/*_anchor.wav 03_SCRIPTS/accidenchua_manners_elearning_20261027/generated/h3-job/results/q*_480p.mp4
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/accidenchua_manners_elearning_20261027/audit_audio.py 03_SCRIPTS/accidenchua_manners_elearning_20261027/generated/h3-retry/results/*_480p.mp4
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/accidenchua_manners_elearning_20261027/prepare_edit.py
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/accidenchua_manners_elearning_20261027/audit_audio.py 03_SCRIPTS/accidenchua_manners_elearning_20261027/generated/final_q2_clip_mix.wav 03_SCRIPTS/accidenchua_manners_elearning_20261027/generated/final_q3_clip_mix.wav
cd 03_SCRIPTS/accidenchua_manners_elearning_20261027/remotion
npm ci
npm run typecheck
npm run stills
npm run render
python3 ../verify_delivery.py
```

完成出力：`final_remotion_elearning.mp4`。動画・生成ログ・監査画像・再構築可能な音声ミックスはGit管理外。
完成尺は5,463フレーム、227.625秒（約3分48秒）。横1280×720、24fps。H3原本は864×480で保持する。
日本語フォントは制作Macのヒラギノ角ゴシックを使用。ナレーションはゆめテレアナウンサーの正典WAVを参照したIrodori音声。
音楽とチャイムは`prepare_edit.py`による独自の波形合成。外部の楽曲録音は使用していない。

ASRは文言と時刻の補助資料。声質・自然さ・精密なリップシンクの聴覚確認とは分けて扱う。
