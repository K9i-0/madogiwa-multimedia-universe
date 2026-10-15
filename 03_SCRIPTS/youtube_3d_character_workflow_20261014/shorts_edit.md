# 本編誘導ショート

採用済み本編v6の冒頭1403フレーム（46.7667秒）＋案内90フレーム。全1493フレーム、49.7667秒、720×1280、30fps。

Wan解説版の `youtube_ai_video_workflow_20261013/remotion/src/shorts-entry.tsx` を継承。上部固定タイトル、中央の横画面、下部の名前28px・字幕38px、最後の笑顔2人と関連動画案内を維持。元の字幕レイヤーだけを隠して再描画し、顔や比較画像をクロップしない。

比較→Tripo実モデル→動作の実演までを使用。挨拶に入る直前で終了。会話音声は完成本編v6から使用。最後の案内部分には同じBGMの同時刻を接続し、発話終了後0.15秒でクロスフェード。新規音声生成なし。

再現：`remotion/`で `python3 render_shorts.py`。映像変更がなければ `--skip-render`。

本編：https://www.youtube.com/watch?v=hCWMw1nB43A
ショートは作成のみ。公開時はYouTube Studioで関連動画にこの本編IDを設定する（現時点でショートのアップロード・関連動画設定は未実施）。Studioへ別エピソードは作らない。

クレジットは `shorts_description.txt`。検証は `shorts_delivery.json`。静止画監査と音声の数値比較を実施し、通しの聴感確認は未実施。
