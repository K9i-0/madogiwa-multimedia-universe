# ゆめみん単独・効果音試作

ユーザー指定：ゆめみん単独版を採用方向とし、合う効果音を任せて試作。

- 映像・ゆめみん・アナウンサー・追加字幕なしは単独版を継承。
- BGMは追加せず、場面切替、いいね数、活動項目、グッズ、最後のコピーへ計13個の短い音を配置。
- 素材：Kenney Interface Sounds（CC0 1.0）。`open_002`、`pluck_001`、`pluck_002`、`confirmation_001`、`confirmation_002`。
- 配置とゲイン：`remotion/src/solo-sfx-manifest.json`。元動画上のフレームから速度変更後の整数フレームへ換算。
- SFXのピークは−24〜−19 dBFS、最終PCMミックスの最大ピーク−6.66 dBFS。ナレーションを一定のまま維持し、効果音を小さめに配置。
- 出力：`final_remotion_yumemin_sfx.mp4`、20.133秒、1920×1080、30fps。
- 画は映像ストリームコピー。単独版と映像packet SHA256が一致、意図しない画質・フレーム変更なし。全編デコードとTypeScript検証に合格。
- 音声は既存完成版AACからデコードして効果音を加算、48kHz stereo / AAC 320kbpsで書き出し。
- 音量・タイミングは機械検証済み。実聴不可のため聴感はユーザー試聴待ち。

## 再現

`remotion/prepare_sfx.py` で同じPCMミックスと映像コピー出力を再現。選定済みOGGとLicenseは `remotion/public/sfx/`。
Remotion上で再編集・プレビューする場合はcomposition `YumemiSoloSfx`（`SoloSfx.tsx`）。

## 概要欄用クレジット

効果音：Kenney「Interface Sounds」／CC0
https://kenney.nl/assets/interface-sounds
https://creativecommons.org/publicdomain/zero/1.0/

取得元・SHA：`sfx-sources.json`。元ZIP・未使用素材は `.local/yumemi_evolution_20261026/sfx/` に保持。
