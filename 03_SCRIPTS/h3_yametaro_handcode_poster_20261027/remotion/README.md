# 喋るポスター

`npm ci && npm run typecheck && npm run render`。
`src/edit-manifest.json`が章タイミング・顔の合成範囲・出力寸法の正本。元画像1086×1448を保持し、480×640の生成動画の顔を一度だけ拡大してフェザー合成する。元ポスターの文字・背景・商品は固定。音声はH3生成の各章をそのまま連結、速度・ピッチ変更なし。

render.pyは ../generated/h3-job/results/ から動画をpublicへhardlinkし、画像をコピーする。映像はRemotion、音声連結とmuxはffmpeg。出力 ../final_remotion_talking_poster.mp4。

顔の位置補正は ../align_face.py（uv run --with opencv-python-headless --with numpy python ../align_face.py）で生成する src/face-transforms.json を使用。元画像の上半顔のSIFT特徴から相似変換をRANSAC推定し、9フレーム平滑化。RemotionのVideoへ変換を適用し、口元と顎のフェザーマスクで合成する。変換は元480pから完成寸法への描画時に適用し、中間拡大動画は作らない。
