# 廃村Y村の怪異S — Remotion

1280×720 / 30fps / 44,492 frames / 24:43.067。字幕373枚、VOICEVOX372クリップ、138ショット。

```sh
npm ci
# VOICEVOX engine must be available for changed speech:
python3 prepare_voice.py
../../../.local/Irodori-TTS/.venv/bin/python prepare_horror_sound.py
python3 prepare_monkey.py
python3 build_edit.py
# NumPy, SciPy, SoundFile installed in the project Irodori venv:
../../../.local/Irodori-TTS/.venv/bin/python build_audio.py
npm run typecheck
python3 preflight.py
python3 render.py
python3 audit_video.py
python3 audit_final_frames.py
```

音声再生成：VOICEVOX 0.25.1をlocalhost:50021で起動し `prepare_voice.py`。
シルエット再生成：`uv run --with 'rembg[cpu]' --with pillow python prepare_silhouettes.py`。
白背景プレビューは `out/`。入力元とクロップは `../silhouette-sources.json`。

`public/mix.wav` は再構築可能な確認ミックス。BGMはリポジトリに格納しない参照動画の分離音で、`../../../.local/y-village-horror/separated/htdemucs/music_sample/no_vocals.wav` が必要。曲名と配布元が判明したら同曲のマスターへ置換し、映像はstream copyで再muxできる。無断で別曲へ切り替えない。

公開先へのアップロードは行っていない。v7納品名は `../review_remotion_horror_aoyama_v7.mp4`（`../review_remotion_horror.mp4`と同内容）。BGMと通し聴感を確認した採用版は `final_remotion_horror.mp4` にする。

ナレーション：VOICEVOX:青山龍星（標準速度1.0、標準音高0）。全て投稿者が引用する一人語り。声質・演技の人間による通し試聴は機械検査と別扱い。

使用する採用音声は `voice-manifest.json` に記録（voice_aoyama、voice_aoyama_v3、voice_aoyama_v4、voice_aoyama_v5、voice_aoyama_v6、voice_aoyama_v7）。そばやの主観音 `../sobaya_beer.wav` を儀式での明瞭な登場直後に一度挿入。`public/voice/` は玄野武宏の旧版。


v4のリアル頭身の影と衣装詳細は `uv run --python 3.11 --with 'rembg[cpu]' --with pillow python prepare_feedback_assets.py` で再現。ネタ追加と読み修正は `dialogue-source.json` と `prepare_voice.py`。祠の追加音声は `../sobaya_early_murmur_v4.wav`。

短い仕事画面は `src/WorkInsert.tsx`。CC0の三種類の猿まね音声は `prepare_monkey.py`、出典は `../monkey-audio-source.json`。画面確認は `node audit_stills.cjs`、最終デコード・音量・抜粋は `python3 audit_video.py`。監査の所見と聴感未確認は `../review-v7.md`。


v6は通常の追加間隔0.3秒を基本に、発見・返答待ちを個別指定。`soundRegions` が音楽、室内音、静寂を管理する。全カット共通の自動拡大は廃止。録画内の本人台詞5箇所だけ同じ音源を狭帯域へ加工する。画像6枚の制作入力は `imagegen-v6.json`。旧版の動画・ローカルバックアップは上書きしない。

`audit_final_frames.py` はPillowが必要。リポジトリの `.local/voicevox-explainer/venv/bin/python` で実行可能。フレーム抽出と音量・読みの機械検査は、人間の全編通し試聴の代替ではない。


v7は `glimpseFrame`（祠の月明かり）と `revealFrame`（儀式の明瞭な登場）を別管理。姿は呪われた人の主観とその回想でのみ表示し、録画や第三者の視点には入れない。新規画像は `imagegen-v7.json`。猿まねは実際の動物の声ではなく、CC0で配布された人の実演3種類を使う。旧素材・旧動画は保持。
