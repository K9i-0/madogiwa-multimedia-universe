# めたんのミステリー研究所 第2回：ちくわ人工物説

## 現行採用：v8

`final_remotion_chikuwa_mystery_v8.mp4`
84発話、10分03.233秒、1280×720、30fps。初版・v2・v3・v4のMP4は別名で保持。

逮捕報告の終盤で「猥褻物陳列罪」の容疑を追加開示し、ずんだもんが「酒癖が悪すぎるのだ」と突っ込む。

v6では人工ちくわと政府・企業による隠蔽は実在する。ずんだもんは天然生物と養殖という常識を信じる。研究員の調査は真相に迫り、めたんは認識や教育の統制へ話を拡張する。v7では毒ちくわの市販品混入ゼロを軸に再構成し、ずんだもんの発話を半分以下に整理。v8は調査の橋渡し、話す時刻に合わせた情報開示、静けさを使う音声編集、3カットの真相提示へ改良。詳細は `revision_v8.md`。

## 素材と再生成

- `dialogue.txt` / `script.md`：採用台本。`dialogue.json`：機械用。
- `inputs/*_v2.png`：内蔵image_genによる採用画像9点。
- `imagegen_prompts_v2.json`：全プロンプト、取得元、保存先。
- `assets.json` / `prepare_assets.py`：既存正本素材のhardlinkと資料フレーム生成。
- `voice_*.wav` / `audio_queries/`：採用音声とクエリ。以前の採用音声は保持。
- `remotion/src/edit-manifest.json`：実測音声尺に基づくフレーム正本。

リポジトリルートから実行。VOICEVOX 0.25.1をlocalhost:50021で起動。

```sh
python3 03_SCRIPTS/chikuwa_mystery_20261025/prepare_script.py
.local/voicevox-explainer/venv/bin/python 03_SCRIPTS/chikuwa_mystery_20261025/prepare_voice.py
npm ci --prefix 03_SCRIPTS/chikuwa_mystery_20261025/remotion
.local/voicevox-explainer/venv/bin/python 03_SCRIPTS/chikuwa_mystery_20261025/remotion/render.py
.local/voicevox-explainer/venv/bin/python 03_SCRIPTS/chikuwa_mystery_20261025/audit_output.py
```

Remotion 4.0.538。めたんnormal2 / speed1.13、ずんだもんnormal3 / speed1.15。共有辞書＋作品内文脈限定読み。24kHz音声を48kHzステレオでミックス。会話-18LUFS、BGM-35LUFS、Unity-38LUFS、資料クリップ-19LUFS。口パクは音声RMS、まばたきあり。

## 検証

`reading_audit_v2.json`：変更33発話の読み修正。
`visual_audit_v8.md` / `audit_v8.json`：画像・字幕・フレーム数・全編デコード・音量確認。
人による通し試聴は未実施。字幕は原文保持、最大2行で表示。

公開・Studio登録は未依頼のため実施していない。誘導用Shortsは前回の任意質問が未回答のため候補のみ。
前作の番組演出・研究員は `../youtube_sobaya_mystery_20261010/` v10を参照。旧生物解説版も保持。

UnityのYouTube利用条件は2026-10-25に公式terms/copyrightページで確認済み。必要なクレジットはyoutube_description.txtに記載。
