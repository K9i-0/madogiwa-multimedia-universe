# VOICEVOX解説 検証版

1280×720、30fps、75.3秒。坂本アヒル式ずんだもん2.3・四国めたん2.1。波形連動の口パク、まばたき、大きな原作漫画、話者別の縁取り字幕。導入から本編へのBGM切り替えを確認する。

## 再現

- `npm ci` / `npm run typecheck`
- Python依存: requests, psd-tools, pillow, numpy。
- 配布素材の原本はリポジトリルートの `.local/voicevox-explainer/` にローカル保持。立ち絵ZIPは作者配布ページで入手して `zunda/`・`metan/` に展開。導入曲Track1は `intro.mp3`。
- `python prepare_assets.py` でPSD差分と原作漫画を `public/` へ配置。
- VOICEVOXを127.0.0.1:50021で起動し `python prepare_voice.py`。既存WAVを再利用するため、台詞変更時は該当WAVを別名退避して生成し直す。
- `npx remotion render src/index.ts Explainer out/visuals.mp4 --codec=h264 --concurrency=2 --muted --props='{"omitMainMusic":true}' --overwrite`
- `python mix_audio.py --main /path/to/ほのぼのワルツ.wav`。本編クレジットを含むRemotion映像を再レンダーしてミックスする。
- 今回のローカル環境では `npm run render` で `../input/` の唯一のWAVを自動選択して再現可能。
- 納品先: `../final_remotion_explainer_pilot_facing.mp4`。Remotion映像に確定フレーム位置で音声合成。音源の代理曲への自動置換はしない。

各音源の利用条件・URLは `../asset_sources.json` と `../youtube_description.txt`。第三者素材の再配布を避け、public・原本・試作音声・レンダーはGit管理しない。
