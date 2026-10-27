# ゆめテレ ビール盗難ニュース

Remotion 4.0.539。1280×720、24fps、362 frames。時刻・局ロゴ・ニュース帯は src/edit-manifest.json が正本。

入力は ../generated/h3-job/results/video_720p.mp4 のhardlinkを public/input.mp4 に置く。CLIで480pからLanczos拡大済みであり、ここでは再拡大しない。H3生成音声を維持する。

```sh
npm ci
npm run typecheck
npm run render
```

完成出力: ../final_remotion_news.mp4。生成原本: ../generated/h3-job/results/video_480p.mp4。
