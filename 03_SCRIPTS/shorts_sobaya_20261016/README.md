# Studio既存動画のShorts編集（2026-10-16）

対象は公式サイト掲載中の作品のうち、元動画が **101秒以下**、Studioに制作プロンプトがあり、今回の照合でショート未作成だった34作品。101秒で長い作品を切り捨てる依頼ではない。採用済み映像・音声を使い、720×1280の縦画面へ編集する。

- 上段：作品タイトル。中央：画角を切らずに元映像を配置。背景：同じ時刻の映像を暗くぼかす。下段：話者名と日本語字幕。
- 字幕はプロンプト、入力WAVの波形・周波数特徴との照合、必要な短区間の音声認識を組み合わせる。元の音声トラックはコピーして保持する。
- 焼き込み字幕・作品内UI・商品名・必要な音声クレジットは残す。復元できない焼き込み字幕を重ねて表示しない。
- 不確かな短い発話は推測で補わず、原音を保つ。各manifestの注記と音声認識記録に根拠を残す。人による全編の試聴完了は主張しない。

## 元版の選択

R2の最新生成が、現在YouTubeへ掲載されている版とは限らない。`source-record.json` / `source-evidence.json` / manifest内の`sourceSelection`に採用版とR2キーを記録した。

- Tシャツ破壊CMは公開尺に一致するv2、ビールで完成するTシャツCMはv3。
- タンクローリー篇は福ギュンの導入・反応がある公開v2。作者はK9i。
- 地球侵略篇の予告は61.2秒の公開版。既存の字幕なし映像と元の予告カードを同じ編集位置で組み、会話字幕だけを下へ移した。原音は予告版のまま。作者はK9i。
- ビール電池は採用された福ギュン・よーたん版。作者はK9i。
- バンジーアプリは公開版の焼き込み字幕を保持。
- 赤ちゃん回とたこさんのPHP回は、実際に公開されたアニマティックを採用。
- ゆめみんのPHP回は、公開元動画がすでに1080×1920の縦動画だったため、重複した新規投稿は作らない。

作品名に「そば屋」があるかどうかでは作者を判定しない。今回の新規分はK9i 3本・そば屋さん31本。

## 再編集・書き出し

リポジトリのルートで実行する。必要なソース動画は各episodeディレクトリにローカル保存してあり、Gitには含めない。再取得時は記録されたR2キーを使う。

```sh
npm ci --prefix 03_SCRIPTS/shorts_sobaya_20261016/remotion
node 03_SCRIPTS/shorts_sobaya_20261016/remotion/render.mjs \
  03_SCRIPTS/shorts_sobaya_20261016/episodes/作品slug/shorts-manifest.json
```

Remotionで字幕の切り替えごとに透明なReactカードを生成し、FFmpegで元映像と合成する。MacはVideoToolbox H.264（quality 75）、他環境はlibx264（CRF18）を使用する。`MMU_SHORTS_ENCODER=libx264`で明示的に切り替えられる。既に出力済みの一部作品はlibx264で書き出した。いずれも元fpsとフレーム数を保持し、元の圧縮音声をコピーする。

途中でソースの色・SAR等のメタデータが変わるとフィルターのフレームカウンターがリセットされるため、入力の`reinit_filter`を無効にした。書き出し直後にもフレーム数の一致を必須にして、末尾欠落を検出する。

予告篇の中間素材を再作成する場合：

```sh
python3 03_SCRIPTS/shorts_sobaya_20261016/tools/rebuild_trailer_clean.py
```

この処理は既存40秒版の`03_SCRIPTS/66_madogiwa_super_try_invasion/remotion/out/shorts-clean.mp4`を参照する。そのファイルがない場合は、同作品の元入力を`public/`へ戻し、同作品の`remotion/`ディレクトリで先に次を実行する。

```sh
npx remotion render src/shorts-clean.tsx ShortsClean out/shorts-clean.mp4 --concurrency=2
```

## 検証と自動投稿

各groupの技術監査で全編デコード、720×1280、fps・フレーム数、音声ストリームSHA、101秒以下、字幕の範囲・重複を確認する。目視監査は完成動画から取り出した字幕中間点・シーン・末尾フレームを対象に行い、ファイルSHAに紐付ける。

```sh
python3 03_SCRIPTS/shorts_sobaya_20261016/audit_completed.py \
  --groups group-root.json --out technical-audit-group-root.json --workers 1
python3 03_SCRIPTS/shorts_sobaya_20261016/integrate_queue.py --write
python3 tools/shorts-nightly/run.py
```

`queue.json`の`ready`は両監査を通過した完成物だけに付ける。既存の夜間投稿処理はこのqueueと従来queueを読み、K9iとそば屋さんを交互に選ぶ。各作者内の順番を維持し、片方がなくなれば残る作者を続ける。既存ルールの「23:00 JST、その日に公開投稿も当日予約もなければ1本」を維持する。

公式サイト全94作品の内訳は [ショート対応一覧](../shorts_site_inventory_20261016.md) を参照。
