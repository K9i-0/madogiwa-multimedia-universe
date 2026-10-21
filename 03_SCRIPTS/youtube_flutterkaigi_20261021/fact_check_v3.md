# v3 技術・人物・ロゴの確認記録

確認日：2026-10-21。対象ゲーム：`K9i-0/flutterkaigi2026`、実装・性能記録はcommit `4f3ffba1edc84f571723822d583f2c4b44f4a31d`。最新版一般の保証と、今回の実装・測定事例を区別する。

## SDK / 描画

- ゲームの`.mise.toml`はFlutter 3.47.2。実際に`mise exec -- flutter --version --machine`を実行し、`frameworkVersion: 3.47.2`、`channel: stable`、Dart 3.13.2を確認。実行結果のrevisionは`d3b14c876900e553bc736ca19295fc09e3853e8e`。
- ゲームの`app/pubspec.yaml`はFlutter Scene forkを`2606511163ea1144b096f3a7d16b8b85ee0dbc2e`に固定。この取得済みソースの`packages/flutter_scene/README.md:299`にもFlutter 3.47 stable以降と記載。現在の[上流README](https://github.com/bdero/flutter_scene/blob/master/packages/flutter_scene/README.md)とも照合。
- [Flutter GPU設計資料](https://github.com/flutter/flutter/blob/master/docs/engine/impeller/Flutter-GPU.md)は低レベルGPU APIとImpellerへの接続、APIの不安定性を説明。一方でmaster推奨という古い案内も残るため、この資料単独で「Stableでは使えない」とは判断しない。上記の実SDKと固定依存版の要件を根拠に、台詞を「このゲームは3.47.2」「現在のScene案内では3.47以降」と具体化。「最新なら無条件に動く」とは言わない。
- ネイティブはImpellerとFlutter GPUの有効化が必要。今回のiOS/macOSの`Runner/Info.plist`は`FLTEnableFlutterGPU=true`、Androidの`AndroidManifest.xml`は`io.flutter.embedding.android.EnableFlutterGPU=true`。一般の試行コマンドは`flutter run --enable-flutter-gpu`。Webは別バックエンドなので、説明図に「ネイティブ」と明示。
- Flutter Sceneはモデル・カメラ・ライト・アニメーションを扱う層。3D描画に対して通常WidgetでUIを構成。ゲーム内の落下・当たり判定は独自Dart処理であり、Flutter Scene一般に物理機能がないという主張ではない。

## MCPとゲーム独自拡張

- [Dart / Flutter公式説明](https://docs.flutter.dev/ai/tools)とゲームの`.mcp.json`・`.codex/config.toml`を照合。`dart mcp-server --enable=flutter_app_lifecycle`、起動・hot reload・Widget調査・runtime error取得。DTDは開発用接続の概念図であり、すべてのAPI呼び出しが同一経路と断定しない。
- [Marionette開発元](https://github.com/leancodepl/marionette_mcp)と`app/lib/main.dart:29`以降を照合。Bindingをdebug時に初期化し、VM Service経由でWidget操作・画面・ログ確認。Marionette自体の制約と今回の`kDebugMode`条件を混同しない。
- `app/lib/main.dart:109`以降の`madogiwa.inspectCatch`はスコア・座標・落下物等を返す。`madogiwa.catchAction`の`configure`、`start`、`step`を確認。`step`は1/60秒更新を指定回数実行する。センサーの物理操作を代替するという説明にはしない。
- [mobile MCP開発元](https://github.com/mobile-next/mobile-mcp)とプロジェクトの1.0.8固定設定を照合。AndroidはADB、iOSはWebDriverAgent等の端末操作基盤。アプリ内のMarionetteBindingと別経路。表示・操作確認と、フレーム時間・RSSの計測は区別する。

## 実機性能・AIの担当

- [改善commit](https://github.com/K9i-0/flutterkaigi2026/commit/4f3ffba)および`app/qa/device-performance-20261021/README.md`を確認。Pixel 7a Android 14 / Vulkan、iPhone 14 iOS 26.5 / Metal。profile条件下の記録。
- Androidの未変更ライトデータ送信による同期待ちを避ける上流修正の取り込み。約30→60fpsはcommitの要約値。記録のフレーム時間はCPU側で、GPU実行時間やパネル更新頻度そのものではない。動画の注記を修正。
- メモリ約1.9→0.74GB RSSはライブラリ更新と最大2048のゲーム用テクスチャを含む比較。素材縮小だけを独立に測った因果比較として見せない。元モデルの制作素材は保持。
- 同commit末尾のClaude共同著者表記を確認。表記がないcommitを全てCodexと分類しない。Codex中心の機能・画像・簡単な3D制作という担当説明はユーザーの制作情報に基づく。
- `tools/build_chikuwa.py`の形状生成コードを資料画面に使用。人物制作の説明は採用済みTripo解説を参照。

## 人物・公開情報

- ゆめプロの説明、CTO＝Chief Ticket Officer、タスク管理が上手いための愛称、若手社員、福ギュンとそば屋が窓際族であることは今回のユーザー指定を正本にする。Chief Technology Officerとは表示しない。
- [登壇告知](https://www.yumemi.co.jp/flutterkaigi2026_sponsor)とユーザー添付の告知画像に合わせたセッション題名・登壇者・時刻。
- [YouTubeチャンネル](https://www.youtube.com/channel/UCyQtPu94OaiGxFdd2A6bXdw)の公開画面をChromeで撮影。個人のナビゲーション・アカウント領域を除いた範囲を保存。福ギュン・そば屋の採用済み写真を丸型アイコンとして添える。
- 展示後向けの語りはユーザーの制作指定。制作日現在の開催済み事実を新たに主張するものではない。

## ロゴ・概要欄

- [Flutterブランドガイド](https://docs.flutter.dev/brand)と[素材ガイド](https://flutter.dev/brand)を確認。動画チュートリアルは利用例に含まれる。Google公式・協賛と誤認させず、素材の形・色・比率を維持する。
- FlutterロゴはGPU説明の一続きの区間だけ。タイトル、まとめ、MCP説明から削除。概要欄へ商標帰属・非提携文を追加。ガイドのWebページ向け帰属文を、ユーザー指定に従い概要欄にも採用したもので、動画内に常時ロゴを出す必要はない。
- Claudeアイコンはインストール済みAnthropic公式アプリの`ion-dist/images/claude_app_icon.png`を無改変で使用。Codexも既存のOpenAI公式アプリ素材。AIの比較・接続図の紹介対象として表示。
- [Anthropic商標ガイド](https://www.anthropic.com/legal/trademark-guidelines)は事前承認・無改変・非推奨誤認等を記載。素材を取得できたことを許諾取得済みと扱わない。本制作はユーザー指定による紹介用ロゴ配置で、Anthropicから個別許諾を取得した記録はない。投稿は未実施。
