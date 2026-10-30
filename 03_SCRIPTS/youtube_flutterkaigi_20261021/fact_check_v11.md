# v11 技術照合（2026-10-30）

v9・v10の根拠は各fact_checkを継承。照合先はflutterkaigi2026 HEAD `08b2161`、pub-cacheの`marionette_flutter-0.7.0`、`flutter_scene@2606511`、Flutter 3.47.8 SDK。詳細なレビューは`review_v10.md`。

## 修正した発言

- Pixel 7a 約30→60fps：`app/PERFORMANCE.md`「現状」。60fpsは固定性能モードの値。通常の電力モードの実プレイはHUD約46〜50fps、3Dの更新は毎秒約20回。台詞と図に条件を明示した。
- Impellerの有効化：flutter_scene README「Impeller…is the default renderer on every native platform as of 3.47」。有効化が必要なのはFlutter GPUだけ（`ios/Runner/Info.plist` `FLTEnableFlutterGPU`、`android/app/src/main/AndroidManifest.xml` `EnableFlutterGPU`）。
- メモリ：`app/qa/device-performance-20261021/README.md`。上流同期版はiPhone 14で読み込み時に強制終了（Jetsam、ピーク約3.0GB）。旧版RSSピーク1.9GB、2048²へ縮小後739MB。
- 物理：flutter_scene READMEにRapier/box3dの物理がある。このゲームは軌道計算で、剛体シミュレーションを使わない。
- MCP：`marionette_flutter-0.7.0/skills/marionette-flutter-drive-app/SKILL.md`「debug or profile — never release」。releaseはVM Serviceなし。profileではhot reload不可（AOT）。Flutterのウィジェットインスペクタ拡張はSDK `widgets/binding.dart` で`assert`内登録のためdebugのみ。

## 追加した説明

- pubspec：`app/pubspec.yaml`の直接依存10個（Flutter SDK除く）。flutter_sceneはgit fork `K9i-0/flutter_scene` @`2606511`。独自3コミット（空の補間・同フレームの表示切替・回転のクロスフェード）は`app/README.md`のPixel 7a節。台詞では「アニメーションの切り替えまわりの小さな修正」とした。
- hooks：`app/hook/build.dart`が10個のGLBを`buildScenes`へ渡す。`flutter_scene/build_hooks.dart`がビルド時に`.fsceneb`へ変換し、`flutter_scene_generated/`へ出力。
- madogiwa_engine：`packages/madogiwa_engine/README.md`。衝突・レイ判定、視認・聴覚の認知記憶、モーション時計。アプリは`scene.dart`の`CharacterMotionPlayer`だけをimport（`catch_scene.dart`、`gallery_screen.dart`）。重みとseekで複数クリップを再生。
- sensors_plus：`app/lib/tilt_input.dart`。`accelerometerEventStream(samplingPeriod: 16ms)`、`1-exp(-dt*14)`の平滑化、`atan2`で角度、`maxDegrees=13.75`、6%のデッドゾーン、初回サンプルとラウンド開始等で`calibrate()`。シミュレーターは矢印キー（`main.dart`）。
- marionette_flutter：通常のdependencies。`main()`で`MarionetteBinding.ensureInitialized()`。
- Flutter Sceneの再表示：`app/PERFORMANCE.md`「数値の読み方」「端末差の考察」。`Scene.maxGpuFramesInFlight = 1`、UIスレッドで3Dを組み立て、通常モードのPixel 7aは3フレームに1回。
- ブース部品：shared_preferences（`records.dart`・設定）、audioplayers（`countdown_audio.dart`）、qr_flutter・url_launcher（`about_dialog.dart`）。

## profileでの動作確認

2026-10-30、macOSのprofileビルドで確認。`app/lib/main.dart`の2か所のゲートを`kDebugMode`から`!kReleaseMode`へ変更（未コミット）。`connect`、専用拡張4件の一覧、`madogiwa.inspectCatch`、`catchAction`の`start`・`step`、Widget要素の取得が成功。スクリーンショットはアプリ側で撮影成功（3D描画を含む）だが、Marionette MCPのツール応答は内部エラー（画像サイズの問題と推定、未確定）。実機（iPhone）は未ペアリングで未確認。

画面のmain.dartは`!kReleaseMode`を表示している。ゲームリポジトリへゲート変更を採用しない場合は、この画面と「profileでも実際に操作できる」の台詞を見直す。

## 既存の映像

ゲーム映像は2026-10-30にiPhone 17 Pro（iOS 26.5）シミュレーターのdebugで再収録。`--dart-define=CAPTURE=true`で結果ダイアログを出さない（`main.dart`の`checkRoundEnd`、未コミット）。撮影用自動入力`action=demo`を使用。性能測定映像ではない。

# v12 追記：公式ドキュメントとの照合（2026-10-30）

画面右下の「参考」は `remotion/src/Explainer.tsx` の `refs`。各URLのHTTP 200を確認。

| 台本の説明 | 照合した資料 | 結果 |
| --- | --- | --- |
| Widgetのツリーからelementのツリー、配置・描画にかかわるelementがRenderObjectを持つ。elementはフレームをまたいで残る | docs.flutter.dev/resources/architectural-overview | 一致。「one element for every widget」「RenderObjectElement…intermediary」「element tree is persistent from frame to frame」。全Widgetが RenderObjectを持つとは言わない（図はColumn→RenderFlex、文字はRenderParagraphなど、とした） |
| レイアウトは親が制約を渡し、子が大きさを返す | 同上 | 一致。「passes down size constraints」「passing up a size」 |
| エンジン・ImpellerがGPUで描く | 同上、docs.flutter.dev/perf/impeller | 一致 |
| ImpellerはStableの標準 | docs.flutter.dev/perf/impeller | iOS・Android（API 29+）は3.27から、macOS・Linux・WindowsはFlutter 3.47から既定。古いAndroidやVulkan非対応はOpenGLへフォールバック。台詞は「ネイティブの標準」の範囲で一致 |
| Flutter GPUはAPIの安定性が保証されない | github.com/flutter/flutter docs/engine/impeller/Flutter-GPU.md、api.flutter.dev/flutter/flutter_gpu | 一致（「early preview…does not guarantee API stability」）。ただし同文書は「master channel」と記載し、flutter_scene（3.47 stable以上）やこのアプリの3.47.8と食い違う。有効化フラグはflutter_sceneのREADMEとアプリのInfo.plist／AndroidManifestを根拠にした |
| Flutter Sceneは3.47以降 | fscene.dev/getting-started、pub.dev/packages/flutter_scene | 一致（「needs Flutter 3.47 (stable) or newer」） |
| hooksはビルド時に実行 | dart.dev/tools/hooks | 一致（`hook/`のDartスクリプト、ビルドの過程でSDKが自動実行、`package:hooks`の`build`） |
| sensors_plusの加速度センサー | pub.dev/packages/sensors_plus | 一致（重力を含む加速度、samplingPeriod指定可。Androidでは間隔が保証されない） |
| Dart MCPの起動・hot reload・Widget調査・実行時エラー、DTD | github.com/dart-lang/ai/tree/main/pkgs/dart_mcp_server | 一致。`launch_app`は`flutter_app_lifecycle`で有効化。debugまたはprofileのFlutterアプリはDTDに自動登録 |
| Marionetteはdebug・profile、releaseは不可。releaseに残さない | marionette.leancode.co/docs/concepts | 一致（「VM service exists in debug and profile builds, never in release」「compile-time constants, so the release binary contains no Marionette code」） |
| profileでhot reload不可、性能はprofile・実機で測る | docs.flutter.dev/testing/build-modes | 一致（「Hot reload works only in debug mode」「Measure performance in profile mode on an actual device」）。シミュレーターはprofile不可のため、profileの動作確認はmacOSで実施 |
