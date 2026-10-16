# 投稿ゼロ日のショート自動公開

2026-10-15 ユーザー指定：毎日 **23:00（日本時間）**、その日の公開投稿が0本なら、作成済みの投稿待ちショートを1本YouTubeへ公開する。通常動画・ショートを合わせて判定する。Studio登録・横版の更新・新規制作は行わない。

2026-10-16 ユーザー指定：自分（`k9i`）とそば屋さん（`sobaya`）の動画を交互に投稿する。追加制作の対象は、元動画が **1分41秒以下**でStudioに生成プロンプトがある未ショート化作品。短縮によって長い元動画を対象に含めない。

## 動作

- 公式チャンネル `UCyQtPu94OaiGxFdd2A6bXdw` を既存の所有者OAuthで確認。アップロード一覧を全ページ取得し、各動画の `status.privacyStatus` と `snippet.publishedAt` からJSTの当日分を数える。非公開・限定公開は公開本数に含めない。
- 当日中の予約公開が残っている場合も見送る。
- `config.json` の `queues` に並ぶ投稿待ちフォルダを読み、`ready` だけを対象にする。公開済み、YouTube IDがある回、アップロード記録がある回、チャンネルに同じ投稿タイトルがある回を除外する。同じslug・元動画YouTube IDの重複はqueueをまたいでも除外する。
- 直近に公開成功した管理対象Shortsの作者と逆の作者を選ぶ。同じ作者の中ではqueueの記載順・各queueのorder順を保つ。片方の残りが0本なら、もう片方を続けて投稿する。作者は各行の `creator` を使い、省略された従来行は `k9i` と扱う。タイトル中の「そば屋」から作者を推定しない。
- 公開成功はチャンネルの公開・処理完了状態とID、または成功済みの日別記録で判断する。失敗・処理待ちでは交代しない。成功履歴がまだない場合だけ `firstCreator`（省略時 `k9i`）を使う。
- 動画・マニフェストのSHA、技術監査・目視監査、公開メタデータ、720×1280を検証。従来行は60秒未満を維持する。明示した追加制作の許可情報を持つ行だけ101秒以下を認め、元動画の尺と保存済みStudioプロンプトの存在も確認する。変更済み・未監査なら自動で飛ばさず停止。
- アップロード直前にも当日の投稿を再確認。1日最大1本。全体の排他ロックと、設定されたすべてのqueueの既存batch投稿用ロックを取得する。
- 転送前に候補・SHA・日付を保存。通信失敗時は同じ候補・同じ再開セッションだけを利用し、別の動画へ進めない。既存IDは再投稿しない。前日以前の未解決転送は人が確認するまで停止。
- 23:10〜23:50に10分間隔で失敗時の再試行・処理状態確認。公開・processing succeededを確認してqueueへpublishedとIDを記録。成功後の同日実行は終了する。
- YouTube状態を取得できないときは「投稿0本」と推定しない。処理待ち・非公開・失敗になった動画を、別IDで投稿し直さない。
- 公開判定後にユーザーが手動投稿する競合まで原子的には防止できない。直前の再確認で間隔を小さくしている。

公開日時の意味：[YouTube Data API Videos reference](https://developers.google.com/youtube/v3/docs/videos#snippet.publishedAt)。非公開の所有者取得時はアップロード日時になるため、publicとの組み合わせで判定する。

## 複数queueと追加制作の記録

`queues` はリポジトリ相対のフォルダ一覧。従来の `queue` は古い転送中記録の所属先として保持する。設定は実行ごとに読み直すため、追加だけならlaunchdの再登録は不要。

```json
{
  "queue": "03_SCRIPTS/shorts_queue_20261011",
  "queues": [
    "03_SCRIPTS/shorts_queue_20261011",
    "03_SCRIPTS/shorts_sobaya_20261016"
  ],
  "firstCreator": "sobaya"
}
```

各フォルダの `queue.json`、`technical-audit.json`、`visual-audit.json`、`metadata/`、`youtube_uploads/` は従来と同じ形式で個別に保持する。既存upload記録を移動・上書きしない。元動画が101秒以下の追加制作行には次を追加する。`promptPath` はリポジトリ相対パス。完成動画自体も101秒以下である必要がある。

```json
{
  "creator": "sobaya",
  "eligibility": {
    "policy": "studio-prompt-max101s-20261016",
    "sourceDurationSeconds": 78.25,
    "promptPath": "03_SCRIPTS/shorts_sobaya_20261016/episodes/example/prompt.txt"
  }
}
```

まだ完成していない行は `rendering` などの状態で保持し、動画・メタデータ・両監査が揃ってから `ready` にする。転送中の `pending.json` には所属queueと作者も保存する。作者交代やqueueの順番を変更しても転送途中の候補は変えない。旧形式のpendingは従来queueへ戻し、同じ再開セッションで処理する。未解決pendingのqueueを設定から外すと停止する。

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

ログは `.local/shorts-nightly/launchd.log`、最終結果は `last-run.json`、確認だけの結果は `last-preview.json`。転送中は `pending.json`、成功日は `days/YYYY-MM-DD.json`。公開IDは候補の所属フォルダの `youtube_uploads/<slug>.json` とqueueに記録する。成功記録には作者と公開日時も残し、次の作者選択へ使う。定期処理は自動Git commit/pushを行わない。

秘密情報と再開セッションURLは既存の `~/.config/mmu-youtube/` のみ。ログ・Git・チャットへ出さない。期限切れセッションや不明な既存タイトルは、チャンネルを確認せず削除・再発行しない。

## 初回確認

2026-10-15朝の実API読み取りではチャンネル動画100本、当日公開0本、次候補は「窓際スーパーつらい — 土下座レース篇 #Shorts」。本番アップロードを伴わないdry-runで確認。9件の自動テスト合格。実際の投稿可否は23:00に再判定する。

2026-10-16の拡張では27件の自動テストが合格。作者交代・片側の残数ゼロ・queue間重複・成功履歴・旧pending互換・queue別ロック・101秒の明示許可・プロンプト欠落・既存の60秒制限を検証した。
