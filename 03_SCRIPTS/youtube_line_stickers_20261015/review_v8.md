# 字幕訂正とX用横動画（2026-10-16）

v7の `intro-08` にある表示字幕「移動らしいわ…」を「異動らしいわ…」へ訂正した。台本、字幕SRT、caption layout、Remotionの表示文字列、Shorts字幕を同期。音声の実生成入力・ASR書き起こしは履歴として維持し、同音のため再生成していない。

- 本編：`final_remotion_line_stickers_v8.mp4`、1280×720、30fps、20440フレーム。
- ショート：`final_remotion_shorts_9x16.mp4`、720×1280、30fps、1186フレーム。
- X用：`final_remotion_x_opening_16x9.mp4`、1280×720、30fps、1186フレーム（39.533秒）。ショートと同じ冒頭からPythonのツッコミと余韻まで。元の横画角と字幕レイアウトを使い、縦版のタイトル枠は追加しない。

本編とX用はRemotionから再レンダーし、v7のAACをストリームコピー。横・縦の抜粋は同一の完全AACパケット列を使う。本編の全107発話・音声・フレーム時刻・演出は変更していない。元v7と修正前のショートは保持。

再現：`python3 03_SCRIPTS/youtube_line_stickers_20261015/build_caption_fix_v8.py main`、同じコマンドの `x`、および `build_shorts.py --skip-clean-render`。字幕なしの冒頭素材には訂正前後の字幕自体が含まれないため、そのまま再利用できる。

検証コマンド：`verify_caption_fix_v8.py` と `verify_shorts.py`。基準コミットは `d49cbdab`。表示文字以外のmanifest差分がないこと、映像全体のデコード、尺・解像度・フレーム数、音声パケット一致を確認する。検査結果は `caption_fix_v8.json`、`shorts-audit.json`。

YouTubeは同じIDへ動画本体を差し替えられないため、新IDの修正版へ19:00の公開予約を引き継ぐ。旧IDの予約は解除し、非公開で保持する。現在のID・処理・予約状態は `youtube_upload.json` と `youtube_shorts_upload.json`、旧版は `*_superseded.json` を参照。本編URLに依存するショート概要欄とX返信用テキストも更新する。

Xには投稿せず、投稿用MP4と本編URLを納品する。主観的な通し試聴は行わず、元音声の圧縮データの一致で保全を確認する。
