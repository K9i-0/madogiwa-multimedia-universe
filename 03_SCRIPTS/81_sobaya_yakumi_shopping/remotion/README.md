# そば屋の買い出し 完成編集

`npm ci` → `npm run typecheck` → `npm run render`。

Composition: `SobayaYakumi`。出力: `../final_remotion_yakumi_call_crop.mp4`。
`src/edit-manifest.json`の900フレーム新規素材＋137フレーム既存連行映像を接続する。
`public/input.mp4`は`../wan3_yakumi_seed810925_480p.mp4`、`public/ending71.mp4`は第71話の字幕なしWan原本のhardlink。動画はGit対象外のため別環境では元素材が必要。

生成上の差異・音声確認の限界はエピソードの`script.md`を参照。

現行コードは通報シーン[564,775)の左上基準1.255882倍トリミングを含む。旧採用版`final_remotion_yakumi.mp4`は保持。

## Shorts試作（2026-10-11）

`npm run render:shorts` → `../final_remotion_shorts_9x16.mp4`。
`src/shorts-manifest.json`が縦版の字幕タイミング正本。既存横版の設定は維持。
入力`public/story-source.mp4`は採用横版とSHA-256一致。
720×1280、30fps、1037フレーム。上下は本編をぼかした背景、上部コピー、下部に話者と字幕。
本編領域720×480への軽い左右クロップで人物を拡大。映像・音声の速度や構成は変えない。
音声はレンダー後に採用横版からストリームコピーし、二重再生を防ぐ。
日本語フォントはmacOSのHiragino Sans。別環境での再現には同フォントが必要。
音声のPCM一致と全編デコードを確認。字幕の精密な聴覚同期監査は未実施。
