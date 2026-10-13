# 生成AI動画制作の解説

1280×720 / 30fps。台本正本は dialogue.json、読みと実測タイミングは src/edit-manifest.json。
VOICEVOX 0.25.1、めたん2 / ずんだもん3。採用済み解説テンプレの立ち絵・静かな音響方針を継承。

## 再現

- `npm ci`
- `python prepare_assets.py`（リポジトリにローカル素材が必要）
- VOICEVOXを127.0.0.1:50021で起動
- `../../../.local/voicevox-explainer/venv/bin/python prepare_voice.py`
- `npm run typecheck`
- `npm run render`

Remotion 4.0.535（npmで安定版確認）。APIキー・生成課金は不要。既存の作品素材を使用。
音声キャッシュはエンジン版・話者・クエリをSHA-256で識別。
第三者の立ち絵・BGM・生成動画はpublicにhardlinkしGit管理外。
最終MP4はエピソード直下、確認用MP4と監査フレームはout/へ保存。

料金・外部出典：../sources.json。クレジット：../youtube_description.txt。

## 納品と監査

完成版は `../final_remotion_ai_video_workflow.mp4`（9分7秒）。`../delivery.json`、`../review.md`、`../speech_audit.json`に検証結果と制約を記録。全編再現は通常の `npm run render`。最終版では冒頭ラベルの修正のみ25.8秒まで再レンダーし、本編とAACを再エンコードせず接続している。
