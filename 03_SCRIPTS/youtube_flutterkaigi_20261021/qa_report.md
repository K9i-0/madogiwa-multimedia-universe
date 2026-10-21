# 改訂v5 検証記録 — 2026-10-21

- v4の104発話を維持し、図解・資料構図・会話の間・字幕同期を全編改修。対応表は`editing_v5.md`。
- `npm run typecheck`と`git diff --check`合格。全45種類の画面、追加69フレームの茶番・段階表示・中間/終端を目視確認。
- 採用WAVを変速せず、前50ms・後80msを残して低振幅区間のみトリム。切除部分の絶対振幅が0.003以下であることを104発話で確認。波形閾値0.01で発話間隔の中央値0.405秒、最小0.220秒、最大0.777秒。
- 163字幕ページの原文保持・時間範囲・音声トリム範囲を検証。VOICEVOXのprefix読みと元クエリのモーラ長で字幕と語句強調を同期。prefix対応で5モーラを超える差異なし。
- Marionetteによるstartボタンの実タップを追加収録。seed1→start→step6秒・入力0→inspectの実取得値と同時スクリーンショットを保存（score100、x0、caught1、activeCans3）。性能試験とは区別。
- おだてつの顔と衣装が見える資料用クロップ、Tripo資料領域だけのクロップ、モデル内の実テクスチャを使用。テクスチャ面積比は解像感比較ではないと明記。
- 全編ミックスをWhisper-smallで自動認識（26区間）。台本の主要内容・順序を確認。音声認識の表記と実際の発音は区別。
- FlutterロゴはGPU説明のみ。概要欄の商標帰属・非公式表記を維持。YouTubeへの投稿・概要欄更新は未実施。
- **主観的な通し試聴は未実施。** 波形・モーラ・ASRによる同期検証は聴感評価とは区別する。
- 証跡（Git管理外）：`remotion/out/audit/`、`out/beat_audit_v5/`、`out/timing_validation_v5.json`、`out/full_audio_asr_v5.json`。

- 完成ファイル：`final_remotion_flutterkaigi_v5.mp4`、47,411,571 bytes。H.264、1280×720、30fps、19,098フレーム、636.600秒（10分36.6秒）。AAC 48kHzステレオ。
- 完成MP4を映像・音声とも終端までデコードしエラーなし。AAC sample peak −1.7dBFS、mean −22.0dBFS。
- 完成MP4から字幕開始・終了・中間、先頭・末尾の491フレームを抽出。全163ページの中間フレームを9枚のコンタクトシートで目視確認。証跡は`remotion/out/final_audit_v5/`。

---

# 改訂v4 検証記録 — 2026-10-21

- ゲーム最新commit `6652753`をDart MCPからdebug起動し、Marionetteで画面・状態を確認。選択画面、昼/夜/そば屋のプレイ、おだてつのキャラクター中心5倍ズームを再収録。
- 4本の採用クリップ（通常18秒×3、アップ12秒）の先頭・中間・終端を確認。旧版の画面、結果ダイアログ、録画UIは混入なし。
- 全45種類の中央レイアウトを実フレームで目視確認。モデル紹介4:47.1〜5:00.4はおだてつのアップ、次にTripo動画。
- 「参考にしてみてね」、通常プレイの20秒、ピンチズーム、カメラ基準操作、Claude Codeの操作性改善に台詞を更新。変更5発話だけ音声再生成。未採用の一時音声はoutへ退避。
- 104発話・163字幕ページの原文保持、時間範囲、採用WAVの存在を検証。変更5発話のVOICEVOXかな情報を確認。
- `npm run typecheck`、`git diff --check`合格。
- 旧版v1〜v3を保持。Flutter商標帰属・非公式表記を概要欄に維持。
- **主観的な通し試聴は未実施。** 自動音声認識・音量測定と聴感の判定は区別する。

- 完成ファイル：`final_remotion_flutterkaigi_v4.mp4`、54,790,077 bytes。H.264、1280×720、30fps、20,221フレーム、674.033333秒（11分14.0秒）。AAC 48kHzステレオ。
- 完成MP4を映像・音声とも終端までデコードしエラーなし。AAC sample peak −1.5dBFS、mean −22.2dBFS。
- 完成MP4から字幕開始・終了・中間、先頭・末尾の491フレームを抽出。全163ページの中間フレームをコンタクトシートで目視確認。差し替えの前後も配置・内容に問題なし。
- 全編ミックスをWhisper-smallで自動認識し、台本の主要内容・順序を確認。375秒付近で認識の反復が出たため、372〜404秒のBGMなし音声で再確認し、通常の説明として認識されることを確認。認識誤字と実発音は区別する。
- 証跡（Git管理外）：`remotion/out/final_audit_v4/`、`full_audio_asr_v4.json`、`recheck_audio_asr_v4.json`、`clips_v4.jpg`、`audit/views_v4_*.jpg`。

---

# 改訂v3 検証記録 — 2026-10-21

- 完成：`final_remotion_flutterkaigi_v3.mp4`、50,593,793 bytes、667.5秒（11分7.5秒）。H.264 1280×720 / 30fps / 20,025フレーム、AAC 48kHz stereo。
- FFmpegで映像・音声とも終端までデコードしてエラーなし。完成AACのsample peak −1.5dBFS、mean −22.2dBFS。
- 104発話・161字幕ページ。45種類の使用画面を実フレームで確認し、福ギュンの丸型アイコンの顔切れを修正してから本レンダー。
- 完成MP4から字幕開始・終了・中間と先頭・末尾の計485フレームを抽出。全161字幕ページの中間フレーム、先頭・末尾を目視確認。2行以内、時間の正値、全音声ファイルの存在も検証。
- 1:06.27で公開リポジトリを紹介。Flutterロゴは3:02.4から約14秒のGPU解説のみ。タイトル・締めにロゴなし。ClaudeとCodexは比較・接続図に併記。
- 技術の裏どりは`fact_check_v3.md`。SDK実出力、固定Scene fork、実アプリのMCP設定・拡張、性能改善commitと計測条件を照合。人物の訂正はユーザー指定を正本とする。
- 全編ミックスをWhisper-smallで自動認識。575秒付近だけ認識の反復が発生したため、571秒から32秒の音声単独区間で再認識し、台詞の流れを確認。1.9GB / 0.74GBなどの数値と追加固有名詞はAudioQueryのモーラも確認。
- `npm run typecheck`、`git diff --check`合格。台本・SRT・解説資料・概要欄をv3へ同期。
- **主観的な通し試聴は未実施。** ASR・モーラ・音量検証は、聴感やアクセントの最終確認とは区別する。
- 証跡：`remotion/out/final_audit_v3/`、`out/full_audio_asr_v3.json`、`out/recheck_audio_asr_v3.json`、`out/audit/`（Git管理外）。
- 概要欄原稿にFlutterの商標帰属・非提携文、Claudeアイコン出典を追加。YouTubeへの投稿・概要欄更新は未実施。

---

# 改訂v2 検証記録 — 2026-10-21

- 完成ファイル: `final_remotion_flutterkaigi_v2.mp4`、48,876,535 bytes。
- H.264、1280×720、30fps、19,012フレーム、633.733333秒（10分33.7秒）。AAC 48kHzステレオ。
- 最終MP4の映像・音声を終端までFFmpegでデコードしエラーなし。
- 完成AACのsample peak −1.5dBFS、mean −22.2dBFS。音割れを示すフルスケール到達なし。
- 101発話、150字幕ページ。原文の保持、字幕範囲と隣接区間の整合、採用WAVの存在を検証。
- 完成MP4から字幕開始・終了・中間、先頭・末尾の452フレームを抽出。全150ページの中間フレームを目視確認。
- 新規14種類のMCP図解を実フレームで確認。コード・説明文の折り返しを修正して再レンダー。
- 全編ミックス音声をWhisper-smallで自動認識し、追加MCP部分を含む台本との主要内容・順序を照合。MCP、DTD、Binding、VM Service等はVOICEVOXクエリの読みも点検。
- `npm run typecheck` と `git diff --check` 合格。
- Flutterロゴは公式ブランドページ、CodexアイコンはOpenAI公式アプリ同梱の素材。画像の色・形は変更せず、出典とSHA-256を保存。
- 対象ゲームの `.mcp.json`、`.codex/config.toml`、`app/lib/main.dart`、README、実機性能記録を参照。Dart MCP・Marionette・mobile MCPの一次資料も照合。
- MCP抜粋: `preview_mcp_v2.mp4`、約193.7秒、本編のMCP章をstream copy。
- **主観的な通し試聴は未実施。** 自動音声認識・モーラ照合・音量測定は聴感の最終確認ではない。
- 証跡（Git管理外）: `remotion/out/final_audit_v2/`、`remotion/out/full_audio_asr.json`、`remotion/out/audit/`。

---

# 初稿v1 検証記録 — 2026-10-21

- 完成ファイル: `final_remotion_flutterkaigi_v1.mp4`、43,081,891 bytes
- H.264、1280×720、30fps、14,706フレーム、490.2秒
- AAC、48kHz、ステレオ。完成AACのsample peak −1.6dBFS、mean −22.3dBFS（FFmpeg volumedetect）。
- FFmpegで映像・音声とも終端までデコードしエラーなし。
- `npm run typecheck` 合格。
- 87発話、118字幕ページ。字幕原文保持と時間範囲を検証。BudouXと保護語で改行を作り、Flutter Scene等の語中分割を修正。
- 全32種類の中央画面をレンダーして確認。完成MP4から字幕開始・終了・中間と先頭・末尾の計356フレームを抽出。全118字幕ページの中間フレームをコンタクトシートで目視確認。
- おだてつは公式写真。「パーマの男性」「若手社員」。福ギュン表記を採用。
- 実ゲーム3クリップ、過去Tripo解説の採用v6抜粋を確認。ゲーム映像には撮影用自動入力・シミュレーターの注記あり。性能数値は映像の測定値ではなくcommit 4f3ffbaの記録。
- Flutter GPU/SceneのStable対応、SDK・forkのpin、役割分担と共同著者表記はソース調査に基づく。Claude表記のないコミットをCodexと断定しない。
- 全編のミックス音声をWhisper-smallで自動認識し、台本の順序・主要内容を照合。固有名詞・専門用語のASR誤認は残る。VOICEVOX AudioQueryで「APIの安定性」の誤読を特定して再生成、共有辞書にも反映。
- **主観的な通し試聴は未実施。** 音量測定・ASR・モーラ照合は、聴感、アクセント、BGMとの聴き取りやすさの最終判定ではない。
- 証跡（Git管理外）: `remotion/out/final_audit/report.json`、`remotion/out/full_audio_asr.json`、`remotion/out/audit/`、`remotion/out/final_audit/`。

冒頭確認用: `preview_opening_v1.mp4`（約64秒）。投稿は未実施。
