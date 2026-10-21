# ゆめみ採用試験 技術解説 改訂v2

ずんだもん＆四国めたん。参考は窓際族物語紹介v5。

- `remotion/dialogue.txt`: 台詞と画面指定
- `remotion/src/edit-manifest.json`: 30fps整数フレーム正本
- `remotion/prepare_voice.py`: 共有読み辞書と作品辞書を利用。VOICEVOX 0.25.1、ずんだもん3/1.15、めたん2/1.13
- `remotion/prepare_media.py`: シミュレーター収録から素材化
- `remotion/render.py`: Remotion映像・音声ミックス・AAC mux
- `guide.md`: 未公開の解説資料

レンダー：`cd remotion && npm ci && npm run render`（リポジトリ内のVOICEVOX用venvを使用）。

投稿・Studio登録は行わない。初稿の確認後に誘導用Shortsの切り出しを選ぶ。

## ローカル入力と再生成

完成v1は `final_remotion_flutterkaigi_v1.mp4`（8分10.2秒、1280×720、30fps）。
本番セリフWAV、最終AudioQuery、字幕、編集マニフェスト、採用画像を保存している。
音声を変更するときだけ `prepare_voice.py` を実行する。再ミックスだけなら `mix_audio.py` と映像stream copyを使う。

BGMと過去Tripo動画の抜粋は `prepare_assets.py` で既存ローカル作品から復元できる。
ゲーム収録はGit管理外。`remotion/out/{odatetsu,sobaya,night}_raw.mov` と採用クリップはこのマシンに保持。
対象は sibling `flutterkaigi2026/app`、revision `4f3ffba1edc84f571723822d583f2c4b44f4a31d`。
Marionette `madogiwa.catchAction` の `select` / `demo` で撮影用自動入力を使い、
iPhone Duo Simulatorのdisplay 3を `simctl io recordVideo --display=3` で収録した。
収録動画は性能評価用ではない。`prepare_media.py` は5秒地点から18秒を切り出す。
新しいマシンではこの収録素材の移送または再収録が必要。

制作時点では開催前だが、ユーザー指定どおり展示後に使う語りとしている。
主観的な通し試聴は未実施。自動音声認識・音量・映像監査の記録は `qa_report.md` を参照。

## 改訂v2（2026-10-21 フィードバック反映）

- 最新出力: `final_remotion_flutterkaigi_v2.mp4`、10分33.7秒、1280×720、30fps。
- AI利用の一般論を縮め、Dart MCP、Marionette MCP、mobile MCPの仕組みと実プロジェクトの検証方法を追加。
- 新しい資料画面は `remotion/src/WorkflowViews.tsx`。専用拡張とdebug/profileの使い分けまで説明。
- Flutter公式配布ロゴ、OpenAI公式アプリ同梱のCodexアイコンを無改変で使用。取得元・hashは `asset_sources.json`。
- `script.md`、`guide.md`、SRT、概要欄をv2に同期。v1の完成MP4は保持。
- MCP部分の確認用抜粋: `preview_mcp_v2.mp4`。
- 最終生成は101発話・150字幕ページ。v1採用音声は保持し、変更のない発話を再利用。
