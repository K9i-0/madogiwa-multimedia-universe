# めたんのミステリー研究所 第2回：ちくわ人工物説

## 採用内容

115発話、9分21.433秒、1280×720、30fps。
研究の観察・実験は妥当だが、目的や背後関係になると「闇の政府」へ飛躍する。ずんだもんはちくわが生物であることを常識とし、毒ちくわの外見は二人とも判別できない。

旧生物解説版 `../chikuwa_biology_explainer_20261025/` は保持。今作は `../youtube_sobaya_mystery_20261010/` v10の番組演出・研究員名・BGMを継承した別作品。前作の木村人事担当は今作未登場。

## 完成版

`final_remotion_chikuwa_mystery.mp4`（動画はGit管理外）
`script.md` / `dialogue.txt`：採用台本。`dialogue.json`：機械用。
`assets.json`：素材正本への参照。`prepare_assets.py`：hardlinkと資料フレーム生成。
`voice_*.wav` / `audio_queries/`：採用音声と再生成クエリ。
`remotion/src/edit-manifest.json`：実測音声尺に基づく唯一のフレーム正本。

## 再生成

リポジトリルートから実行。VOICEVOX 0.25.1をlocalhost:50021で起動。

```sh
python3 03_SCRIPTS/chikuwa_mystery_20261025/prepare_script.py
.local/voicevox-explainer/venv/bin/python 03_SCRIPTS/chikuwa_mystery_20261025/prepare_voice.py
npm ci --prefix 03_SCRIPTS/chikuwa_mystery_20261025/remotion
.local/voicevox-explainer/venv/bin/python 03_SCRIPTS/chikuwa_mystery_20261025/remotion/render.py
.local/voicevox-explainer/venv/bin/python 03_SCRIPTS/chikuwa_mystery_20261025/audit_output.py
```

Remotion 4.0.538（npm確認済み）。音声はめたんnormal2 / speed1.13、ずんだもんnormal3 / speed1.15。共有辞書＋作品内の文脈限定読み補正。24kHz音声を48kHzステレオでミックス。会話-18LUFS、BGM-35LUFS、Unity-38LUFS、資料クリップ-19LUFS。口パクは音声RMS、まばたきあり。

## 検証と公開

`reading_audit.json`：全発話の読み確認と修正履歴。
`visual_audit.md` / `audit.json`：画面・字幕・全編デコード・フレーム数・ラウドネス確認。
人による通し試聴は未実施。字幕は原文保持、各発話に合わせて最大2行で表示。

公開・Studio登録は未依頼のため実施していない。概要欄とメタデータは納品用。誘導用Shortsは候補のみで、任意の選択待ち。本編の完成を妨げない。

UnityのYouTube利用条件は2026-10-25に公式terms/copyrightページで再確認。必要なクレジットはyoutube_description.txtに記載。
