# YouTube OAuth 受付

専用の Cloudflare Worker と D1。Google Cloud project は `madogiwa-youtube-api`。
公式チャンネル `UCyQtPu94OaiGxFdd2A6bXdw` の所有者がブラウザーで認可する。
YouTube Studio の管理者招待のみでは API の代理認可はできない。

## 初期設定

1. Google Auth Platform のアプリ設定を完了する。
2. Web application の OAuth client を作成し、redirect URI に
   `https://youtube-auth.madogiwa.work/callback` を登録する。
3. Testing の間は `madogiwa.work@gmail.com` をテストユーザーに登録する。
4. ダウンロードした JSON を Git 管理外へ保存し、次を実行する。

```sh
python3 manage.py configure --client-json /absolute/path/client.json
python3 manage.py invite
```

招待 URL は `~/.config/mmu-youtube/owner-invitation.json` に保存される。
所有者本人に渡す。24 時間、一度だけ有効。送信はこのツールでは行わない。
所有者が Google で公式チャンネルを選び、閲覧・アップロードを許可した後に確認する。

```sh
python3 manage.py status
python3 manage.py access-token
```

短期 access token は `~/.config/mmu-youtube/access-token.json` に保存する。
認可だけでは動画を投稿しない。実 API の接続・アップロード試験は所有者の認可後に行う。
Testing の YouTube OAuth refresh token は通常 7 日で失効する。
継続運用では Production 設定と必要な OAuth 審査を確認する。
新規 API プロジェクトの動画公開制限に関する YouTube API audit は別手続き。
同僚のプロジェクトの審査結果がこのプロジェクトへ引き継がれるとは限らない。

## 配置・検証

このディレクトリで実行する。親 Studio の自動生成設定を拾わないよう config を明示する。

```sh
node --test worker.test.mjs
../node_modules/.bin/wrangler types --config wrangler.jsonc
../node_modules/.bin/wrangler deploy --dry-run --config wrangler.jsonc
../node_modules/.bin/wrangler deploy --config wrangler.jsonc
../node_modules/.bin/wrangler secret bulk ~/.config/mmu-youtube/web-secrets.json --config wrangler.jsonc
```

Secrets: `ADMIN_TOKEN`, `TOKEN_KEY` (base64url 32 bytes), `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`。
秘密ファイルは権限 600、ディレクトリは 700。Git に入れない。
Refresh token は AES-GCM で暗号化して D1 に保存し、管理 API でも返却しない。
`ADMIN_TOKEN` を持つ運用者は短期 token を発行できるため、所有者と同等に慎重に扱う。
認可コードが URL に含まれるため Worker observability は無効。
招待を fragment で渡し、ページ表示直後に URL から消す。state・ブラウザー Cookie・PKCE を検証する。
Google アカウントの接続設定からアプリを解除すれば継続アクセスを取り消せる。

## 2026-10-09 の稼働状況

Google project・YouTube Data API・D1・Web OAuth client設定、所有者による認可、Productionへの変更が完了。readonly / upload / force-sslで実APIを利用でき、公開動画88本の状態取得も確認済み。
StudioのCronはこのWorkerの `/admin/access-token` をサービスBinding経由・管理secret付きで呼び、公開状態を同期する。管理secretとGoogle認証情報はGitへ含めない。

参考: https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps
https://developers.google.com/identity/protocols/oauth2#expiration
https://developers.google.com/youtube/v3/docs/videos/insert
