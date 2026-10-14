# 2026-10-15 ショート限定・たこさん音声差し替え

ユーザー指定により、たこさんをVOICEVOX 中国うさぎ・ノーマル（style61）、速度1.1、標準音高0へ変更。横版・投稿済みYouTube動画は変更しない。

- 新しい完成版: `final_remotion_shorts_usagi_9x16.mp4`
- 旧ショート: `final_remotion_shorts_9x16.mp4` を比較用に保持。
- 採用セリフ: エピソード直下の `shorts_takosan_usagi_*.wav`。
- 全生成クエリ: `shorts-usagi-queries.json`。前後無音 .09/.12秒、48kHz mono。
- 配置・音量・元ファイルハッシュ: `shorts-usagi-record.json`。
- 字幕と映像: `shorts-manifest-usagi.json`。720×1280、30fps、元の尺を維持。
- 環境音は既存の制作素材から復元。差し替え区間外のPCMは再エンコード前に完全一致を検証。
- 新音声の発音速度・音高を後から変更しない。元映像の演技は保持し、新音声との音素単位の同期は保証しない。
- 概要欄へ `VOICEVOX:中国うさぎ` を追加。

再生成: リポジトリ直下で `.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/shorts_queue_20261011/replace_takosan_usagi.py`。WAVがなければ保存クエリからローカルVOICEVOX Engineで生成。次に共有Remotionディレクトリで `node render_usagi.mjs`。
検証: `shorts-usagi-qa.json`、`shorts-usagi-asr.json`。全編デコード・尺・解像度・採用AAC一致・横版のSHA不変と字幕カード静止画を確認。人による通し試聴は未実施。

## 同日追加：ホログラム場面の声

ユーザー指定「たこさんの声に、電子的な響きや薄い残響を加える」。ホログラム全景の後半2セリフだけ、軽い42Hzリング変調、23/31msのステレオ遅延、RT60=0.42秒の薄い残響を追加。声の音高・速度・配置は保持し、発話中のRMSを元と揃えた。前半の窓際力測定の声は加工しない。

現行完成版は `final_remotion_shorts_usagi_hologram_9x16.mp4`。元の中国うさぎ版は保持。映像ストリーム完全一致、処理区間540〜754f外のPCM一致（再エンコード前）、横版のSHA不変、全編デコードを確認。主観的な通し試聴は未実施。

再現: `.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/80_sobaya_clone_lab/remotion/process_shorts_hologram.py`。設定は `remotion/src/shorts-hologram-audio.json`、結果は `shorts-hologram-audio-record.json` と `shorts-hologram-qa.json`。投稿待ち一覧はホログラム加工版へ更新。
