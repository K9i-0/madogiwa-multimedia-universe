# Tripo制作解説・初稿v1

たこさん＆やめ太郎の技術解説。1280×720 / 30fps。正本のセリフと絵の対応は `src/edit-manifest.json`、制作原稿は一つ上の `script.md`。

## 再現

```sh
npm ci
python3 prepare_assets.py
npm run typecheck
node render.cjs stills
node render.cjs short
node render.cjs full
```

`prepare_assets.py`はリポジトリ内の正本とローカル保持映像をSHA-256照合し、publicへ相対symlinkを張る。生成済みの採用音声はエピソード直下。外部ストレージからの動画復元が必要な環境では、不足ファイルを明示して止まる。

音声の再ミックス（リポジトリのPython環境を利用）：

```sh
../../../.local/voicevox-explainer/venv/bin/python mix_audio.py
ffmpeg -y -i out/visuals.mp4 -i public/mixed.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -movflags +faststart ../final_remotion_tripo_workflow_v1.mp4
```

公開・アップロード処理は含まない。概要欄は一つ上の `youtube_description.txt`。

## 音声を作り直す場合

`prepare_voice.py`は候補台詞全体の生成。正典のIrodori環境と起動済みVOICEVOX（localhost:50021）が必要。`edit_selection.json`で重複説明を除き、`finalize.py`で採用WAV・タイムライン・台本を更新する。声のキャッシュキーにはモデル、本文、読み、参照ハッシュ、seed、CFG、生成尺、トリム設定を含む。

```sh
../../../.local/Irodori-TTS/.venv/bin/python prepare_voice.py
../../../.local/voicevox-explainer/venv/bin/python finalize.py
../../../.local/voicevox-explainer/venv/bin/python mix_audio.py
```

`audit_audio.py`はWhisperによる台詞照合であり、主観的な試聴を代替しない。

## Three.js

- GLBは正本参照。モデルごとにSkeletonUtils.cloneで骨を複製し、共有アセットを変更しない。
- フレーム番号から時刻を決め、各評価で初期姿勢に戻してからAnimationMixer.setTimeを使う。
- たこさんの浮遊は共有E/curlの式を固定速度で直接評価。18触手関節の存在を検査。
- ロード終了とCanvasの描画を待ってからRemotionへフレームを渡す。
- Remotion標準配信はシンボリックリンク末端を404にするため、render.cjsで生成バンドルをlocalhostに配信する。原本へのリンクは保持し、モデルを複製配布しない。
- 短区間で確認後、JPEG quality95、並列2で本編レンダー。動画からの実フレーム確認を別に実施。

## 使用した実資料

Blender版そば屋画像、回転動画、実際の四方向入力、たこさんの前後入力、そば屋の姿勢・ウェイト比較、福ギュンの正典写真、公式サイトの実操作録画、AR入口のスクリーンショット、保存済みゲーム画面。原型がローカルに残っていない箇所を架空の「修正前」で補わない。

公式サイト録画の再取得は `capture_site.cjs`。サイト更新により外観やボタンが変わり得るので、初稿の映像はfootage内の記録を保持する。
