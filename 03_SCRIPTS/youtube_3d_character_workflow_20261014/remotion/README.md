# Tripo制作解説・完成版v3

たこさん＆やめ太郎の技術解説。1280×720 / 30fps。完成尺10分34.933秒。正本のセリフと絵の対応は `src/edit-manifest-v3.json`、制作原稿は一つ上の `script.md`。

## 再現

```sh
npm ci
python3 prepare_assets.py
../../../.local/voicevox-explainer/venv/bin/python mix_audio_v2.py --manifest src/edit-manifest-v3.json --output public/mixed-v3.wav --record ../mix_record_v3.json
npm run typecheck
node render_v3.cjs stills
node render_v3.cjs short
node render_v3.cjs full
```

`prepare_assets.py`はリポジトリ内の正本とローカル保持映像をSHA-256照合し、publicへ相対symlinkを張る。生成済みの採用音声はエピソード直下。外部ストレージからの動画復元が必要な環境では、不足ファイルを明示して止まる。

映像とミックス済み音声を完成MP4へまとめる：

```sh
ffmpeg -y -i out/visuals-v3.mp4 -i public/mixed-v3.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -movflags +faststart ../final_remotion_tripo_workflow_v3.mp4
```

公開・アップロード処理は含まない。概要欄は一つ上の `youtube_description.txt`。

## 音声を作り直す場合

`dialogue-v3.json`が採用台詞の正本。`prepare_voice_v3.py`は変更音声を生成し、元のv2の採用音声77発話を再利用する。正典のIrodori環境と起動済みVOICEVOX（localhost:50021）が必要。`finalize_v3.py`で採用WAV・タイムライン・台本を更新し、`prepare_captions_v3.py`で文節と保存音素長から字幕の改ページを確定する。後者はmacOSのCoreFoundationを使う。声のキャッシュキーにはモデル、本文、読み、参照ハッシュ、seed、CFG、生成尺、トリム設定を含む。

```sh
../../../.local/Irodori-TTS/.venv/bin/python prepare_voice_v3.py
../../../.local/voicevox-explainer/venv/bin/python finalize_v3.py
../../../.local/voicevox-explainer/venv/bin/python prepare_captions_v3.py
../../../.local/voicevox-explainer/venv/bin/python mix_audio_v2.py --manifest src/edit-manifest-v3.json --output public/mixed-v3.wav --record ../mix_record_v3.json
```

`audit_audio_v3.py`はWhisperによる台詞照合であり、主観的な試聴を代替しない。

## Three.js

- GLBは正本参照。モデルごとにSkeletonUtils.cloneで骨を複製し、共有アセットを変更しない。
- フレーム番号から時刻を決め、各評価で初期姿勢に戻してからAnimationMixer.setTimeを使う。
- たこさんの浮遊は共有E/curlの式を固定速度で直接評価。18触手関節の存在を検査。
- ロード終了とCanvasの描画を待ってからRemotionへフレームを渡す。
- Remotion標準配信はシンボリックリンク末端を404にするため、render_v3.cjsで生成バンドルをlocalhostに配信する。原本へのリンクは保持し、モデルを複製配布しない。
- 短区間で確認後、JPEG quality95、並列2で本編レンダー。動画からの実フレーム確認を別に実施。

## 使用した実資料

Blender版そば屋画像、回転動画、実際の四方向入力、たこさんの前後入力、そば屋の姿勢・ウェイト比較、福ギュンの正典写真、公式サイトの実操作録画、AR入口のスクリーンショット、2026-09-07のゲーム開発実録（旧モデルの記録と画面内に表示）。原型がローカルに残っていない箇所を架空の「修正前」で補わない。

公式サイト録画の再取得は `capture_site.cjs`。サイト更新により外観やボタンが変わり得るので、初稿の映像はfootage内の記録を保持する。

## 完成ファイルの検証

```sh
../../../.local/voicevox-explainer/venv/bin/python validate_timeline_v3.py
../../../.local/voicevox-explainer/venv/bin/python audit_final_v3.py
../../../.local/voicevox-explainer/venv/bin/python contact.py --final --v3
```

`audit_final_v3.py`は全編デコード、フレーム数・音声形式、既知の緑帯繰り返しの全フレーム検査を行い、各画面と主要切替前後を実MP4から抽出する。目視・試聴の実施範囲は一つ上の`review_v3.md`へ記録する。

## v3の演出と出典

`acting-plan-v3.json`は全93発話について話者・聞き手の表情と反応フレームを指定する。8表情を使い、常時の上下運動は廃止。たこさんの表情PNGの小さな口線は、同じ正典立ち絵の口無し部分を局所合成して隠す。目と衣装は元の表情差分をそのまま使用する。

公式ロゴと料金ページの採用入力は`../inputs/webrefs_v3/`。取得日時、公式URL、実ページの月払い状態、切り抜き範囲、SHA-256は`../web_refs_v3.json`に記録。料金画面には出典・日付を重ね、概要欄に全URLと商標クレジットを記載する。`prepare_assets.py`もこれらを検証する。

## 版の保持

v1・v2の完成MP4、専用コンポーネント、台詞、タイムライン、レンダーコマンドを保持する。v3は`ExplainerV3`を描画し、旧タイムラインと独立して再現できる。完成MP4と中間出力はGit管理外。素材の出所は`../asset_sources.json`・`../asset_sources_v2.json`・`../web_refs_v3.json`、最終検査は`../delivery_v3.json`に記録する。

`repair_site_v2.py`は前版で行った部分修正の記録。v3はサイト映像の停止位置を修正したソースから全編レンダーするため、部分修正は不要。

最終監査で見つけた、たこさんの動作中の足先の見切れは、3場面のカメラに余白を足して修正した。今回の完成MP4は`repair_framing_v3.py`で該当区間を整数フレーム単位で差し替えたもの。新規の全編レンダーは修正済みソースを使うため、追加処理不要。今回の処理範囲とエンコード条件は`../framing_repair_v3.json`に記録。
