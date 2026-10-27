# ゆめテレ ビール盗難ニュース

Remotion 4.0.539。1280×720、24fps、276 frames（11.5秒）。時刻・局ロゴ・ニュース帯は src/edit-manifest.json が正本。

入力は ../generated/h3-job/results/video_720p.mp4 のhardlinkを public/input.mp4 に置く。CLIで480pからLanczos拡大済みであり、ここでは再拡大しない。sourceRangesで原本の[0,180)と[266,362)フレームを保持し、2回目の発話を映像・音声同時に削除する。H3生成音声は同じ区間を連結し32kHz AACへ再エンコードする。速度・ピッチは変更しない。

```sh
npm ci
npm run typecheck
npm run render
```

完成出力: ../final_remotion_news.mp4。生成原本: ../generated/h3-job/results/video_480p.mp4。
