# ゆめみん版 効果音3パターン

共通：ゆめみん単独・追加字幕なし・20.133秒・1080p。ナレーション原音と映像を共通にし、音の方向だけ比較。元映像のストリームコピーで全3版と原版の映像packet SHA256一致を確認。全編デコード、TypeScript、PCMピークを検証。実際の試聴は環境上未実施。

| 版 | 演出 | 出力 |
|---|---|---|
| 無駄に意識高い | 音楽的な決定音、ガラス音、繰り返す大げさな拍手。15キュー | final_remotion_yumemin_keynote.mp4 |
| お笑い | コミカルな短音・スクラッチ・サックスの合いの手・観客の笑い声。17キュー | final_remotion_yumemin_comedy.mp4 |
| 激しめ | ヒット、レーザー、パワーアップを密に配置。21キュー | final_remotion_yumemin_intense.mp4 |

効果音単体のピーク目標は−17〜−10 dBFS。旧控えめ版の−24〜−19 dBFSから強化。ナレーションは速度・音高・ゲインを維持。最大PCMピークは意識高い−6.39／お笑い−5.04／激しめ−3.91 dBFS。

比較プレイヤー：`compare-sounds.html`。再生位置を維持して3版と効果音なしを切り替え可能。

## 再現

- `remotion/prepare_sound_variants.py`：素材選定・フレーム配置・PCM合成・映像コピー書き出し。
- `remotion/src/sound-*-manifest.json`：配置とゲイン。
- Remotion `YumemiSound-keynote` / `YumemiSound-comedy` / `YumemiSound-intense` でプレビュー・再編集可能。
- 使用する加工済み素材：`remotion/public/sfx_variants/`。ソースの採用箇所を短く抜粋し、トリム・フェード・音量調整。
- 全素材の元パス・SHA・ピーク監査：`sound-variants-audit.json`。

## 素材クレジット（公開時は概要欄へ）

- Kenney「Interface Sounds」「Music Jingles」「Digital Audio」、CC0 1.0。抜粋・音量・フェード調整。
  - https://kenney.nl/assets/interface-sounds
  - https://kenney.nl/assets/music-jingles
  - https://kenney.nl/assets/digital-audio
  - https://creativecommons.org/publicdomain/zero/1.0/
- 拍手：Amada44「Sound Effects - Applause after a concert」、CC0 1.0。抜粋・音量・フェード調整。
  - https://commons.wikimedia.org/wiki/File:Sound_Effects_-_Applause_after_a_concert.ogg
- 笑い声：Kyster「big crowd laughter.wav」、CC BY 4.0。抜粋・音量・フェード調整。
  - https://freesound.org/people/Kyster/sounds/124028/
  - https://creativecommons.org/licenses/by/4.0/

拍手と笑い声は第75話の出典記録・取得済み素材を再利用。映像内クレジットは追加しない。
