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
