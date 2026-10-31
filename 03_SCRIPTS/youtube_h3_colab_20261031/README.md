# Colab × MiniMax H3 解説 v2

ユーザー確認用。制作のみで、公開・アップロード・追加GPU利用・購入は実施しない。

- 完成動画：`final_remotion_h3_colab_v2.mp4`（14分00.43秒、1280×720 / 30fps）。v1 MP4も保持。
- 台本：`script.md`。編集入力の正本：`remotion/dialogue.txt`
- 整数フレームのタイムライン：`remotion/src/edit-manifest.json`
- 料金調査：`research/pricing.json`、動画資料：`guide.md`、実行指示書：`workflow.md`
- 音声：VOICEVOX 0.25.1、ずんだもんstyle3 / speed1.15、四国めたんstyle2 / speed1.13。24kHz mono原本。完成ミックス48kHz stereo。
- 既存例：`youtube_project_intro_20261019`の左右立ち絵・簡素な中央資料、`youtube_flutterkaigi_20261021`の質問から技術へ進む構成を参照。

## 再現

リポジトリルートのPython環境 `.local/voicevox-explainer/venv`（requests・numpy・Pillow）、ffmpeg、Node.jsを使用。音声を再生成する場合はVOICEVOXを127.0.0.1:50021で起動する。保存済みの音声・クエリを原本として保持する。

`remotion/`内で実行：

```sh
python3 prepare_assets.py
npm ci
../../../.local/voicevox-explainer/venv/bin/python prepare_voice.py
npm run typecheck
../../../.local/voicevox-explainer/venv/bin/python render.py
```

表示原文と読みを分離し、共有辞書と作品辞書を適用。最終クエリ・話者・エンジンのhashで音声を識別する。BGMのみの修正ならmix_audio.pyを実行し、映像はstream copyして別版へ保存する。

`public/`の第三者立ち絵・音楽、生成動画、プレビューはGit管理外。採用した各セリフWAV、音声クエリ、字幕、編集コード、軽量記録を保持する。

## 使用素材

立ち絵は坂本アヒル式ずんだもん・四国めたんの既存準備済み差分。BGMは昼下がり気分／KK、ほのぼのワルツ【リコーダー】／エクシエ、TheFatRat - Unity。挿入BBQにはCorncob／Kevin MacLeodが含まれる。取得元と必要クレジットはguide.mdへ記載。

## 検証範囲

読みのモーラ確認、字幕の文字・2行上限、TypeScript、価格計算、代表レイアウト、MP4の形式と全編デコードを確認する。主観的な通し試聴と連続再生による目視の合格を機械検査で代替しない。詳細は`qa_final_v2.json`と`reading_audit_v2.json`。

## 版の記録

- v1：13分52.3秒。9つの内部区分、画面の章案内なし。Git `b50277f2` が再現ソース。`delivery_v1.json`・`voice_generation_record.json`・`qa_final.json`は保持。
- v2：14分00.43秒。対象を「AIツールは使うが動画モデルの自力実行は初めての人」と明示。5章のタイトル・問い・現在の章表示を追加。品質と作例を冒頭へ移し、役割・作り方・料金・注意点の順へ整理。
- v2の音声記録：`voice_generation_record_v2.json`、`mix_record_v2.json`。価格の調査日と生成実測はv1と同一。
- `render.py`はmanifestのrevisionを出力名に使い、既存の完成MP4がある場合は停止する。提示済み版を上書きしない。
