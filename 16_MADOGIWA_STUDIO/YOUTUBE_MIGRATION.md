# YouTube移行記録 — 2026-10-09

- 本番 `https://madogiwa.work` に反映。YouTube 87既存作品 + アーロンチュア解説1作品 = 88作品。
- 未対応の3作品は公開カタログ・詳細・サイトマップから除外。Studio記録は保持。
- 迷言集は対応本編がある19件。「ビールのために脱獄」は本編ID未登録のため非掲載。
- YouTube公開・処理完了・埋め込み可を5分Cronで確認。管理画面の同期から本番Worker→OAuth Worker→YouTube API→D1の更新成功を確認。
- ずんだもん解説はexplainer、制作ノートなし。プロンプトなしでも動画公開可能。
- D1は変更前にprivate configへexport済み。R2動画161行、合計2,302,413,812 bytesは削除していない（クリップR2は別）。
- 旧動画配信・新規R2アップロードは410。画像・参照音声・資料は継続。

## 検証

型チェック・lint、Worker/Webテスト54件、OAuthテスト11件、build、startup、deploy dry-runを通過。
本番APIは88件すべてYouTube IDあり。ホーム、動画一覧、人物、世界観、制作ノート、ノートなし解説、迷言一覧・詳細、サイトマップのHTTP検証を実施。除外ページ404・旧動画410も確認。
ブラウザーでタコゲーム・ヒソバの範囲指定YouTube再生、3テーマの固定おすすめ、ノートなし表示、管理同期を確認。
YouTubeの時間指定はフレーム単位の切り抜きではない。版差分の全フレーム照合は未実施。既存タイトル・説明の制作ページURLで紐付けた対応表をaudit JSONへ保持。

## 今後の登録

`.claude/skills/madogiwa-studio/SKILL.md` を使用。完成動画を直接YouTubeへ転送→IDをregister_youtube_video→YouTubeで公開→Cronが掲載。転送中断はupload-youtube.py再実行、ID取得後の処理待ちはCron。

## R2削除

移行直後は保持。後日、ゲーム等の別参照・原本保管・切り戻し期間を確認して動画キーだけを削除する。入力画像・音声・資料・ギャラリーを削除対象へ含めない。
