# Imagegen foreground thumbnail candidates

2026-10-31。ユーザー指定：窓際族物語の紹介サムネと同様、ずんだもん・めたん・文字・装飾をすべてImagegenで生成。背景ゲームだけ実画像。

参考：youtube_project_intro_20261019/thumbnail/thumbnail_project_intro_v3.png、ずんだもん・めたんの本編立ち絵。内蔵image_genで独立に3枚生成。入力全文はprompt_a/b/c.txt。ゲーム画面は生成モデルへ渡していない。

- A：紹介サムネに近い驚き顔＋めたんの解説ポーズ。
- B：指さし・手のひらでゲームへ誘導する動的な構図。
- C：ウインク＋「Flutter Scene × 3Dゲーム」のラベル。

完成はthumbnail_a/b/c.pngと.jpg。比較はcomparison.jpg。透過生成原本はoverlay_a/b/c.png。候補素材と生成出力はローカル保持、選定後に採用入力を追跡する。
合成：プロジェクトの .local/voicevox-explainer/venv/bin/python で compose.py を実行。背景../game_capture.pngを通常リサイズ・クロップするだけで、描き直し・補完なし。端末ノッチはクロップで除外。文字は後付けフォントで作り直していない。
出力1280×720。透過alphaあり、3案の日本語・英語表記、両キャラの識別、ゲームの視認性を目視確認。YouTube投稿なし。
