# 廃村Y村の飲み会 — Remotion

1280×720 / 30fps / 49,040 frames。字幕491枚、VOICEVOX488クリップ、60ショット。

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

公開先へのアップロードは行っていない。現時点の出力名は `../review_remotion_horror.mp4`。BGMと通し聴感を確認した採用版は `final_remotion_horror.mp4` にする。

ナレーション：VOICEVOX:玄野武宏。全て投稿者が引用する一人語り。声質・演技の人間による通し試聴は機械検査と別扱い。
