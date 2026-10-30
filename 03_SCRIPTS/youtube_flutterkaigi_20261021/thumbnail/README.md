# YouTube thumbnail — 2026-10-31

採用タイトル：この3Dゲーム、Flutter製です。Flutter Sceneで作る「ゆめみ採用試験」

- 完成：thumbnail_final.png（1280×720）
- 装飾＋文字＋キャラクターの透過レイヤー：thumbnail_overlay.png（1280×720）
- キャラクター単体：zundamon_overlay.png（内蔵image_gen、透過PNG）
- 実録画フレーム：game_capture.png。remotion/public/game_odatetsu_closeup_v11.mp4 の9.2秒。ゲーム画像は生成AIへ入力していない。再描画・補完なし。
- 構成：背景 #102335、ゲーム画像を x=150,y=201,w=1130,h=519 へ縮小配置、透過レイヤーを上に置く。元ゲームの縦横比をほぼ維持。左端の端末ノッチはずんだもんと背景装飾の下になる。
- 文字：「これ、Flutter!?」「Flutter Scene × 3Dゲーム」。ロゴは使っていない。
- ずんだもん参照：remotion/public/zunda_surprise_1.png。入力プロンプト：prompt_zundamon.txt。生成は内蔵image_genを使用、ゲーム画像と正確な文字はRemotionで合成。
- 再生成：remotionで node render_thumbnail.cjs。編集元はsrc/Thumbnail.tsx。

完成画像と透過レイヤーを原寸で確認。タイトルの可読性、キャラクターの顔・指、ちくわ・ゲームキャラクターが見えることを確認。投稿は未実施。
