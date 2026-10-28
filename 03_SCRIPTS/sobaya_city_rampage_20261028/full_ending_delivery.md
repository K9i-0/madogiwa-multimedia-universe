# THE SOBAYA — ラスト復元版

ユーザー依頼: 飲酒のこぼれを許容し、カットした末尾を復元。通常版とShortsのファイル準備のみ。投稿・公式サイト変更は行わない。

- 通常版: `final_sobaya_full_ending_30s_16x9.mp4`（1280×720）
- Shorts: `final_remotion_full_ending_30s_9x16.mp4`（720×1280）
- 30秒・30fps・900フレーム。従来28.2秒版から54フレーム（1.8秒）復元。
- 27〜30秒は採用済み `wan3_v8_drink_native720p.mp4` の3秒全体。空中移動の既存編集は維持。
- 直近No BGM版の方針を継続し、序盤を含め生成音声を使用。音量-8.13dBとピークリミッターを維持。後付けBGMなし、末尾の映像カット・フェード・速度変更なし。
- Shortsは既存THE SOBAYAタイトル＋同期ぼかし背景の共有Remotion実装。通常版のAACをそのままmuxする。
- 旧版・既存投稿記録は保持。

再現: `python3 render_full_ending.py` → `node render_shorts_full_ending.mjs`。
