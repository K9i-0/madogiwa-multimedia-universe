# めたんのミステリー研究所 第2回：ちくわ人工物説

## 現行制作：v13

出力先：`final_remotion_chikuwa_mystery_v13.mp4`。65発話、6分55.8秒、1280×720、30fps。
原稿：`script.md` / `dialogue.txt`。検討時の全文と演出案は `script_v13.md`、独立レビューは `reviews_v13/`。
中口の現物調査→証拠品の食事回収→霜重の現地調査という二部構成。企業による製法公開を削除し、中口の仮説と、視聴者だけが見るエンディング後の秘密を区別する。
詳細は `revision_v13.md`。

ユーザー指定により、書き出し後の完成動画チェックは実施せず、出力完了後すぐにパスを返す。旧版の監査記録はそれぞれの旧版にのみ適用する。

## 素材と再生成

- `dialogue.txt` / `script.md`：採用台本。`dialogue.json`：機械用。
- `inputs/*_v2.png`：内蔵image_genによる採用画像9点。
- `imagegen_prompts_v2.json`：全プロンプト、取得元、保存先。
- `assets.json` / `prepare_assets.py`：既存正本素材のhardlinkと資料フレーム生成。
- `voice_*.wav` / `audio_queries/`：採用音声とクエリ。以前の採用音声は保持。
- `h3_v9/`：480p Turboのプロンプト・参照画像・workflow。結果はローカル `results/`。
- `sound_design.py`：オリジナル効果音の再現可能な合成。
- `remotion/src/edit-manifest.json`：実測音声尺に基づくフレーム正本。

リポジトリルートから実行。VOICEVOX 0.25.1をlocalhost:50021で起動。

```sh
python3 03_SCRIPTS/chikuwa_mystery_20261025/prepare_script.py
.local/voicevox-explainer/venv/bin/python 03_SCRIPTS/chikuwa_mystery_20261025/prepare_voice.py
npm ci --prefix 03_SCRIPTS/chikuwa_mystery_20261025/remotion
.local/voicevox-explainer/venv/bin/python 03_SCRIPTS/chikuwa_mystery_20261025/remotion/render.py
```

Remotion 4.0.538。基本はめたんnormal2 / speed1.13、ずんだもんnormal3 / speed1.15。v9の選択的な速度・抑揚・声量・間は `prepare_voice.py` と `voice_generation_record.json` に記録。共有辞書＋作品内文脈限定読み。24kHz音声を48kHzステレオでミックス。会話-18LUFS、BGM-35LUFS、Unity-38LUFS、資料クリップ-19LUFS。口パクは音声RMS、まばたきあり。

## 確認範囲

書き出し前の字幕データ・音声クエリ・TypeScript確認のみ。`reading_audit_v13.json` に変更発話の読みを記録。完成後の監査・抜粋出力はユーザー指定で省略。
過去版の確認内容は `audit_v12.json` 等に保持。

公開・Studio登録は未依頼のため実施していない。誘導用Shortsは前回の任意質問が未回答のため候補のみ。
前作の番組演出・研究員は `../youtube_sobaya_mystery_20261010/` v10を参照。旧生物解説版も保持。

UnityのYouTube利用条件は2026-10-25に公式terms/copyrightページで確認済み。必要なクレジットはyoutube_description.txtに記載。
