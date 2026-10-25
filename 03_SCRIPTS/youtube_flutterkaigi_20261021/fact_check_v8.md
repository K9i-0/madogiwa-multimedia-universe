# 最新ゲームとの差分確認（2026-10-25）

対象：https://github.com/K9i-0/flutterkaigi2026/commit/5a11e018c4c91e7922e11478bbf8a80a45b95649
ローカルHEADとfetch後のorigin/mainが一致。比較基準はv7の6652753。

- `.mise.toml`、`app/README.md`：Flutter 3.47.8 / Dart 3.13.7。
- `app/lib/gallery.dart`、`gallery_screen.dart`：3Dモデル、クリップ切替、軌道カメラ、ステージ表示。`app/lib/main.dart`：galleryActionとinspectGallery。
- commit 9eb4ea2、`app/lib`のDropKindとモデルロード：chikuwa/toxicChikuwaが同じassetId、toxicのmaterial variantを使用。
- 0481401、8a10c14：ギャラリーはタイトルからのみ開き、街全体を自由に見回せる。
- 看板はJSON定義とアトラス、ビル追加。紹介動画内では更新済みの実画面で反映し、全広告の列挙は行わない。
- b6a6792/6a6ed1fの追加素材最適化は映像へ反映。旧4f3ffbaの実機測定を今回の最新測定と誤表示しない。

収録：Dart MCP debug起動。Marionette MCP 0.6.0はbinding 0.7.0と不一致で接続不可。同じ公開service extensionをDart VM Serviceから直接呼び出し。通常プレイはdemo入力（実センサー操作ではない）、Widget操作はmarionette.tap。iPhone 18 Pro / iOS27.0 / landscape。
