# 本編誘導用 Shorts（2026-10-16 延長版）

本編v8の冒頭から63.433秒までを使い、挨拶と「二つを作る中で分かったコツを紹介します」まで収録。最後の画面を2秒静止し、「続きは本編で」を表示する。

- 完成版: `final_remotion_shorts_9x16.mp4`、720×1280、30 fps、1963フレーム、65.433秒。
- SHA-256: `399700064152c6f9ef686467cdae8b3f5618b66c1e9865c78a61903b5a835c88`
- 元字幕を非表示にして、16枚の字幕カードを下段へ配置。LINE・Outlook内の演出文字は維持。「異動」の訂正を保持。
- 挨拶から上部タイトルを「Codexで作る／動くLINEスタンプ」に切り替える。
- 元の発話PCMは1903フレームまで完全一致。直後の間だけBGMをフェードし、次の発話が始まる前に無音化。AACは192kbpsで再符号化。
- 共有レンダーの任意指定 `freezeAt` と `endCard` を使用。従来キューの既定表示は維持。
- 旧39.53秒版は `remotion/out/before_extended_short/` に保持。X用横動画は39.53秒版のまま。

再実行:

```bash
python3 03_SCRIPTS/youtube_line_stickers_20261015/build_shorts.py
python3 03_SCRIPTS/youtube_line_stickers_20261015/verify_shorts.py
```

検証: TypeScript、全編デコード、解像度・尺・フレーム数、元の発話PCM一致、終端無音を確認。追加字幕5枚と最後のCTAを静止画確認し、文字の欠け・重複なし。既存11枚は前版で確認済み。通し試聴と動画の主観的動作確認は未実施。詳細は `shorts-audit.json`。

本編は変更せず、YouTubeのショート予約のみ差し替える。単発の投稿として管理し、週次キュー・Madogiwa Studioへは登録しない。
