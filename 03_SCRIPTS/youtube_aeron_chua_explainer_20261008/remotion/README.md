# アーロンチュア解説・動画初稿

1280×720 / 30fps。Remotion 4.0.534（同セッションで検証済みのパイロットと同一版）。

1. `npm ci`（ローカル検証環境では既存パイロットのnode_modulesをsymlinkで共有）
2. `python prepare_assets.py`：既存パイロットの立ち絵・音楽・原作画像、DIY元動画、チュアゴスティーニ採用動画を準備。
3. VOICEVOX 0.25.1を127.0.0.1:50021で起動して `python prepare_voice.py`。Python依存はrequests/numpy。既存venvはルートの `.local/voicevox-explainer/venv`。
4. `npm run typecheck` / `npm run render`。完成版は `../final_remotion_aeron_chua.mp4`。

制作版台詞は `dialogue.json`、音声実測に基づく整数フレームは `src/edit-manifest.json` が正本。音声はクエリhash付きファイル名でキャッシュし変更時の取り違えを防ぐ。CTOのみ発音用表記と表示用表記を分ける。字幕は2行以内。

既存BGMを声-18 LUFS / 音楽-34 LUFSで配置。本編曲の繰り返しは1秒クロスフェード。資料動画3本の間は解説を停止、BGMを下げ、原音を-19 LUFS目標で混合。映像中の元音声はmutedで二重再生を防止。

原音素材と試作TTS、public/out/node_modulesはGit除外。版の検討はチャットで行い、編集HTML・scenario.jsonは最終調整まで更新しない。素材クレジットは `../youtube_description.txt`。

中央素材の改訂：`center_assets.json` に正典写真・採用小道具・公式商品画像・動画からの切り出し位置を記録。各発話のviewで対応するレイアウトを指定し、未定義viewはエラーにする。よーたんは写真をCSSで上半身表示。原作第1話は文字入れとビールをそれぞれ拡大し、語りの対象が見えるようにする。
