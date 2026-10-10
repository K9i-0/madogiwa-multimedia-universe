# そば屋解説：たこさん × やめ太郎

完成動画：`final_remotion_sobaya.mp4`（2分10秒、720p）。`preview.html`で動画と全差分を確認。`commentary_duo_32sprites.zip`に各8表情×口開閉の透過PNG32枚を収録。

共有素材正本：`../00_TEMPLATES/characters/commentary_duo_v1/`。内蔵image_genのプロンプトと入力参照は同フォルダのgeneration.json。差分書き出しはRemotionの合成結果。

制作・再現手順はscript.md、検証結果はqa.json。完成動画・ZIP・合成済みPNG・publicはGit対象外。PNGの元画像、採用WAV、コード、台本、固定依存関係を保持する。

`python3 -m http.server 8769 --bind 127.0.0.1 --directory 03_SCRIPTS/sobaya_duo_explainer_20261010`（リポジトリルートから）で視聴ページを開ける。

## Voidoll比較版（2026-10-10）

ユーザーの試聴依頼で、たこさん12行をVOICEVOX:Voidoll（ノーマル89、速度1.0）へ差し替え。やめ太郎は元のIrodori音声。全体正典・元動画は維持。比較候補のWAVはremotion/out/voicevox/へ保存し、未採用のためGit対象外。

- 全編：final_remotion_sobaya_voicevox.mp4（124.9秒）
- 声だけの冒頭3行：takosan_voicevox_sample.mp3
- エンジンと合成クエリ・実測時間：voicevox_record.json
- 再現：エンジンを127.0.0.1:50021で起動 → generate_voicevox.py → Irodori環境のPythonでremotion/prepare.py --voicevox → remotionでnpm run render:voicevox
- タイミング正本：remotion/src/edit-manifest-voicevox.json。字幕・RMS口パクを新しい音声尺から再計算。終端にVOICEVOX:Voidollクレジット。
- 読みとファイル構造を検証。声の自然さ・精密な口パク同期の実試聴確認は未実施。
