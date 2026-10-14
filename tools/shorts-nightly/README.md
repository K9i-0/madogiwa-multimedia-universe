# 投稿ゼロ日のショート自動公開

2026-10-15 ユーザー指定：毎日 **23:00（日本時間）**、その日の公開投稿が0本なら、作成済みの投稿待ちショートを1本YouTubeへ公開する。通常動画・ショートを合わせて判定する。Studio登録・横版の更新・新規制作は行わない。

## 動作

- 公式チャンネル `UCyQtPu94OaiGxFdd2A6bXdw` を既存の所有者OAuthで確認。アップロード一覧を全ページ取得し、各動画の `status.privacyStatus` と `snippet.publishedAt` からJSTの当日分を数える。非公開・限定公開は公開本数に含めない。
- 当日中の予約公開が残っている場合も見送る。
- `03_SCRIPTS/shorts_queue_20261011/queue.json` の `ready` をorder順に選択。公開済み、YouTube IDがある回、アップロード記録がある回、チャンネルに同じ投稿タイトルがある回を除外。
- 動画・マニフェストのSHA、技術監査・目視監査、公開メタデータ、720×1280・60秒未満を検証。変更済み・未監査なら自動で飛ばさず停止。
- アップロード直前にも当日の投稿を再確認。1日最大1本。既存batch投稿と同じ排他ロックを使用する。
- 転送前に候補・SHA・日付を保存。通信失敗時は同じ候補・同じ再開セッションだけを利用し、別の動画へ進めない。既存IDは再投稿しない。前日以前の未解決転送は人が確認するまで停止。
- 23:10〜23:50に10分間隔で失敗時の再試行・処理状態確認。公開・processing succeededを確認してqueueへpublishedとIDを記録。成功後の同日実行は終了する。
- YouTube状態を取得できないときは「投稿0本」と推定しない。処理待ち・非公開・失敗になった動画を、別IDで投稿し直さない。
- 公開判定後にユーザーが手動投稿する競合まで原子的には防止できない。直前の再確認で間隔を小さくしている。

公開日時の意味：[YouTube Data API Videos reference](https://developers.google.com/youtube/v3/docs/videos#snippet.publishedAt)。非公開の所有者取得時はアップロード日時になるため、publicとの組み合わせで判定する。

## Mac上の定期実行

```sh
python3 tools/shorts-nightly/install.py
```

`~/Library/LaunchAgents/work.madogiwa.shorts-nightly.plist` を登録する。Python 3.11以上、システム時刻Asia/Tokyo、Macへのログインとネット接続、動画ファイル・既存OAuth設定が必要。インストール時に投稿は行わない（RunAtLoad=false）。

Macがスリープ中ならlaunchdは復帰時に起動するが、本処理は **23:00〜23:50 JSTだけ** 実行する。深夜を越えた穴埋め投稿はしない。電源OFF・ログアウト・夜間ずっとスリープの場合、その日の自動投稿は行えない。Macのシステムタイムゾーンを変更した場合はスケジュールも見直す。

停止：

```sh
python3 tools/shorts-nightly/install.py --remove
```

一時停止は `config.json` の `enabled` をfalseへ変更。再開はtrue。

## 確認・記録

```sh
# 読み取りのみ。時刻に関係なく当日の投稿と次の候補を確認。
python3 tools/shorts-nightly/run.py
# 実行（23時台以外は投稿しない）
python3 tools/shorts-nightly/run.py --execute
# 境界・重複・監査・API失敗のテスト
python3 -m unittest discover -s tools/shorts-nightly -p 'test_*.py' -v
```

ログは `.local/shorts-nightly/launchd.log`、最終結果は `last-run.json`、確認だけの結果は `last-preview.json`。転送中は `pending.json`、成功日は `days/YYYY-MM-DD.json`。公開IDは従来どおり投稿待ちフォルダの `youtube_uploads/<slug>.json` とqueueに記録する。定期処理は自動Git commit/pushを行わない。

秘密情報と再開セッションURLは既存の `~/.config/mmu-youtube/` のみ。ログ・Git・チャットへ出さない。期限切れセッションや不明な既存タイトルは、チャンネルを確認せず削除・再発行しない。

## 初回確認

2026-10-15朝の実API読み取りではチャンネル動画100本、当日公開0本、次候補は「窓際スーパーつらい — 土下座レース篇 #Shorts」。本番アップロードを伴わないdry-runで確認。9件の自動テスト合格。実際の投稿可否は23:00に再判定する。
