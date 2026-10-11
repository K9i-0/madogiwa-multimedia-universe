# 1分未満のShorts投稿待ち

2026-10-11ユーザー指定。この環境で制作した採用済み動画のみ。既に公開したパイロット5本を除く**37本**。60秒以上の回・同僚制作回・未採用バージョンは含めない。

[動画一覧](review.html)で完成MP4・投稿文・元の横動画を確認できる。各エピソード直下の `final_remotion_shorts_9x16.mp4` が納品動画。横版は保持し、Studioは変更しない。

## 投稿の順番

`queue.json`が正本。batch 1〜7は5本、batch 8は2本。パイロット投稿後の「次回」をbatch 1とする。カレンダー日付は未指定のため設定していない。自動投稿・公開予約・新規アップロードは今回実行していない。

```bash
python3 03_SCRIPTS/shorts_queue_20261011/publish_batch.py --batch 1
```

既定は一覧を表示するだけ。ユーザーが当該5本の登録を指示したら`--upload`を付ける。YouTubeのみへ公開し、Studioの横版IDを変更しない。既存のYouTube OAuthと再開可能なuploadツールを使用し、公開先・合成メディア申告等は`metadata/`に固定。完了後にYouTubeの処理成功と公開状態を確認する。`youtube_uploads/`は一度できたら削除・上書きしない。

## 編集仕様

720×1280、元fps・元フレーム数・採用音声を保持。同期blur背景、上はタイトルだけ、中央は横映像をcontain、下は名前28px白文字＋38pxメンバー色縁取り字幕。下線・名前枠・下部シリーズ名はなし。

配色正本：`../00_TEMPLATES/subtitles/member-colors.ts`。
字幕・クリップ・タイトルの正本：各回の`shorts-manifest.json`。
共通renderer：`remotion/src/index.tsx`。
既存字幕は移動し、ニュース帯・通販価格・配信コメント・漫画の縦書きなど作品に必要な文字は残す。無言のアクション回にセリフを足さない。

## 再レンダー

依存関係は承認済みパイロットと同じRemotion 4.0.529へ固定（2026-10-11にnpmの最新4.0.534も確認。今回は既存デザインの再現を優先し更新しない）。`remotion`内で`npm ci`、`npm run typecheck`。

1. 必要な採用元MP4と下記clean映像をローカルに置く。
2. リポジトリルートで`python3 03_SCRIPTS/shorts_queue_20261011/prepare_inputs.py`。
3. `remotion`内で`node render.mjs <slug>`。引数なしは37本全件。`--still`は確認画像のみ。
4. リポジトリルートで`python3 03_SCRIPTS/shorts_queue_20261011/audit.py`。
5. PillowのあるPythonで`extract_review.py`を実行し、完成動画の先頭・途中・最長字幕・末尾、全字幕中間点を確認する。

### 元字幕を外す映像

`clean-jobs.json`の7回は`python3 03_SCRIPTS/shorts_queue_20261011/render_clean.py`で再作成できる。引数にエピソードフォルダ名を渡せばその回だけ実行。3D回以外はそれぞれの`remotion`で次のコマンドも使える：

```bash
npx remotion render src/shorts-clean.tsx ShortsClean out/shorts-clean.mp4 --codec=h264 --crf=16 --concurrency=2 --muted
```

`73_beer_materialization_3d/remotion`は：

```bash
npx remotion render src/shorts-clean.tsx BeerTraining out/shorts-clean.mp4 --gl=angle --concurrency=2 --muted --crf=16
```

その他：土下座レースは字幕前inputを0〜600f＋採用エンドカード。ヒソバは字幕前input。そば屋ハザードはrawを0〜816f＋採用ロゴ。WAIは同じv2の字幕前master。すべて音声は採用済み完成版からstream copyし、cleanの音声は使わない。

87の採用元は既存Studio取得済みローカルキャッシュ。声比較の未採用版へ戻さず、現在の採用版とタイムライン一致を確認済み。

## 記録と監査

- `inventory.json`：対象37回、採用元、実測。移行時の登録者だけで作者を判定せず、ローカル生成記録とStudioの生成作者を照合して選定。
- `technical-audit.json`：全編デコード、寸法、60秒未満、fps、フレーム数、元音声のhash一致、動画・字幕ファイルhash。
- `visual-audit.json`：完成フレームと字幕の目視確認記録。
- `delivery.json`：完成MP4・週別一覧・検証結果。
- `metadata/`：横版リンク・元説明文・必要な音楽/音声クレジットを保持。
- `out/`：元YouTube情報、ASR補助、監査画像。ローカルのみ。

ASRは制作台本・既存字幕の照合とタイミング補助として使用した。BGM中の「ご視聴ありがとうございました」などの誤認識は採用しない。音声は元の採用音源を変更せず保持する。主観的な全編試聴の完了は認定していない。

新規制作・今後の運用は `.claude/skills/shorts-video/SKILL.md` を参照。
