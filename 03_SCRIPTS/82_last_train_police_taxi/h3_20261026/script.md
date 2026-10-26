# 帰宅困難族：H3比較生成（2026-10-26）

第82話の採用台本をMiniMax H3 R2Vで再生成する。人物画像6枚・声質参照3本。
正典キャラクターシートは現行版を使用。車両・飲み会画像と声質参照は元エピソードを使用。
元Wan動画を入力せず、台本・参照入力から作る。最後の台詞を車外へ移す採用済み演出を維持。

- 前半：居酒屋→閉駅→そば屋がタクシーを手で止める。「止め方！」まで。
- 後半：パトカー後部座席。福ギュンが赤坂とコンビニを依頼。走り去る車外で「タクシーちゃうねん」。
- 各362frames / 24fps = 15.0833秒。合計724frames = 30.1667秒。
- 864×480、base20steps、seed820926 / 820927。画像と声は参照、台詞はH3生成。
- Colab A100を1台使用し直列実行。セットアップ1回。ComfyUIとモデルrevisionは共通スキルの固定値。
- 初期残高180.48CU。生成開始前179.82CU、6.77CU/時。前ターン終了による不要な待機を含むため、残高差と生成処理費を区別する。
- ユーザーは明らかなネタ動画として実行する判断を明示。モデル地域不明等の独自の保守的停止条件を追加しない。

入力出典とハッシュ：input_manifest.json。実入力本文：prompt_ch1.txt / prompt_ch2.txt。
リポジトリルートから `python3 03_SCRIPTS/82_last_train_police_taxi/h3_20261026/prepare.py` で .local/h3-episode82/bundle にworkflowと入力を準備。
colab_batch.pyは同じGPUで2本を順次実行し、ジョブID保存による再送防止、ログ、結果ZIPを保持する。

## 初回生成結果

生成・回収成功、A100停止済み。出力 `h3_last_train_720p.mp4` は1280×720、724frames、24fps、30.1667秒、AAC32kHz stereo。
480p原本2本は `generated/ch1_480p.mp4` と `generated/ch2_480p.mp4`。動画・詳細ログはGit管理外。

- GPU: NVIDIA A100-SXM4-80GB。セットアップ内部165.22秒、サーバーreadyまで196.23秒。
- 前半571.43秒、後半571.18秒。サンプラーは各約8分31秒、残りはモデル処理・VAE・保存・検査。
- リモート全工程1339.02秒（22分19秒）。720p化・監査はGPU停止後にローカル実行。
- 消費表示180.48→177.01 CU、差3.47CU。実行前の不要な待機・転送・回収を含む。6.77CU/時からの全工程計算値は約2.52CU。残高表示には反映遅延があり厳密な請求値ではない。
- 画像の1秒間隔全体確認、音声認識、フレーム数・音声トラック検査、最終全デコードを実施。
- 3人と居酒屋→駅→タクシー→パトカー車内→車外の順序を確認。
- 演出差分：そば屋が前かがみ。後輪が浮く演出は確認できない。居酒屋の白Tシャツに点状の胸陰影が残る。
- ASRには予定台詞が含まれるが、後半に台本外と思われる追加発話も認識された。声質・自然さ・厳密な口同期・通し試聴の合格は未判定。初回比較用として納品し、自動修復・追加生成は行っていない。
- 2本の生成フレームを保持し `export.py` で結合、Lanczosで一度だけ720p化。今回の単純結合・拡大にはFFmpegを使用し、字幕や音声修正は加えていない。

ハッシュ・ジョブ情報・ASR・監査範囲の正本は `generation_record.json`。


## Irodori全台詞差し替え・編集確認版

ユーザーが全音声のIrodori化と完成編集を依頼。タクシーがカメラ方向へ突っ込む点、運転手への問いかけにそば屋が反応する点は今回は許容。映像の再生成は行わない。

- postproduction=remotion、既存remotionプロジェクトへ `H3LastTrainIrodori` を追加。旧Wan編集compositionは保持。
- 正典参照3本からIrodori v4 Largeで全10行を初回生成。やめ太郎通常短文はCFG5・duration0.70・captionなし・uncut。そば屋は正典monsterize。
- H3会話音声を外し、Irodoriを等速配置。話す長さに合わせて映像の区間速度を調整。車内の余計な発話区間を削除し、オチを車外へ。
- H3の発話のない乾杯／停止音と、既存Wan71由来の採用済みサイレンを配置。新規の効果音生成はなし。
- 確認版 `h3_irodori_review_v1.mp4`、1280×720、24fps、725frames、約30.21秒。初回音声のため完成採用前。
- やめ太郎の語尾の伸びとコンビニの「寄って」の読みについて、4行（01/04/09/10）の再生成をユーザーへ確認中。追加生成未実行。
- 音声候補と詳細ログは `.local/h3-episode82-edit/`。候補WAVは採用前のためGit対象外。正典参照、生成コード、候補設定とハッシュ、編集タイムライン、QAは記録する。
- 再現：リポジトリルートから既存Large環境のPythonで `remotion/scripts/h3_generate_dialogue.py`（既存候補があると再生成を拒否）。`h3_prepare_edit.py`→`h3_build_edit.py`。remotion内で `npx remotion render src/index.ts H3LastTrainIrodori out/h3_irodori_v1.mp4 --codec=h264 --crf=18 --concurrency=2`。
- 音声認識と通し試聴・音素単位の口同期は別。現在はASR／映像確認／全デコード／尺・音声トラックを検査済み。


## Irodori編集完成版（2026-10-26）

追加生成の確認ルールは課金が発生する場合だけで、ローカルIrodoriは対象外というユーザーの明確化に従い、修正を継続。

- 全10台詞を正典参照のIrodori音声へ差し替え。01/04/10はduration_scale 0.40で語尾・余計な発話を改善。09は読み入力を「よって」とし、seed42・CFG5・captionなしで修正。
- 07「止め方！」は短縮候補2本で発話が崩れたため、不採用。ASRで台詞が確認できた初回音声を採用。音声の早送りや語尾切断はしない。
- サイレンを車内0.04／車外0.055へ抑え、台詞の間と映像の速度を調整。余分な車内発話場面を削除、車外でオチ。
- 完成出力 `../final_remotion_h3_irodori.mp4`、1280×720、24fps、635frames、約26.46秒。H3元映像は保持。追加API・Colab利用なし。
- 採用10行WAVはエピソード直下の `h3_line*.wav`。再生成設定・参照と採用ハッシュは `remotion/h3-voice-manifest.json`。未採用候補は.localのみ。
- 再構築：ルートで `python3 03_SCRIPTS/82_last_train_police_taxi/remotion/scripts/h3_prepare_edit.py` → `h3_build_edit.py`（同ディレクトリ）→ remotion内で `npx remotion render src/index.ts H3LastTrainIrodori out/h3_irodori_v2.mp4 --codec=h264 --crf=18 --concurrency=2`。原本H3動画2本がローカルに必要。
- 音声再生成が必要ならLarge環境のPythonで `remotion/scripts/h3_regenerate_adopted.py`。採用WAVを上書きせず.localへ出す。初回候補用の `h3_generate_dialogue.py` は履歴用。
- 検証範囲はASR、映像サンプル、型チェック、全デコード、映像・音声トラックと音量。聴感・厳密な口同期の合格は自動検査から断定しない。許容された映像2点はそのまま。


## FB1修正（2026-10-26）

ユーザー視聴で、居酒屋の環境音不足、05の「タクシー」の異常な引き伸ばし、07「止め方！」後の音声崩れが判明。前回ASR一致は聴感の合格ではなかった。

- 居酒屋の0〜136フレーム（5.667秒）に、会話のざわめき・食器音の環境録音を追加。高域を抑え、-31 LUFSで主台詞の後ろへ配置。出典はJoseph SARDIN / BigSoundBank「Restaurant」（CC0）、`remotion/h3-ambience-source.json`。これはフランスのレストラン録音を背景のガヤとして使用したもの。
- 05「あ、タクシー！」：Irodori Large、正典参照、seed100、captionなし、CFG5、duration_scale0.55でローカル再生成。2.32秒の候補から発話を含む1.40秒を採用し、末尾60msフェードで伸びを削除。音高・話速は変更なし。
- 07「止め方！」：ユーザーの後半カット指定に従い、既存採用音声の先頭0.90秒を保持。最後40msフェード。1.2秒以降を含む候補にはASRでも余計な語句が出たため除外。映像も対応区間の後半を切り、早送りにしない。
- 完成版は同じ `../final_remotion_h3_irodori.mp4` を更新。1280×720、24fps、537フレーム、22.375秒。修正前は `remotion/out/h3_irodori_before_fb1.mp4` に保持。
- 採用音声は `h3_line05_fukuchan_fb1.wav` / `h3_line07_yametaro_fb1.wav`、環境音は `h3_izakaya_ambience.wav`。設定・カット範囲は音声manifestと再生成スクリプトへ反映。追加有料生成なし。
- 05/07の採用カットを再ASRし指定台詞を確認。型・タイムライン・全デコード・音量・映像サンプルを検証。聴感の合格はASRから断定しない。
