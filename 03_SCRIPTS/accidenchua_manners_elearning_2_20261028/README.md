# 窓際マナー研修 第二弾・メガジョッキ編試作

## メガジョッキ編・DVD風試作

ユーザー指定：そば屋・福ギュンを主役にH3で実写の演技を作り、古いDVD風の導入BGM、画質、安っぽいUIと真面目なナレーションで解説する。

- 正本：`content.json`、`script.md`。
- 生成：H3 480p Turbo、640×480、311フレーム／24fps、8step、A100・1worker。
- 仕上げ：4:3、960×720、24fps。`remotion/src/edit-manifest.json` に整数フレームのタイムラインを保存。
- 配役：そば屋（正典Large＋monsterize）、福ギュン（正典Small）、本作専用の男性教材ナレーター（Irodori Smallによる独自音声デザイン）。設定・参照・実測尺は `voice-records.json`。
- H3原本：`scene-sources.json` の採用パス。v1は余分なジョッキと白Tの点状陰影で不採用。v2では内蔵imagegenで作った `input_mega_scene_v2.png` を唯一の画像入力にする。画像生成の実プロンプトは `prompt_image_mega_scene_v2.txt`。
- v2に残った白Tの小さな黒点だけを `retouch_shirt.py` で追跡・局所補間。元動画を保持し、640×480のまま可逆圧縮し、元のAAC音声はビットストリーム一致を確認してコピー。補修領域・フレームは `retouch-record.json`。
- 元の参考動画は `generated/reference/` に取得して画面を観察。完成品には映像・音声とも流用していない。音楽は `prepare_edit.py` の独自合成。
- 完成出力：`final_remotion_mega_dvd.mp4`（53.042秒、1273フレーム）。機械検証と目視・聴感の確認範囲は `production-report.json` に区別して記録する。

完成MP4の全編デコード、映像・音声形式、タイムラインを検証済み。完成MP4から抽出した58枚で章・字幕の切替を確認。実際のミックス音声もASRで文言を照合した。聴感と細かな口パクは未確認。H3のGPUランタイムは終了済み。

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
