# 窓際マナー研修 第二弾・メガジョッキ編試作

## メガジョッキ編・DVD風試作

ユーザー指定：そば屋・福ギュンを主役にH3で実写の演技を作り、古いDVD風の導入BGM、画質、安っぽいUIと真面目なナレーションで解説する。

- 正本：`content.json`、`script.md`。
- 生成：H3 480p Turbo、640×480、311フレーム／24fps、8step、A100・1worker。
- 仕上げ：4:3、960×720、24fps。`remotion/src/edit-manifest.json` に整数フレームのタイムラインを保存。
- 配役：そば屋（正典Large＋monsterize）、福ギュン（正典Small）、本作専用の男性教材ナレーター（Irodori Smallによる独自音声デザイン、FB1の解説改稿2ブロックは同じ参照WAVを使うv4 Large）。設定・参照・実測尺は `voice-records.json`。
- H3原本：`scene-sources.json` の採用パス。v1は余分なジョッキと白Tの点状陰影で不採用。v2では内蔵imagegenで作った `input_mega_scene_v2.png` を唯一の画像入力にする。画像生成の実プロンプトは `prompt_image_mega_scene_v2.txt`。
- v2に残った白Tの小さな黒点だけを `retouch_shirt.py` で追跡・局所補間。元動画を保持し、640×480のまま可逆圧縮し、元のAAC音声はビットストリーム一致を確認してコピー。補修領域・フレームは `retouch-record.json`。
- 元の参考動画は `generated/reference/` に取得して画面を観察。完成品には映像・音声とも流用していない。音楽は `prepare_edit.py` の独自合成。
- 完成出力：`final_remotion_mega_dvd.mp4`（64.833秒、1556フレーム）。機械検証と目視・聴感の確認範囲は `production-report.json` に区別して記録する。

初版は完成MP4の全編デコードと58枚の抽出画面、ミックス音声のASRを確認。FB1ではユーザーの指示により自動認識の追加確認を停止し、既存候補から音声を採用した。最新の画面・再生データの確認範囲は `production-report.json`。聴感と細かな口パクは未確認。H3のGPUランタイムは終了済み。

再現（リポジトリルートから）：

```sh
python3 03_SCRIPTS/accidenchua_manners_elearning_2_20261028/generate_voices.py
# 初回生成のみ。既存ジョブの再送はしない。
python3 03_SCRIPTS/accidenchua_manners_elearning_2_20261028/build_h3_v2.py
python3 .claude/skills/minimax-h3-video/scripts/colab_h3.py run --job 03_SCRIPTS/accidenchua_manners_elearning_2_20261028/generated/h3-mega-v2 --session UNIQUE_SESSION --gpu A100
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/accidenchua_manners_elearning_2_20261028/audit_audio.py 03_SCRIPTS/accidenchua_manners_elearning_2_20261028/scene*.wav 03_SCRIPTS/accidenchua_manners_elearning_2_20261028/explain*.wav 03_SCRIPTS/accidenchua_manners_elearning_2_20261028/generated/h3-mega-v2/results/video_480p.mp4
uv run --with opencv-python-headless --with numpy python 03_SCRIPTS/accidenchua_manners_elearning_2_20261028/retouch_shirt.py
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/accidenchua_manners_elearning_2_20261028/prepare_edit.py
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/accidenchua_manners_elearning_2_20261028/audit_mix.py
cd 03_SCRIPTS/accidenchua_manners_elearning_2_20261028/remotion
npm ci
npm run typecheck
npm run stills
npm run render
python3 ../verify_delivery.py
```

FB1では解説の理由を丁寧な語りかけへ広げ、締めを「できる社会人の気配り」へ変更。改稿音声は `explain03_fb1.wav` / `explain04_fb1.wav`。変更前の動画・台本・ミックス・監査記録は `generated/revisions/before-fb1/` に保持。元の採用音声も別名で残す。

レンダー後、冒頭、実演、各解説、末尾、字幕の切替を目視確認する。ASRの一致を声質・自然さ・精密な口パクの合格と扱わない。

## 採用方向：名簿の左寄せを避ける

ユーザー採用案：左寄せが左遷を連想させるとして、窓際社員だけ極端に右寄せする。

- 解説用名簿は一般社員を左寄せ、「二八 そば屋」「無職 やめ太郎」の二人だけ右寄せにする。
- 「二八」は今回の名簿向けの名字案。共有キャラクター設定は変更しない。
- 一般社員名は見本用の架空名。
- 色、書体、大きさは全員共通。横幅の広い氏名欄と配置の違いだけで二人を目立たせる。
- 見本：`roster_right_aligned_preview.png`（1280×720）。
- 再生成：`uv run --with pillow build_roster_preview.py`（macOSのヒラギノ角ゴシック使用）。

解説文案：

> 左寄せは、左遷を連想させるため不適切です。該当する方のお名前だけ、右端に寄せましょう。ほかの社員と離れてしまっても問題ありません。これは隔離ではなく、配慮です。

## 上下余白のショート版 v1

- `final_remotion_shorts_9x16_v1.mp4`：720×1280、24fps、64.833秒。元の4:3完成映像を720×540で中央（y=370）に配置し、上下に黒い余白を追加。クロップ・引き伸ばし・本編UIの再配置なし。
- ユーザー指定に従いDVD内の文字・字幕を保持し、下の余白へ独立字幕を追加。上部の装飾・タイトルは追加しない。会話字幕は共通のメンバー色、ナレーションは白。
- 採用済み横版からAACを無変換コピー。音声ストリームhash一致、フレーム数、全編デコードと字幕カードの文字収まりを確認。新たな音声生成・自動認識なし。
- 実装は `render_shorts.py`（FFmpegの等比縮小・pad・ASS合成）。データは `shorts-manifest.json`、`shorts-captions.ass`、監査は `shorts-audit.json`。実行：`python3 03_SCRIPTS/accidenchua_manners_elearning_2_20261028/render_shorts.py`。既存出力がある場合は停止するので、改善版はスクリプトの出力名とversionを更新して別名で保存する。
- 2026-10-28のユーザー依頼で、横版とショート版をYouTubeへ公開。タイトルは共通で「窓際マナー研修 — 飲み会編」。

## YouTube公開

- 横版：https://www.youtube.com/watch?v=keLSYe7vwfw
- ショート版：https://www.youtube.com/shorts/elro68hH6ag
- 投稿先：窓際族物語【AI制作】（`UCyQtPu94OaiGxFdd2A6bXdw`）。
- 各版の `youtube*_metadata.json` / `youtube*_description.txt` が投稿内容、`youtube*_upload.json` が動画ID・送信ファイルhash、`youtube_publication_check.json` が公開・処理状況の確認記録。ショート版概要欄に横版リンクを記載。
- 今回の依頼はYouTubeへの2本の投稿。Studioのエピソード登録や公式サイト掲載は行っていない。
