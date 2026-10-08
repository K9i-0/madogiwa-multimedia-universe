# 制作時の引き渡し・採用実装

パスはリポジトリルート基準。2026-10-08採用版を出発点にする。

## 再利用元

- 現行の完成テンプレ：`03_SCRIPTS/youtube_aeron_chua_explainer_20261008/remotion/`
- 台詞：同ディレクトリの `dialogue.json`。初期の `scenario.json` / `editor.html` は古い叩きであり、完成動画の正本ではない。
- タイミング：`src/edit-manifest.json`。BGMの本編・終了開始、音声の実測尺、資料動画のsourceStartFrameとdurationInFramesを持つ。
- 最新音響方針：`mix_audio.py` とエピソード直下の `mix_record.json`。READMEやvideo_script.mdにある旧「会話後に音量を上げる」説明は採用前の履歴。現行は持ち上げなし。
- 中央の実装：`src/Explainer.tsx`、素材の由来：`center_assets.json` / `video_assets.json`。
- 立ち絵の準備・第三者素材：`03_SCRIPTS/youtube_explainer_pilot_20261008/remotion/prepare_assets.py` と同エピソードの `asset_sources.json`。
- エディター：`tools/scenario-editor/index.html`。最終調整時のみ使う。

これは実作品を参照するテンプレ。新作には必要なコード・設定を抽出し、題材固有の台詞・素材・view・旧manifest・完成動画を丸ごと持ち込まない。node_modulesやキャッシュも複製しない。元作品の上書きを避け、新作のpublicを素材正本から準備する。Remotionバージョン・依存関係・レンダー環境の扱いはremotion-videoに従う。

## VOICEVOX

採用時のエンジンは0.25.1、HTTPは `127.0.0.1:50021`。ローカル実行ファイルの例は `~/Applications/voicevox_engine/macos-arm64/run`。環境の有無・稼働状態を確認して再利用する。

| 話者 | スタイルID | speedScale |
|---|---:|---:|
| 四国めたん・ノーマル | 2 | 1.13 |
| ずんだもん・ノーマル | 3 | 1.15 |

`prePhonemeLength=.09`、`postPhonemeLength=.12`、出力24kHz。波形RMSで口差分を切り替え、まばたきと必要な驚き表情を加える。キャッシュは少なくとも話者・クエリ・エンジン版を識別し、台詞を変えたのに古いWAVを使うことを防ぐ。既存prepare_voice.pyは題材専用の読み・終了条件を含むため、新作へそのまま適用しない。

発音用と表示用を分ける例：`CTO`→発音「シーティーオー」、`AERON CHUA`→発音「アーロンチュア」。出力されたかなを確認し、固有名詞をチェックする。字幕の2行分割は既存コードの句読点分割だけで済ませず、禁則・意味の切れ目・長文を確認する。

既定の発話間は9フレーム/30fps。オチ・反応では15〜42フレーム程度が今回の例で、内容に応じて調整する。数字を全台詞へ機械的に固定しない。

この二人は今回ユーザーが指定したVOICEVOX配役。窓際族メンバーの新しいセリフまでVOICEVOXへ置き換えない。元動画は採用原音を利用し、メンバーの新規音声が必要なら `02_CHARACTERS/VOICE_CAST.md` と該当制作経路を参照する。

## 採用音量の出発点

| 対象 | ラウドネス目標・処理 |
|---|---|
| 解説音声 | -18 LUFS |
| 導入・本編BGM | -34 LUFS |
| 原音付き資料クリップ | -19 LUFS、解説停止、BGMを下げる |
| Unity | -38 LUFS。会話終了後も持ち上げなし |
| 本編→Unity | 2秒クロスフェード |
| Unity末尾 | 4秒フェードアウト |

ミックス48kHzステレオ。これは素材ごとの目標値であり、完成動画全体のLUFSではない。今回のBGMは曲全体のloudnorm処理後に使う範囲を切っているので、選択範囲の実測LUFSは目標値と必ずしも一致しない。曲や区間を変えたら、短時間の音量・ピーク・声との関係を確認する。

エンディングは曲の先頭から使用した。既定の意図は終了の合図であり、ドロップに合わせた急な盛り上げではない。本編曲が足りない場合は繰り返し接続を短くクロスフェードする。最後は二人の会話→静かな余韻→フェードアウト。

## 音源・クレジット

- 昼下がり気分／KK：`https://opentracks.com/bgm/detail/4695`
- ほのぼのワルツ【リコーダー】／エクシエ：`https://commons.nicovideo.jp/works/nc116360`
- Unity：`https://www.thefatrat.com/release/unity`、採用取得先・hashは `03_SCRIPTS/youtube_aeron_chua_explainer_20261008/unity_source.json`。
- VOICEVOX:ずんだもん、VOICEVOX:四国めたん、立ち絵：坂本アヒル。
- 実際の説明欄は同エピソードの `youtube_description.txt` を元に、使用した素材だけ残す。

Unityは公式配布の音源を使い、利用前に公式の現行条件を確認する：`https://www.thefatrat.com/terms-and-conditions` / `https://www.thefatrat.com/copyright`。2026-10-08確認時は通常のYouTube動画での利用・収益化をクレジット条件で案内している。広告・ゲーム等も無条件に使える素材として扱わない。概要欄には少なくとも以下を入れる。

```text
Music: TheFatRat - Unity
Watch the official music video: https://www.youtube.com/watch?v=n8X9_MgEdCg
```

第三者音源・配布PSD・試作WAV・完成動画は既存のGit方針に従いローカル保持。スキルへバイナリを同梱しない。音源が不足しているときは別曲へ勝手に差し替えず、公式に取得可能なら取得し、取得できない場合は不足を伝える。

## 改修時の最小工程

- 台詞変更：該当音声を生成、実測尺と字幕・資料動画・BGM開始フレームを更新してremotion-videoで再編集。
- 中央素材だけ：音声は維持。顔と物体が見えるフレームで視覚監査してから再レンダー。
- BGM音量だけ：映像stream copy、音声のみ再ミックス。映像ストリーム不変・尺・全編デコードを確認。
- エンディング：全編と約30秒程度の確認用抜粋を出す。主観的な聞きやすさを機械的なデコード成功だけで保証しない。
