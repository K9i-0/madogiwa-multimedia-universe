# 廃村Y村の怪異S — 仮面篇

2026-10-24の「10分以内・ボケを減らす・禁じられた部屋の仮面を壊す」改稿から制作した短編。旧・飲み会の呪い版は `../y_village_drinking_horror_20261017/` に保持する。

- 完成動画：`final_remotion_horror.mp4`（`review_remotion_horror_mask_v1.mp4` と同一内容）
- 9分16.267秒 / 1280×720 / 30fps / stereo AAC 48kHz
- 本文：`script.md`、実測時刻：`timing.md`
- ナレーション：VOICEVOX 青山龍星・ノーマル、速度1.0、音高0、抑揚0.85。114発話。早回しなし。
- そばや「かえして」「こっち、むいて」とF先生の警告・偽の終了宣言のみ正典Irodori音声。F先生の読経も同じ正典参照から生成。
- BGM：KK「不安、恐怖、戦慄」。参考動画 `xGBpa1njZPA` と同曲。曲の出典、実際の取得元、照合記録は `music-source.json`。
- 48カット・120字幕。新規画像は組み込みimage_gen。全プロンプト・参照元は `remotion/imagegen.json`。M/Y/Fの影は旧版の写真・正典画像加工素材を再利用。YはRemotion内で上半身を切り出す。

## 再生成

リポジトリルートから。VOICEVOXは `http://127.0.0.1:50021`、共有読み辞書は `voicevox-control` スキルを利用する。採用WAV・生成時AudioQuery・読み補正を保存している。

```sh
python3 03_SCRIPTS/y_village_mask_horror_20261024/remotion/prepare_voice.py
python3 03_SCRIPTS/y_village_mask_horror_20261024/remotion/build_edit.py
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/y_village_mask_horror_20261024/remotion/build_audio.py
```

音楽原音は `.local/y-village-mask-horror-20261024/music/kk_fuan_kyofu_senritsu.wav`。外部楽曲単体をGitで再配布しない。公式トラック動画 `WvtIo0CnGRc` のAACを取得し、FFmpegで48kHz stereo WAVへデコードした。OpenTracksのMP3配信エンドポイントはHTTP403だったため、サイトがリンクする公式トラック動画を使用。朗読入り参考動画からの分離ではない。

```sh
cd 03_SCRIPTS/y_village_mask_horror_20261024/remotion
npm ci
npm run typecheck
python3 preflight.py
npm run render
```

RemotionとCLIは当日安定版4.0.538へ固定。字幕・画・音のタイミングは `src/edit-manifest.json` の整数フレームを正本とする。

## 演出と監査

仮面破損、最初の遭遇、帰宅後、タオル、儀式で段階的に距離を詰める。同じ息遣いを遠方と耳元で反復。自宅の「足音はしませんでした」の場面へ足音を追加しない。儀式ではF先生の唱える声を残し、同じ声の終了宣言を右耳へ近づける。最後は解呪後の記憶への恐怖とし、怪異の再登場を加えない。

字幕・読み・尺・画像の対応、全編デコード、音量、採用台詞のASR照合を検査する。人の耳による全編通し試聴、声質と演技の聴感判定は未実施で、ASR一致をその代わりにはしない。具体的な結果は `review.md`、`video-audit.json`、`audio-review.json`、`voice-asr-review.json` を参照。

概要欄用のクレジットは `youtube-description.txt`。投稿や公開は行っていない。
