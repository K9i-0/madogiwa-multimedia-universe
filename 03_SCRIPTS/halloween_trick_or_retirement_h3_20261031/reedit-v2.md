# 話者対応を整理した編集 v2

依頼: 喋っているキャラの取り違えを編集で改善。

- H3の元映像は保持し、追加の動画生成は行わない。
- 台詞ごとにそば屋・やめ太郎・とーくんへ画角を切り替える。他キャラの口の動きを同時に見せない。
- クビ宣告はたこさんのリアクションに重ねる。「とーくん（声）」と明示し、元映像冒頭の誤ったマスク変形を避ける。
- そば屋の脅しと最後の台詞を正典参照から再生成。最後の「明日から」の重複を除く。
- 最後はたこさんの無言の視線で締める。話者名と共有メンバーカラーを字幕に付ける。
- 元のv1動画、編集manifestとRootを残す。v2の正本は `remotion/src/edit-manifest.json`。

## 音声

`generate_v2_voices.sh` で再生成可能。Irodori-TTS-v4-Large / seed42 / text CFG5 / duration scale1 / uncut。正典 `02_CHARACTERS/Sobaya_voice.wav` を参照し、`tools/sobaya_monsterize.sh` を適用。採用WAVはエピソード直下。差し替え区間では元音声を完全に外し、-18 LUFSを目標に調整する。他の台詞とチェーンソー音はH3原音。

## 再現

```sh
python3 prepare_edit_v2.py
cd remotion
npm run typecheck
node render.mjs video ../final_remotion_halloween_v2.mp4
```

生成480pから完成1280×720へ直接拡大、24fps。映像速度は変更しない。字幕は完成解像度で描画する。

## 確認範囲

画角・字幕の静止画確認、音声のASR補助確認、コンテナ仕様と終端までのデコードを実施する。口形自体の再生成・リップシンク修復ではなく、切り返しと音声差し替えによる編集。通し試聴と厳密な口形同期の検証は未実施。

書き出し結果: 33.458333秒 / 1280×720 / 24fps / H.264 + AAC 48kHz。終端までデコードエラーなし。全ショット中間の字幕と画角を確認。そば屋2台詞のASRは意図した文と一致。共通manifest validatorは単一inputVideo形式専用のため、この複数segment構成では独自の尺・クロップ・字幕範囲検証を使用。
