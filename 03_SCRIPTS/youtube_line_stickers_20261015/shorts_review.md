# 本編誘導用 Shorts（2026-10-16）

採用 v7 の冒頭を `0–1185` フレーム（39.533 秒）で切り出し。スタンプの使い所から LINE 通知、Outlook の辞令、廃村／Python のオチまでを含み、挨拶は含まない。

- 完成版: `final_remotion_shorts_9x16.mp4`、720×1280、30 fps、1186 フレーム、H.264 + AAC 48 kHz stereo。
- SHA-256: `065975a3a0dca452c73b3e26a9f79b8aab25e083f520a947ed155cd9a05039f6`
- 元動画: `final_remotion_line_stickers_v7.mp4`。本編ファイルと台本・採用音声は変更していない。
- レイアウトは `03_SCRIPTS/shorts_queue_20261011/remotion/src/index.tsx` を再利用。共有コードへ任意の `titleCues` だけ追加し、従来キューの既定表示は維持。
- 元映像の会話字幕は `Explainer` の `hideCaptions` で外して再レンダー。LINE トークと Outlook メールなど演出の文字は残す。
- 会話字幕は原稿と整数フレームを保ち、下余白に 11 カードで再配置。名前 28 px、セリフ 38 px、やめ太郎は紫、たこさんはピンク。最長 3 行。
- 上部は「LINEスタンプで／ガチの島流し」。最後のツッコミ中だけ「作り方はチャンネルの本編へ／動くLINEスタンプ」に切り替え。追加のセリフや尺は設けない。
- 音声は v7 の AAC を stream copy。映像終端を越えない最後の完全パケットまで保持し、音声終端は 39.531 秒。発話末尾は 38.933 秒で、セリフには影響しない。
- 概要欄は `shorts_description.txt`。本編リンクと実使用の音声・BGM・通知音クレジットを含む。

再実行（リポジトリルート）:

```bash
python3 03_SCRIPTS/youtube_line_stickers_20261015/build_shorts.py
python3 03_SCRIPTS/youtube_line_stickers_20261015/verify_shorts.py
```

依存関係は既存の本編・共有 Shorts Remotion プロジェクトを使用する。字幕なし中間映像と public hardlink、完成動画、監査画像は Git 管理外。

検証: 両 Remotion プロジェクトの TypeScript、全編デコード、解像度・フレーム数・尺・コーデック、元動画ハッシュ、元 v7 の対応区間と最終音声の圧縮 AAC ハッシュ一致を確認。先頭／末尾、全字幕カード、LINE／Outlook の表示待ち、最終 CTA を静止画で確認した。通し試聴・動画の主観的な動作確認は未実施。詳細は `shorts-audit.json`。

既存の Shorts pilot 配信記録・uploads・週次キューに本件の重複はなかった。今回の単発の予約公開は週次 5 本キューとは分け、YouTube 投稿記録で管理する。
