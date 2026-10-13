# メンバー紹介（2026-10-13）

台詞は dialogue.txt、引用範囲は clips.json、完成タイムラインの正本は src/edit-manifest.json。
VOICEVOX 0.25.1、四国めたん2、ずんだもん3。既存解説の採用速度を維持。

リポジトリルートから：

```sh
.local/voicevox-explainer/venv/bin/python 03_SCRIPTS/youtube_members_explainer_20261013/remotion/prepare_assets.py
.local/voicevox-explainer/venv/bin/python 03_SCRIPTS/youtube_members_explainer_20261013/remotion/prepare_voice.py
```

このディレクトリで `npm ci`、`npm run typecheck`、`npm run render`。
生成音声の正本はエピソード直下。キャッシュキーはエンジン版・話者・本文・速度を含む。
人物素材と元映像は変更せず、publicへhardlink。第三者音源と立ち絵は既存採用素材を利用。
原音付きクリップでは解説停止。通常画面は左右立ち絵・中央資料・下部字幕。
音楽クレジットと参考記事はエピソード直下youtube_description.txt。

`export_metadata.py`で採用WAVを整理し、概要欄のチャプターとSRTを再生成。`audit_output.py <MP4>`で最終映像・字幕境界・引用字幕の全種類を抽出し、目視用コンタクトシートと構造検証を作成。`audit_mix.py`で全発話区間の音量とクリッピングを検査。ASRは`.local/Irodori-TTS/.venv/bin/python`で`audit_asr.py`または`audit_full_audio.py`。自動音声確認を主観的通し試聴の合格と扱わない。
