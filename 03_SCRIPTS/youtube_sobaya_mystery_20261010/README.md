# めたんのミステリー研究所：SOBAYA

## 現行版 v3

ユーザーFB（2026-10-10）に基づく改稿。11分15.433秒、1280×720・30fps、128発話。

- 完成動画：`final_remotion_sobaya_mystery_v3.mp4`（ローカル保持）。初稿 `final_remotion_sobaya_mystery.mp4` は比較用に保持。
- 正本台本：`script.md`。表示・発話・間：`remotion/dialogue.json`。
- 整数フレームのタイミング：`remotion/src/edit-manifest.json`。
- 字幕：`subtitles_ja.srt`。チャプター：`chapters.txt`。
- 新画像・プロンプト・UMAの参照先：`research_sources.md` と `inputs/`。

### 改稿内容

ツッコミの連打を減らし、ずんだもんは観察・質問を中心に研究へ付き合う。辛辣さは再生による検証、配線の隠蔽、そば屋の欲張りと待機生活、正体判明、宇宙の未解明部分に集中させる。

image_genでビッグフット・イエティの想像復元、地下保存装置の仮説復元、解析作業の再現図を生成。採用画像4点と実際のプロンプトは `inputs/*_v3.png` と `inputs/imagegen_v3_prompts.json`。霜重の読みは「しもしげ」。

正体判明前は「ソバヤ」／研究資料では「SOBAYA」。大柄な輪郭、仮面状の顔面構造を説明し、全身紹介は黒いシルエットを使用する。終盤まで「そば屋」「クローン」「ビール」を台詞に出さず、クリーンなエピソード映像も見せない。

目撃映像は手ぶれ・遮蔽・低帯域の映像、遺跡の映像は固定観測カメラの走査線・ノイズとして再編集。クローン研究施設を旧文明の遺跡、窓を古代の門として解説する。編集前の素材は変更しない。

広域未確認生物研究所、狭間文明研究所、木村・林・霜重研究員、未確認ニュースネットは架空。間違った推論、初歩的な確認の欠落、訂正時の言い訳を、めたんが真顔で紹介する。ビッグフット・イエティの一般的な伝承説明と、本番組の珍説を区別する。

終盤で人事部の連絡と鮮明な映像を見せ、表記を「そば屋」に切り替える。「呼び名は最初から合っていた」が追加のオチ。

## 再生成

VOICEVOX 0.25.1を `127.0.0.1:50021` で起動。

```sh
cd 03_SCRIPTS/youtube_sobaya_mystery_20261010/remotion
npm ci
../../../.local/voicevox-explainer/venv/bin/python prepare_assets.py
../../../.local/voicevox-explainer/venv/bin/python prepare_evidence.py
../../../.local/voicevox-explainer/venv/bin/python prepare_voice.py
npm run typecheck
npm run render
../../../.local/voicevox-explainer/venv/bin/python check_output.py
```

Remotion 4.0.534固定。前作からの立ち絵とローカルの原本動画を使用。画像生成は内蔵image_genによる参照付き生成。採用シルエットはGit管理の `inputs/sobaya_silhouette_v2.png` から復元できる。

音声はVOICEVOX:四国めたん／ずんだもん。採用設定は `production_record.json`。環境音楽は自作アンビエント、`mix_audio.py` で再現する。元動画の音声は再生せず、解説とBGMを配置する。

`public/`、`out/`、node_modules、生成動画はGit対象外。旧版の画面・音声はローカル保持、コードはGit履歴の `5138e2fa` から参照できる。

## 検証

全種類のレイアウトと証拠映像、正体判明前後の切替を実フレームで確認する。機械検査では128発話の存在、WAV実測尺、字幕長、時刻の整合、正体判明前の語彙、完成動画のフレーム数と終端までのデコードを確認。

音声の通し試聴は利用可能な手段がなく未実施。機械的な音声検査と区別する。結果は `qa_record.json` と `production_record.json`。
