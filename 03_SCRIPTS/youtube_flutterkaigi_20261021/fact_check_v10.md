# v10：Marionette / mobile MCPの使い分け

2026-10-30確認。v9の根拠はfact_check_v9.mdを継承。

## 一次資料

- Marionette公式Concepts: https://marionette.leancode.co/docs/concepts/
  BindingがVM Service extensionを登録。MCP bridgeから呼び出し、キー・文字・Semantics等でWidgetを特定。実機を含むFlutterアプリで利用でき、VM Serviceがあるdebug/profileに対応、releaseは非対応。profileでは利用できる開発機能に制約があるため、全機能同等とは説明しない。
- mobile MCP公式: https://github.com/mobile-next/mobile-mcp
  実機・シミュレーター・エミュレーターでの端末操作。タップ、スワイプ、画面取得等。Flutter専用Bindingは不要だが、OS・端末ごとの接続設定は必要。
- iOS real-device setup: https://github.com/mobile-next/mobile-mcp/wiki/Getting-Started-with-iOS-Real-Device
  WebDriverAgent等の端末側のセットアップ。版で変わり得る内部経路の列挙は今回の動画から省き、接続先と用途に集中。

## このゲームの設定

`/Users/kotahayashi/Workspace/flutterkaigi2026/app/lib/main.dart` の39〜40行付近で `if (kDebugMode) { MarionetteBinding.ensureInitialized(); }`。したがってこのゲームの連携はdebug限定。一般的なMarionetteのprofile対応とは別。

## 台本上の整理

MCP導入 → 今回の用途比較 → 内部／外部の違い → 実機でもMarionetteが使える補足 → Dart MCPの起動・hot reload → Bindingによる操作・専用拡張 → バランス検証 → 実機の操作＋性能測定。

「ほとんどMarionetteで事足りる」「実機の性能調整ではmobileを使用」はユーザーの本プロジェクトでの運用説明。全Flutter開発への普遍的な優劣・性能比較としない。mobile MCPだけが画面要素の構造を扱えないとも説明しない。

mobile MCPは測定のための場面再現・操作を支援する。描画時間とメモリの測定はprofileビルド・別のログを用いる。Marionetteが実機では動かないため使い分ける、という誤説明は避ける。

Columnの読みはユーザー指定により「カラム」。字幕・コードはColumnのまま。共有辞書techスコープ、ASCIIトークン単位に限定し、ColumnWidth等には適用しない。
