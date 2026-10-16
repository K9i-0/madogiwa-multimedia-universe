# 廃村Y村の飲み会 — Remotion

1280×720 / 30fps / 61,389 frames。字幕492枚、VOICEVOX488クリップ、60ショット。

```sh
npm ci
python3 build_edit.py
# NumPy, SciPy, SoundFile installed in the project Irodori venv:
../../../.local/Irodori-TTS/.venv/bin/python build_audio.py
npm run typecheck
python3 render.py
```

音声再生成：VOICEVOX 0.25.1をlocalhost:50021で起動し `prepare_voice.py`。
シルエット再生成：`uv run --with 'rembg[cpu]' --with pillow python prepare_silhouettes.py`。
白背景プレビューは `out/`。入力元とクロップは `../silhouette-sources.json`。

`public/mix.wav` は再構築可能な確認ミックス。BGMはリポジトリに格納しない参照動画の分離音で、`../../../.local/y-village-horror/separated/htdemucs/music_sample/no_vocals.wav` が必要。曲名と配布元が判明したら同曲のマスターへ置換し、映像はstream copyで再muxできる。無断で別曲へ切り替えない。

公開先へのアップロードは行っていない。v2納品名は `../review_remotion_horror_aoyama_v2.mp4`（`../review_remotion_horror.mp4`と同内容）。BGMと通し聴感を確認した採用版は `final_remotion_horror.mp4` にする。

ナレーション：VOICEVOX:青山龍星（標準速度1.0、標準音高0）。全て投稿者が引用する一人語り。声質・演技の人間による通し試聴は機械検査と別扱い。

音声改訂版は `public/voice_aoyama/` を使用。そばやの主観音 `../sobaya_beer.wav` を初登場直後に一度挿入。`public/voice/` は玄野武宏の旧版。
