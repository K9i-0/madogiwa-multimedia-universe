# そば屋解説：たこさん × やめ太郎

完成動画：`final_remotion_sobaya.mp4`（2分10秒、720p）。`preview.html`で動画と全差分を確認。`commentary_duo_32sprites.zip`に各8表情×口開閉の透過PNG32枚を収録。

共有素材正本：`../00_TEMPLATES/characters/commentary_duo_v1/`。内蔵image_genのプロンプトと入力参照は同フォルダのgeneration.json。差分書き出しはRemotionの合成結果。

制作・再現手順はscript.md、検証結果はqa.json。完成動画・ZIP・合成済みPNG・publicはGit対象外。PNGの元画像、採用WAV、コード、台本、固定依存関係を保持する。

`python3 -m http.server 8769 --bind 127.0.0.1 --directory 03_SCRIPTS/sobaya_duo_explainer_20261010`（リポジトリルートから）で視聴ページを開ける。
