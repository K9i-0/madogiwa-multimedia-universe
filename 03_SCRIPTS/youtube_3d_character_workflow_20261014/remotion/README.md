# Tripo制作解説・完成版v2

たこさん＆やめ太郎の技術解説。1280×720 / 30fps。完成尺10分42.767秒。正本のセリフと絵の対応は `src/edit-manifest-v2.json`、制作原稿は一つ上の `script.md`。

## 再現

```sh
npm ci
python3 prepare_assets.py
../../../.local/voicevox-explainer/venv/bin/python mix_audio_v2.py
npm run typecheck
node render_v2.cjs stills
node render_v2.cjs short
node render_v2.cjs full
```

`prepare_assets.py`はリポジトリ内の正本とローカル保持映像をSHA-256照合し、publicへ相対symlinkを張る。生成済みの採用音声はエピソード直下。外部ストレージからの動画復元が必要な環境では、不足ファイルを明示して止まる。

映像とミックス済み音声を完成MP4へまとめる：

```sh
ffmpeg -y -i out/visuals-v2.mp4 -i public/mixed-v2.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -movflags +faststart ../final_remotion_tripo_workflow_v2.mp4
```

公開・アップロード処理は含まない。概要欄は一つ上の `youtube_description.txt`。

## 音声を作り直す場合

`dialogue-v2.json`が採用台詞の正本。`prepare_voice_v2.py`は変更音声を生成し、元の採用音声66発話を再利用する。正典のIrodori環境と起動済みVOICEVOX（localhost:50021）が必要。`finalize_v2.py`で採用WAV・タイムライン・台本を更新し、`prepare_captions_v2.py`で文節と保存音素長から字幕の改ページを確定する。後者はmacOSのCoreFoundationを使う。声のキャッシュキーにはモデル、本文、読み、参照ハッシュ、seed、CFG、生成尺、トリム設定を含む。

```sh
../../../.local/Irodori-TTS/.venv/bin/python prepare_voice_v2.py
../../../.local/voicevox-explainer/venv/bin/python finalize_v2.py
../../../.local/voicevox-explainer/venv/bin/python prepare_captions_v2.py
../../../.local/voicevox-explainer/venv/bin/python mix_audio_v2.py
```

`audit_audio_v2.py`はWhisperによる台詞照合であり、主観的な試聴を代替しない。

## Three.js

- GLBは正本参照。モデルごとにSkeletonUtils.cloneで骨を複製し、共有アセットを変更しない。
- フレーム番号から時刻を決め、各評価で初期姿勢に戻してからAnimationMixer.setTimeを使う。
- たこさんの浮遊は共有E/curlの式を固定速度で直接評価。18触手関節の存在を検査。
- ロード終了とCanvasの描画を待ってからRemotionへフレームを渡す。
- Remotion標準配信はシンボリックリンク末端を404にするため、render_v2.cjsで生成バンドルをlocalhostに配信する。原本へのリンクは保持し、モデルを複製配布しない。
- 短区間で確認後、JPEG quality95、並列2で本編レンダー。動画からの実フレーム確認を別に実施。

## 使用した実資料

Blender版そば屋画像、回転動画、実際の四方向入力、たこさんの前後入力、そば屋の姿勢・ウェイト比較、福ギュンの正典写真、公式サイトの実操作録画、AR入口のスクリーンショット、2026-09-07のゲーム開発実録（旧モデルの記録と画面内に表示）。原型がローカルに残っていない箇所を架空の「修正前」で補わない。

公式サイト録画の再取得は `capture_site.cjs`。サイト更新により外観やボタンが変わり得るので、初稿の映像はfootage内の記録を保持する。

## 完成ファイルの検証

```sh
../../../.local/voicevox-explainer/venv/bin/python validate_timeline_v2.py
../../../.local/voicevox-explainer/venv/bin/python audit_final_v2.py
../../../.local/voicevox-explainer/venv/bin/python contact.py --final --v2
```

`audit_final_v2.py`は全編デコード、フレーム数・音声形式、既知の緑帯繰り返しの全フレーム検査を行い、各画面と主要切替前後を実MP4から抽出する。目視・試聴の実施範囲は一つ上の`review_v2.md`へ記録する。

## 版の保持

v1の構成、音声、`render.cjs`、`final_remotion_tripo_workflow_v1.mp4`は保持する。v2は`ExplainerV2`を描画し、旧タイムラインと独立して再現できる。完成MP4と中間出力はGit管理外。v2追加素材の出所・ハッシュは`../asset_sources_v2.json`、最終ファイルの検査は`../delivery_v2.json`に記録する。

最終監査で見つけたサイト映像の停止位置は修正済み。`repair_site_v2.py`は既存の全編出力から該当2区間を差し替えた作業の再現用で、新規の全編レンダーには不要。
