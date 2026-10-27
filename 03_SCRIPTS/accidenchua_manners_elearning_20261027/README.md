# アクシデンチュア 新入社員向けeラーニング

「窓際マナー研修」全5問、改訂2。内容の正本は `content.json`、完成台本は `script.md`。
全事例の出演はそば屋＋福ギュン。第3問の正解は「窓際なのにすみません」。
全15選択肢について、誤り／正解の理由をゆめテレアナウンサーの声で解説する。

古い業務ソフト風の青いヘッダー、フォルダツリー、灰色の立体ボタン、表形式の一覧、
赤い「未完了」をRemotionで描画する。参考画像は `references/legacy-lms-ui.jpg`。
人物映像はH3、画面・字幕・設問・音楽ミックス・完成映像はRemotion。

## 再現

リポジトリルートから実行する。既存WAVは再利用され、同じIDで文言が変わった場合は生成を止める。

```sh
python3 03_SCRIPTS/accidenchua_manners_elearning_20261027/generate_voices.py
```

第1問は初版のそば屋＋福ギュン映像を再利用。第2〜5問の今回のH3入力は
`prompt_q2_r2.txt`〜`prompt_q5_r2.txt` と対応する `*_workflow.json`。
実行済みジョブを再送せず、`status` / `fetch` で状態確認・回収する。
再生成が必要な場合だけ、新しい出力ディレクトリとセッション名で新規ジョブを作る。

```sh
python3 03_SCRIPTS/accidenchua_manners_elearning_20261027/build_h3_r2.py
python3 .claude/skills/minimax-h3-video/scripts/colab_h3.py run --job 03_SCRIPTS/accidenchua_manners_elearning_20261027/generated/h3-r2 --session UNIQUE_REVISION_SESSION --gpu A100
```

`build_h3_r2.py` は既存の実行済みジョブを上書きしない。ColabはA100を1台使用し、
結果のダウンロードとハッシュ照合後に自動停止する。生成は864×480、24fps、Turbo 8 steps。
初版のプロンプト・workflow・採用WAV・完成動画は保持している。

採用映像の正本は `scene-sources.json`。各事例の白Tに出た小さな点状陰影を
`retouch_video.py` / `retouch_r2.py` で局所補修し、元動画・音声・解像度を保持する。
第1・4問の最終ミックスASRでの文言判定の揺れ、第2問の重複した間投詞と遅い発話開始に対応し、正典WAVを場面の発話位置に合わせて配置。事例映像中はBGMを外す。
編集上の差し替えと発話開始位置は `edit-overrides-r2.json` に記録する。

```sh
python3 03_SCRIPTS/accidenchua_manners_elearning_20261027/retouch_video.py
python3 03_SCRIPTS/accidenchua_manners_elearning_20261027/retouch_r2.py
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/accidenchua_manners_elearning_20261027/audit_audio.py 03_SCRIPTS/accidenchua_manners_elearning_20261027/*_anchor.wav 03_SCRIPTS/accidenchua_manners_elearning_20261027/generated/h3-r2/results/*_480p.mp4
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/accidenchua_manners_elearning_20261027/prepare_edit.py
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/accidenchua_manners_elearning_20261027/audit_audio.py 03_SCRIPTS/accidenchua_manners_elearning_20261027/generated/final_q*_clip_mix.wav
cd 03_SCRIPTS/accidenchua_manners_elearning_20261027/remotion
npm ci
npm run typecheck
npm run stills
npm run render
../../../.local/Irodori-TTS/.venv/bin/python ../capture_audit.py
# generated/audit-r2/encoded の画像を確認してから、完成ファイルを検証する
python3 ../verify_delivery.py
```

今回の完成出力：`final_remotion_elearning_v2.mp4`。初版：`final_remotion_elearning.mp4`。
完成尺は8,021フレーム、334.208秒（5分34秒）。
完成解像度は1280×720、24fps、H.264／AAC 48kHzステレオ。正確な尺と検証結果は
`production-report.json`、生成計測は `compute-record.json`。
動画・生成ログ・監査画像・再構築可能な音声ミックスはGit管理外。

フォントはMS PGothic／Meiryo優先、制作Macではヒラギノ角ゴシックにフォールバック。
正典ゆめテレアナウンサー参照WAVによるIrodori音声を使用する。
音楽とチャイムは `prepare_edit.py` による独自の波形合成。
ASRは音源SHA256付きで保存し、ファイル変更時には再実行する。
ASRの文言・時刻、画像による人物・字幕、波形とラウドネスを確認する。
声質や自然さの聴感、精密なリップシンクの確認は未実施。

## YouTube

公開タイトル：eラーニング - 窓際マナー研修

https://www.youtube.com/watch?v=5XBCCTBE6GU

サムネイルは完成動画の第0フレームを抽出した `youtube_thumbnail_first_frame.jpg`。
登録結果は `youtube_upload.json`、サムネイル設定は `youtube_thumbnail.json`、公開状態は `youtube_status.json`。
完成ファイルの最終画面レビューは、ユーザーの指示により省略。既に実施した素材・字幕・音声・仕様確認とは分けて `production-report.json` に記録している。
