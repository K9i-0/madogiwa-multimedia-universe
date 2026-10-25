# ゆめみ採用試験 技術解説 改訂v8

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
旧収録の対象は sibling `flutterkaigi2026/app`、revision `4f3ffba1edc84f571723822d583f2c4b44f4a31d`。
Marionette `madogiwa.catchAction` の `select` / `demo` で撮影用自動入力を使い、
iPhone Duo Simulatorのdisplay 3を `simctl io recordVideo --display=3` で収録した。
収録動画は性能評価用ではない。v1〜v3では5秒地点から18秒を切り出した。
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

## 改訂v3（全体の流れを再構成）

- 最新出力：`final_remotion_flutterkaigi_v3.mp4`、11分7.5秒、1280×720、30fps。v1/v2は保持。
- 1分6秒で公開リポジトリを紹介。人物紹介→素材のつながり→3D描画→MCPによる開発・検証→実機改善、という流れへ改稿。
- ゆめプロの説明、Chief Ticket Officerの意味と愛称の由来、若手社員の紹介を修正。
- 実際のYouTubeチャンネル画像と福ギュン・そば屋の丸型アイコンを追加。
- FlutterロゴはGPU説明の1区間のみ。Claude公式アプリ同梱アイコンを追加。概要欄の商標帰属文を更新。
- `fact_check_v3.md`にSDK・固定依存版・MCP・性能記録・ブランド資料との照合結果を保存。
- 104発話・161字幕ページ。VOICEVOX設定とBGM方針は継承。変更した台詞だけ再生成。

## 改訂v4（最新版ゲームへの更新）

- 最新出力：`final_remotion_flutterkaigi_v4.mp4`、11分14.0秒、1280×720、30fps。v1〜v3を保持。
- ゲーム6652753をDart MCPで起動。Marionetteで選択・撮影用自動入力・キャラクター中心の5倍ズームを操作し再収録。
- 原本は`remotion/out/{odatetsu,sobaya,night,closeup}_v4_raw.mov`。`prepare_media.py`で通常は3秒から18秒、アップは1秒から12秒を素材化。
- 公開コードの紹介は「参考にしてみてね」。操作説明はカメラ基準入力とピンチズームへ更新。通常プレイが20秒であると明示。
- 3Dモデル紹介はおだてつのアップ→過去のTripo解説の順。選択画面・ちくわ画像も更新。追加機能の網羅説明はしない。
- `fact_check_v4.md`に変更根拠を記録。性能章の数値は従来どおり4f3ffbaの履歴。

## 改訂v5（図解・テンポ・字幕の全編再編集）

- 最新出力：`final_remotion_flutterkaigi_v5.mp4`、10分36.6秒、1280×720、30fps。過去v1〜v4を保持。
- 台詞を削らず104発話を維持。採用WAVは再生成せず、前後の低振幅区間だけをトリム。速度変更なし。
- `remotion/src/VisualsV5.tsx`：描画階層、MCP接続経路、発声に同期した強調、ゲームの模式図、実取得状態、尺度を共有する比較グラフ、実テクスチャの面積比。
- 中央1040px・立ち絵165pxを基本に、茶番のみ立ち絵205px。字幕は中央890px、話者色を維持。
- `prepare_edit_v5.py`：元の採用WAV/AudioQuery/voice_generation_recordからv5タイムラインを再生成。字幕境界と強調語は元クエリのモーラ長を用いる。prefixの読みはVOICEVOXで解析して対応を確認。再生成時はVOICEVOX起動が必要。
- `edit_timing_v5.json`：各発話の元音声トリム、文脈別の間、語句cue。最終フレーム正本はsrc/edit-manifest.json。
- `prepare_media_v5.py`：既存素材の資料抜粋・アップ、追加実操作収録から素材化。
- 再ミックス・レンダー：`python mix_audio.py` → `python render.py --no-mix`（共有venv）。音声を変更して`prepare_voice.py`を使った場合、その後に`prepare_edit_v5.py`で編集タイミングを生成する。
- 実ゲームの追加取得結果は`inspection_v5.json`。撮影は6652753、シミュレーターdebug。性能の数値は従来の4f3ffba実機記録。
- 映像演出の確認：`audit_frames.cjs`（全45画面）、`audit_beats_v5.cjs`（茶番・段階表示などの中間/終端）。完成MP4は`audit_output.py`。

## 改訂v6（スライドの情報整理）

- 出力：`final_remotion_flutterkaigi_v6.mp4`。10分36.6秒、1280×720、30fps。
- 台詞・字幕・音声・タイムラインはv5を維持。`VisualsV5.tsx`を`VisualsV6.tsx`へ移行。
- ゲーム映像下の長い注記、スライドでの台詞の二重表示、制作事情のフッターを削除。見出しを短くし、図のラベル・比較値・操作手順を中心にする。
- 茶番はゲーム映像を使用。人物紹介とリポジトリの重複説明、登壇日時・会場表示も整理。
- 整理した内容は`editing_v6.md`。撮影条件・出典は従来の素材台帳・QA・概要欄に保持。
- `node audit_frames_v6.cjs`で全画面確認、`python audit_output.py`で完成ファイル監査。

## iPhone 18 Pro 横画面への差し替え

v6のゲーム映像・選択画面・inspect画像・MCP操作実演はiPhone 18 Pro（A4EB7AA4-DDDC-4B36-9E79-8FF7579F5162、iOS 27.0）で再取得。アプリは横画面固定、論理874×402。ゲームrevisionは6652753。端末の横長比率を保持し、図のUI枠も配置を修正。

通常3本は撮影用入力、アップは4.5倍・character中心で正面から収録。素材化は`remotion/prepare_media_v6.py`。元録画は`remotion/out/*_v6_raw.mov`。過去版の素材は保持。

## 改訂v7

- 最新出力：`final_remotion_flutterkaigi_v7.mp4`、11分54秒、1280×720、30fps。
- タスク管理とチケットをさばく達人の台詞を削除。登壇紹介を「今年のゆめみのスポンサーセッションに登壇しているわ。」へ変更。
- UIのレイアウト、具体的な中央配置、GPUリソース、三角形の描画、Flutter Sceneとの関係を5種類の図で説明。
- 変更していない発話音声とiPhone 18 Pro横向き映像は再利用。
- 音声改稿時は `prepare_voice.py` → `prepare_edit_v5.py` → `render.py` の順で実行。

## 改訂v8（2026-10-25）

- 最新：`final_remotion_flutterkaigi_v8.mp4`、12分20.9秒、1280×720、30fps。
- 公開ゲーム5a11e01をfetch後のorigin/mainと照合。全ゲーム映像をiPhone 18 Pro横向きで再収録。街のビル・看板、選択画面などを更新。
- モデル説明の流れにギャラリー、ちくわ説明に同一形状・材質切替を追加。使用SDKを3.47.8へ更新。
- v8素材化はprepare_media_v8.py。rawはremotion/out/*_v8_raw.mov。録画はsimctl、操作はDart VM Service拡張（MCPの版不一致の代替）。
