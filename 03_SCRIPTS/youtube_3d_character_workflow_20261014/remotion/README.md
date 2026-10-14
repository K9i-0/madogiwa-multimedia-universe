# Tripo制作解説・完成版v6

たこさん＆やめ太郎の技術解説。1280×720 / 30fps、20,832フレーム、694.4秒（11分34.4秒）。99台詞・138字幕ページ。正本のセリフと絵の対応は `src/edit-manifest-v6.json`、制作原稿は一つ上の `script.md`。

## 再現

以下のコマンドはこの `remotion/` ディレクトリで実行する。全編をレンダーする経路：

```sh
npm ci
python3 prepare_assets.py
../../../.local/voicevox-explainer/venv/bin/python mix_audio_v2.py --manifest src/edit-manifest-v6.json --output public/mixed-v6.wav --record ../mix_record_v6.json
npm run typecheck
node render_v6.cjs stills
node render_v6.cjs short
node render_v6.cjs full
```

`prepare_assets.py`はリポジトリ内の正本とローカル保持映像をSHA-256照合し、publicへ相対symlinkを張る。生成済みの採用音声はエピソード直下。外部ストレージからの動画復元が必要な環境では、不足ファイルを明示して止まる。

映像とミックス済み音声を完成MP4へまとめる：

```sh
ffmpeg -y -i out/visuals-v6.mp4 -i public/mixed-v6.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -movflags +faststart ../final_remotion_tripo_workflow_v6.mp4
```

既存の `out/visuals-v5.mp4` がある場合は、全編レンダーと上のMP4結合の代わりに、変更のない先頭部分を無劣化で再利用できる。音声ミックスは先にv6として作成する。

```sh
node render_v6.cjs tail 19429
python3 assemble_v6.py
```

先頭19,429フレーム（10分47.633秒）の映像を再利用し、第8章の開始・進捗表示（19,481フレーム）より前のIDRから末尾まで描き直す。`assemble_v6.py`は旧版と同じ台詞・音声・字幕・開始位置を照合し、映像とv6音声を結合する。再利用した全19,429フレームのデコード後ハッシュ一致と、完成映像の全表示時刻が30fps間隔で連続することを検証し、`../render_reuse_v6.json`へ記録する。旧版の音声・ミックス・レンダー・ソースには上書きしない。

公開・アップロード処理は含まない。概要欄は一つ上の `youtube_description.txt`。

## 音声を作り直す場合

`dialogue-v6.json`が採用台詞の正本。`prepare_voice_v6.py`はコメント募集の2発話を生成し、v5の採用音声97発話を再利用する。正典のIrodori環境と起動済みVOICEVOX（localhost:50021）が必要。`finalize_v6.py`で採用WAV・タイムライン・台本を更新し、`prepare_captions_v6.py`で文節と保存音素長から字幕の改ページを確定する。後者はmacOSのCoreFoundationを使う。声のキャッシュキーにはモデル、本文、読み、参照ハッシュ、seed、CFG、生成尺、トリム設定を含む。

```sh
../../../.local/Irodori-TTS/.venv/bin/python prepare_voice_v6.py
../../../.local/voicevox-explainer/venv/bin/python finalize_v6.py
../../../.local/voicevox-explainer/venv/bin/python prepare_captions_v6.py
../../../.local/voicevox-explainer/venv/bin/python mix_audio_v2.py --manifest src/edit-manifest-v6.json --output public/mixed-v6.wav --record ../mix_record_v6.json
../../../.local/Irodori-TTS/.venv/bin/python audit_audio_v6.py --ids c124 c125
```

`audit_audio_v6.py`はWhisperによる台詞照合であり、主観的な試聴を代替しない。追加2発話の照合記録は `../asr_record_v6.json`。

## Three.js

- GLBは正本参照。モデルごとにSkeletonUtils.cloneで骨を複製し、共有アセットを変更しない。
- フレーム番号から時刻を決め、各評価で初期姿勢に戻してからAnimationMixer.setTimeを使う。
- たこさんの浮遊は共有E/curlの式を固定速度で直接評価。18触手関節の存在を検査。
- ロード終了とCanvasの描画を待ってからRemotionへフレームを渡す。
- Remotion標準配信はシンボリックリンク末端を404にするため、render_v6.cjsで生成バンドルをlocalhostに配信する。原本へのリンクは保持し、モデルを複製配布しない。
- 短区間で確認後、JPEG quality95、並列2で本編レンダー。動画からの実フレーム確認を別に実施。

## 使用した実資料

Blender版そば屋画像、回転動画、実際の四方向入力、たこさんの前後入力、そば屋の姿勢・ウェイト比較、福ギュンの正典写真、公式サイトの実操作録画、AR入口のスクリーンショット、2026-09-07のゲーム開発実録（旧モデルの記録と画面内に表示）。原型がローカルに残っていない箇所を架空の「修正前」で補わない。

公式サイト録画の再取得は `capture_site.cjs`。サイト更新により外観やボタンが変わり得るので、初稿の映像はfootage内の記録を保持する。

## 完成ファイルの検証

```sh
../../../.local/voicevox-explainer/venv/bin/python validate_timeline_v6.py
../../../.local/voicevox-explainer/venv/bin/python audit_final_v6.py
../../../.local/voicevox-explainer/venv/bin/python contact.py --final --v6
```

`audit_final_v6.py`は全編デコード、フレーム数・音声形式、既知の緑帯繰り返しの全フレーム検査を行い、各画面・主要切替前後・追加2発話の前後を実MP4から抽出する。目視・試聴の実施範囲は一つ上の `review_v6.md` へ記録する。完成後のエンディング確認用抜粋は `out/ending-v6-preview.mp4`（約31秒）。

## 演出と出典

`acting-plan-v6.json`は全99発話について話者・聞き手の表情と反応フレームを指定する。8表情を使い、常時の上下運動は廃止。たこさんの表情PNGの小さな口線は、同じ正典立ち絵の口無し部分を局所合成して隠す。目と衣装は元の表情差分をそのまま使用する。

公式ロゴと料金ページの採用入力は`../inputs/webrefs_v3/`。取得日時、公式URL、実ページの月払い状態、切り抜き範囲、SHA-256は`../web_refs_v3.json`に記録。料金画面には出典・日付を重ね、概要欄に全URLと商標クレジットを記載する。`prepare_assets.py`もこれらを検証する。

## 版の保持

v1・v2・v3・v4・v5の完成MP4、専用コンポーネント、台詞、タイムライン、レンダーコマンドを保持する。v6は `ExplainerV6` を描画し、`node render_v6.cjs full` で旧版の出力映像に依存せず全編を再現できる。完成MP4と中間出力はGit管理外。素材の出所は `../asset_sources.json`・`../asset_sources_v2.json`・`../asset_sources_v4.json`・`../web_refs_v3.json`、最終検査は `../delivery_v6.json` に記録する。

`repair_site_v2.py`は前版で行った部分修正の記録。v5はサイト映像の停止位置を修正したソースから全編レンダー済みで、v6もこの修正を継承する。旧版の部分修正処理を追加実行する必要はない。

v3で修正したたこさんの足先の見切れ対策（3場面でカメラ倍率0.90）はv5・v6でも継承する。v3の部分修正履歴は `../framing_repair_v3.json` に保持する。

## 引き継いだ比較と費用説明

`VisualV4.tsx`は冒頭の基準画像/Blender版/Tripo版の比較、制作例720pと推奨1080p、1080pでの料金試算を担当する。基準画像は現在の標準シートの正面をCSSで切り抜き、当時の生成入力は書き換えない。`../asset_sources_v4.json`にハッシュと用途を記録する。

料金はWan 3.0 1080P・8秒の通常単価$0.20/秒で256円、Tripoの採用実例120クレジットで192円、合計448円（会話では約450円）。1ドル160円、入力画像/再試行/Codex等は別。実制作の720P素材と推奨設定の試算を区別し、出典・料金条件・確認時の割引は`../resolution_source_v4.json`と概要欄に保存する。

V5の音声変更は7発話。ASR照合の記録は`../asr_record_v5.json`。主観的な通し試聴とは区別する。

```sh
../../../.local/Irodori-TTS/.venv/bin/python audit_audio_v5.py --ids u039 u055 r058 r059 p059 p060 r060
```

## v5の依頼のしかた

`VisualV5.tsx`は、Codexへ回転動画の生成・4方向切り出し・Tripo生成と保存まで依頼すること、リポジトリを添えた依頼例、Wan/Tripo双方のAPI準備を担当する。概要欄には制作知見の直リンクと、自分のキャラクターシートを渡すための依頼例を掲載。制作記録にある720Pを推奨設定と混同しないよう、画面と依頼例へ縦長1080p指定を添える。

97台詞・136字幕ページ。変更7発話、v4から90発話を再利用。API監視手順を増やさず、利用者が渡す資料と用意する設定を説明する。資料の参照先は`04_GAME_ASSETS/3d/SOBAYA_V3_LESSONS.md`。旧版の音声・映像・料金条件は保持する。

## v6のコメント募集

v5の97台詞を保ち、概要欄案内 `u124` の直後に `c124`・`c125` を追加した。たこさんがTripoの使い方やリグの作り方に自己流の部分があると伝え、やめ太郎がおすすめの方法をコメントで募る。その後は元の「会社に自分の代わりのモデルを置く」というオチへつなぐ。`VisualV6.tsx` がコメント募集画面を担当する。

追加は最終章の途中なので、概要欄の8章の開始時刻はv5から変わらない。完成仕様は99台詞・138字幕ページ、新規2発話とv5音声97発話の再利用。`../voice_record_v6.json`・`../mix_record_v6.json`・`../asr_record_v6.json` に今回の音声とミックスを記録する。
