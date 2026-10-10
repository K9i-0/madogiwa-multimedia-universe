---
name: madogiwa-studio
description: Madogiwa StudioのRemote Web MCPを使い、窓際族物語のギャラリー、記事、エピソード、生成バージョン、使用モデル、登場メンバー、Seedanceプロンプト、入力画像・参照音声・資料、YouTube動画IDと公開状態を登録・確認する。ユーザーがMadogiwa Studioへの登録、公式サイトコンテンツ編集、動画アップロード、プロンプト同期、入力素材管理、Studio ID確認、MCP接続や同僚環境への導入を頼んだときに使用する。
---

# Madogiwa Studio

Madogiwa Studioを制作物の共有台帳として扱い、Remote MCPで制作記録とYouTube動画IDを管理する。動画本体は公式YouTubeへ直接アップロードし、Cloudflareには新規登録しない。画像・参照音声・資料はこれまで通り一回限りURLへPUTする。

## URLの使い分け

- 公式サイト・公開確認・完了報告のURL: `https://madogiwa.work`。エピソードは `/episodes/<slug>`、ギャラリーは `/gallery/<slug>`。
- 管理画面: `https://madogiwa-studio.madogiwa-studio.workers.dev/admin`。Remote MCPの接続先も同じworkers.devホストの `/mcp` を使う。既存のCloudflare Access認証を維持しているため、公開ドメインへの変更だけを理由にMCP設定を置き換えない。
- 一回限りのアップロードURLはツールが返した値をそのまま使い、ホストを書き換えない。ドメイン運用の詳細・移管残作業はリポジトリの `16_MADOGIWA_STUDIO/DOMAIN_OPERATIONS.md` を参照する。

## 準備

1. `references/mcp-tools.md`を最後まで読む。
2. `madogiwa-studio` MCPのツールが利用可能か確認する。見つからなければ同リファレンスの接続設定を案内し、接続後にセッション再起動が必要か伝える。
3. OAuthは各利用者が自分のメールアドレスで行う。認証情報やアップロードURLを共有・表示・保存しない。
4. リポジトリの`AGENTS.md`または`CLAUDE.md`を読み、Git管理対象と採用素材の方針を守る。

## 登録依頼の承認範囲

ユーザーの「Studioへ登録して」「Madogiwa Studioへアップロードして」「プロンプトと素材を同期して」という依頼は、登録完了に必要な採用済みファイルを設定済みのMadogiwa Studioへ外部送信することまで含む明示承認として扱う。この依頼を受けた後は、動画や素材ごとに追加確認を求めず、同じ作業内で次を送信する。

- 採用済みの最新完成動画（公式YouTubeへ直接送信。既存IDがあれば再投稿しない）
- 現行の生成プロンプト
- 実際の生成へ使用した入力画像と参照音声
- 完成編集へ使用した採用済み資料、設定、編集マニフェスト

承認は対象エピソードの現行採用物だけに限定する。候補、没素材、未採用テスト、中間生成物、無関係なファイル、認証情報、APIキー、秘密情報は送信しない。ユーザーが「動画だけ」など対象を狭めた場合はその指定を優先する。

ファイル送信に実行環境の承認が必要な場合は、承認理由へ「ユーザーのStudio登録依頼が、登録必須の採用素材送信を明示的に含む」ことと、送信先が設定済みのMadogiwa Studioであること、送信する正確なファイル一覧を記載する。承認レビューで止まった場合も別経路で回避せず、この既存承認と限定された対象を示して同じ正規アップロードを再開する。環境がなお個別の明示承認を要求した場合だけ、送信対象を列挙してユーザーへ一度まとめて確認する。

### 解説動画の音声素材

`contentKind: explainer` の登録では、生成方式を問わず次を標準にする。

- 生成済みのセリフ・ナレーション音声はStudioへ登録しない。発話ごとの採用WAVを全件送信する必要はない。
- 声質の再現に実際に使用した参照音声は登録する。Irodori-TTS等の参照WAVと、モデル・seed・生成設定を対応づける。
- VOICEVOX等、参照音声を使わない話者は、エンジン・バージョン・話者名・スタイルID・話速などの設定を記録する。登録用の声質参照WAVを新たに作らない。
- 台本・読み・字幕・編集マニフェストは引き続き登録対象。これはStudioへの送信範囲の方針であり、ローカルやGitの採用音声保存方針は変更しない。

ユーザーがセリフ音声の登録を明示した場合はその指定を優先する。解説以外の動画には、この省略方針を自動適用しない。

## 読み取りと対象決定

書き込み前に`list_episodes`と必要に応じて`list_members`を呼び、slugや既存エピソードとの重複を避ける。既存エピソードは`get_episode`で生成バージョン、プロンプト、入力、動画を確認してから変更する。

- エピソード番号を識別子に使わない。Studio内ではランダムな`studio_id`が正本になる。
- slugは内容を表す安定した英小文字・数字・ハイフンで作る。
- 同じエピソードの再生成は新しいエピソードではなく`create_generation`でv2、v3へ追加する。
- `create_episode`はv1を自動作成する。直後に`get_episode`でv1の`generationId`を取得し、最初の生成を登録するためだけに`create_generation`を呼ばない。
- 登場メンバーは`list_members`が返したIDだけを使う。

## 登録ワークフロー（2026-10-09 YouTube移行）

エピソードは通常 `published` とするが、登録したYouTube動画が **公式チャンネル・公開・処理完了・埋め込み可** の全条件を満たすまで公式サイトに掲載されない。取り下げはエピソードを `archived` にする。Studioの制作記録と公式サイトの掲載を区別する。

1. `list_episodes` / `get_episode` と `list_youtube_videos` で既存登録を確認する。動画ID・ローカルの `youtube_upload.json` がある場合は再アップロードしない。
2. 新規なら `create_episode`（v1は自動作成）、新しい制作版なら `create_generation`。`update_generation` の `notes` に台本・出典・クレジット・編集内容を記録できる。
3. 実際に使用した生成プロンプトがある場合だけ `upsert_prompt`。ずんだもん解説、Remotion/Three.js編集などに架空のプロンプトを作らない。上記の「解説動画の音声素材」を含む対象選別を行い、登録対象の画像・音声・資料は `create_input_upload` → PUT → `get_episode` でreadyを確認する。
4. 最新の完成動画をYouTubeへ直接アップロードする。標準720pの完成原本を使い、Studio向けの再圧縮MP4やCloudflare動画サムネイルを新規作成しない。公式チャンネルは `UCyQtPu94OaiGxFdd2A6bXdw`。
5. アップロードがIDを返したら、YouTubeの処理完了を待たず `register_youtube_video` を呼ぶ。`episodeId`, `youtubeId`, 任意の `generationId`, `featured`, `contentKind`, `productionNotes` を渡す。
   - 種類は視聴者向けに `story`（物語）、`explainer`（解説）、`music`（音楽）、`other`（その他）。生成技術で分類しない。
   - 制作ノートは任意。公開する場合 `productionNotes:true` と対象 `generationId` が必要。プロンプト・モデル・入力素材は存在するセクションだけ表示。ノートなしの動画は `productionNotes:false`。
   - 再登録時も種類・ノート・イチオシを明示して、意図せず既存設定を既定値へ戻さない。
6. ユーザーが公開を依頼・採用している場合はYouTubeをpublicにする。通常アップロードはprivate。YouTubeの公開操作とStudioのID登録を混同しない。登録だけを理由に未承認動画を公開しない。
7. `sync_youtube_videos` を一度実行し、`list_youtube_videos` で状態確認。処理中・公開待ちならその状態とIDを報告する。Cloudflare Cronが約5分ごとに継続確認するので、会話を開いたまま待つ必要はない。
8. `ready` かつ `is_active:1` なら公開ページを確認する。差し替えは新IDを同作品に登録し、条件成立まで旧版を維持。チャンネルにある未登録動画は勝手に掲載されない。旧YouTube動画は自動削除しない。

## YouTubeアップロードと再開

MMUリポジトリでは以下を使用する（詳細・JSON形式はリファレンス）。秘密情報は `~/.config/mmu-youtube/`、結果の動画ID・URL・ハッシュは制作物の登録記録へ保存する。

```sh
python3 16_MADOGIWA_STUDIO/tools/upload-youtube.py /absolute/path/final.mp4 \
  --metadata /absolute/path/youtube_metadata.json \
  --record /absolute/path/youtube_upload.json
```

- アップロードは8MiBチャンクで再開可能。ネットワーク失敗・中断は同じコマンドを再実行する。セッションURLやOAuth tokenをログ・Git・チャットへ出さない。
- ID取得前のローカル転送中断はCronでは再開できない。CLIを再実行する。ID取得後のYouTube処理・公開待ちはCronが担当する。
- セッション期限切れはチャンネルを確認して重複投稿を防いでから再発行する。単なる失敗で新しいエピソードを作らない。
- MMU本体がない同僚環境では既存のYouTubeアップロード手段を利用し、返ったIDだけMCP登録する。所有者のOAuthキャッシュを共有しない。

## ギャラリー・記事ワークフロー

- 書き込み前に`list_gallery_items`または`list_articles`でslugと表示順を確認する。
- 新しいギャラリー項目は`draft`で作成し、`create_gallery_image_upload`の一回限りURLへJPEG、PNG、WebPのいずれかをPUTしてから`published`へ変更する。
- ギャラリー画像は10MB以下にし、URL発行とPUTを同じ作業内で連続して行う。アップロードURLは表示・保存しない。
- 記事は外部URL、掲載元、リンク文言まで確認してから公開する。
- 並べ替えは一覧で全対象IDを確認してから`reorder_gallery_items`または`reorder_articles`を使う。
- 物理削除は行わず、取り下げは`draft`または`archived`へ変更する。
- 更新後は一覧を再取得し、公開サイトの表示順、画像URL、公開状態を確認する。

## 入力素材のPUTと既存R2動画

- 入力素材の登録はPUT成功とready確認まで完了させる。チケット発行だけでは完了としない。
- 一回限りURLはBearer相当の秘密情報。返却値のまま使い、表示・保存しない。実ファイルのContent-Typeで送る。
- 公開する制作ノートに紐付いた入力素材のみ公開される。未採用・非公開の制作記録は管理画面に残る。
- `create_video_upload`、`/media/` 動画配信、MP4保存・ファイル共有は廃止。`set_video_status` / `set_video_featured` は旧動画行の保守用で、YouTube掲載設定には使わない。
- 既存R2動画は移行時のバックアップとして残す。新規動画をR2へPUTしない。削除は参照先・ローカル原本・切り戻し期間を確認した別作業とし、入力画像・参照音声・資料をまとめて削除しない。

## 完了報告

作品名、Studio ID、slug、YouTube ID/URL、種類、制作ノート有無、制作記録の対象版と素材、YouTube処理・掲載状態、公開ページURLを簡潔に報告する。「アップロード済み」「公開待ち」「サイト掲載済み」を区別する。
