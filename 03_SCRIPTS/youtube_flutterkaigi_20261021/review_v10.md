# v10 レビューとv11構成案（2026-10-30）

対象: `script.md`（v10、18分04.9秒）。照合先: `flutterkaigi2026` HEAD、pub-cacheの `marionette_flutter-0.7.0`、`flutter_scene@2606511`、Flutter 3.47.8 SDK。

## 1. 技術面の照合結果（優先度順）

| # | v10の発言 | 判定 | 根拠 | 修正案 |
| --- | --- | --- | --- | --- |
| 1 | 「Pixel 7aで約30fpsから約60fpsになった記録」 | 誤解を招く | `app/PERFORMANCE.md` 現状表・冒頭段落。60fpsは固定性能モード（`adb shell cmd power set-fixed-performance-mode-enabled true`）での値。通常モードの実プレイはHUD 46〜50fps、3Dの更新は毎秒約20回 | 「固定性能モードで」と明示。通常モードでは60fpsに届いていないことも一言入れる |
| 2 | 「ネイティブではImpellerとFlutter GPUの有効化が必要」 | 不正確 | flutter_scene README「Impeller…is the default renderer on every native platform as of 3.47」。アプリは `ios/Runner/Info.plist:5` `FLTEnableFlutterGPU`、`android/.../AndroidManifest.xml:6` `EnableFlutterGPU` だけ | 「ImpellerはStableの既定。Flutter GPUだけをInfo.plist／AndroidManifestで有効にする」 |
| 3 | 「実機でパフォーマンスを調整するときは、mobile MCPで端末を操作する」（使い分けの根拠） | 前提が誤り | 下記2章。Marionetteはprofileでも動く。debug限定なのは本アプリの `kDebugMode` ゲート | 2章の使い分けに差し替え |
| 4 | 「ライブラリの更新と素材の縮小を含む改善後は、1.9GBから0.74GB」 | 正しいが経緯を省略 | `app/qa/device-performance-20261021/README.md:9`。同期版はいったん約3.0GBでJetsam強制終了 → 4096²テクスチャを2048²へ縮小して739MB | 「上流同期でメモリが増えて落ちた → テクスチャ縮小で解消」の順に話す方が正確で面白い |
| 5 | 「剛体シミュレーションはしていない」 | このゲームとしては正しい | flutter_scene README: Rapier/box3dの物理、音声、MCP付きエディタを持つゲームエンジンになっている | 「Flutter Sceneには物理もあるが、このゲームは軌道計算で十分なので使っていない」と一言 |
| 6 | Flutter Sceneの紹介 | 不足 | `app/pubspec.yaml` はgit fork `K9i-0/flutter_scene` の固定ref。`app/README.md:248` に独自3コミット（空の補間・同フレームの表示切替・回転のクロスフェード） | 「forkを固定コミットで使っている」と明示。エンジニアは必ず気にする |

問題なしと確認したもの: 描画パイプライン（Widget→RenderObject→paint→エンジン）、Flutter GPUの位置づけ（Impellerの低レベル描画基盤のDart API、Web版はWebGL2バックエンド）、3.47以降（flutter_scene pubspec `flutter: ">=3.47.0"`）、制限時間20秒（`lib/catch_game.dart:48`、`lib/balance.dart:29`）、点光源の毎フレーム転送とVulkanの同期待ち（`app/README.md:248`）、Marionetteの仕組み（BindingがVM Service extensionを登録）。

## 2. Marionetteはprofileで使えるか

**使える（ドキュメント・ソースで確認。実機での動作は未検証）。**

- `marionette_flutter-0.7.0/skills/marionette-flutter-drive-app/SKILL.md:8-9`「debug or profile — never release」、`:252-254` releaseはVM Serviceがないため非対応。
- パッケージ自体はdebug限定ゲートを持たない。`lib/src/widgets/marionette_device_config.dart:23-27` は「profileでもVM Serviceに届くので `kDebugMode` ではなく `!kReleaseMode`」と明記。
- debug限定はこのアプリの選択: `app/lib/main.dart:39`（Binding）、`:144`以降（`madogiwa.inspectCatch` / `catchAction` / ギャラリー拡張の登録）。READMEのクイックスタートが `kDebugMode` 例なので、そのまま採用していた。
- 既存の性能測定もprofileのVM Serviceに接続している（`app/PERFORMANCE.md`「計測の方法」の `tool/scene_rate_probe.py ws://...`）。Marionetteは同じ接続に乗れる。

### profileでできる／できないこと

| | debug | profile | release |
| --- | --- | --- | --- |
| Dart MCP `launch_app` | ○ | ○（`--profile` 指定可） | ○ |
| hot reload / hot restart | ○ | ×（AOT） | × |
| Dart MCP `widget_inspector` | ○ | ×（SDK `widgets/binding.dart:798-811` で `assert` 内登録） | × |
| Marionette 操作・要素取得・スクショ・専用拡張 | ○ | ○（Binding有効時） | ×（VM Serviceなし） |
| DevTools・タイムライン・CPUプロファイル | 目安のみ | ○ | × |

注意: Marionetteは場面を「起こす」道具で、測るのはDevTools／計測ログ（SKILL.md「Performance work」）。要素ツリー走査やスクショはUIスレッドで動くので、計測区間の外で呼ぶ。Bindingが待機しているだけでフレーム時間に影響するかは未計測。

### 使い分けの説明案（v11）

- **Marionette（アプリの中）**: debugでもprofileでも、シミュレーターでも実機でも。debugではhot reloadと組み合わせて作る、profileでは `catchAction` で同じ場面を決定論的に再現し、`inspectCatch` で状態を読みながら測る。
- **mobile MCP（端末の外）**: VM Serviceがないreleaseビルド（TestFlight・ストア版）、OSのダイアログ・ホーム画面・アプリの終了と再起動・低電力モードなどアプリ外の操作、Bindingを入れていないアプリ。
- **どちらも端末は傾けられない**: 傾きの手触りは人が確かめる。自動化するなら専用拡張から入力を注入する。
- 台詞の流れ案: 「最初はMarionetteはdebug専用だと思い込んで、実機の性能調整はmobile MCPで操作していたの。でも実際はprofileでも使える。debug限定にしていたのは、このアプリの設定だったのよ」。誤りを正直に言う方がエンジニアには刺さる。

アプリ側の変更（未実施・要判断）: `main.dart` の2か所のゲートを `!kReleaseMode` にする。収録や台本の前に、macOSまたはiPhone 14で `flutter run --profile` → `connect` → `madogiwa.inspectCatch` が返るかを確認する。

## 3. エンジニア目線の評価

良い点
- 描画の説明が「普段のFlutterもGPUを使う → Flutter GPUは何が違う」の順で、誤解しやすい点（Impellerを置き換えるわけではない）を先に潰している。
- バランス検証でボットの限界（種類・着地位置を知っている）を自分から言っている。数字の扱いが誠実。
- 性能の話が「ポリゴン削減」ではなく、無駄な転送・素材解像度に着地している。

弱い点
- Flutterエンジニアが一番知りたい「実際どのパッケージで、どう組んでいるか」がコードに降りてこない。pubspecを起点にすると解消する（4章）。
- 性能の章に、このリポジトリで最も価値のある知見が入っていない: Flutter Sceneは3Dの描画コマンドをUIスレッドで組み立てるので重さはUI時間に出る、「GPU（raster）」はGPU実行時間ではない、`Scene.maxGpuFramesInFlight = 1` で前フレームを出し直すので「HUD 60fps・3Dは毎秒30回」がありうる（`app/PERFORMANCE.md`「数値の読み方」）。独立した見せ場にできる。
- MCPの章が長く、Dart MCPの紹介がMarionetteの使い分けの後に来ている。起動（Dart MCP）→ 操作（Marionette）→ build modeの順が自然。
- 18分は長め。導入の会社紹介くだりやゆめプロ紹介は維持するにしても、技術パートの重複（v10_usageが3回登場）を整理できる。

## 4. pubspec.yaml起点の構成案

`app/pubspec.yaml` の直接依存は11個。均等に回らず、3段に分ける。pubspecの画面を「地図」として章の切り替わりで再表示し、今どの依存の話かをハイライトする。

**A. 章を立てる（5個）**

| 依存 | 話すこと | 既存素材 |
| --- | --- | --- |
| `flutter_scene`（git fork・固定ref） | v9の描画解説（Widget→Flutter GPU→Scene）をここへ。forkの理由と独自3コミット、Flutter GPUの有効化フラグ | `v9_*`、`scene`、`stable` |
| `hooks` | `hook/build.dart` がビルド時に10個のGLBをFlutter Scene形式へ変換（`flutter_scene/build_hooks.dart` の `buildScenes`）。初回ビルドが遅い理由。ここから「そのGLBはどう作ったか」でTripo／ちくわの章へつなぐ | `model_flow`、`chikuwa_*`、`tripo` |
| `madogiwa_engine`（path） | モノレポの共有パッケージ。このアプリは `scene.dart` の `CharacterMotionPlayer`（共有時計で複数クリップのウェイトとseekを制御し、Idle/Walkをブレンド）だけを使う。衝突・認知記憶は `labs/sobaya_hazard` 側で利用。v9の「研究の蓄積」をパッケージとして具体化する | `v9_research`、`gallery_model` |
| `sensors_plus` | `lib/tilt_input.dart`: 加速度計を16ms間隔で購読 → 指数平滑のローパス → `atan2` で角度 → 13.75°で最大、6%のデッドゾーン → 最初のサンプルで自動キャリブレーション。シミュレーターは矢印キー。実プレイのCPUではプラットフォームチャンネル受信が約3%（`PERFORMANCE.md`）。「軽く触れる」なら30〜40秒 | `logic`、`game_odatetsu` |
| `marionette_flutter` | dev_dependenciesではなく通常の依存（Bindingを `main()` で初期化するため）。コンパイル時定数の分岐でreleaseでは動かさない。ここからMCPの章へ入り、2章の使い分けを説明 | `v10_*`、`custom_extension`、`deterministic` |

**B. 1枚でまとめる（6個）**: `vector_math`（Flutter Sceneと共通の3D数学）、`shared_preferences`（端末内ランキング・設定）、`audioplayers`（カウントダウン音）、`qr_flutter`・`url_launcher`（ブースで見せる「このアプリについて」のリポジトリQR）。ブース展示ならではの依存として軽く笑いにできる。

**C. pubspecの外**: Dart MCP・Marionette MCP・mobile MCPは `.mcp.json`、Flutter SDKは `.mise.toml` の3.47.8。「pubspecに載らない開発ツール」としてMCP章の冒頭で見せる。

### 章立て案（v11）

1. intro・game（v10を維持）
2. **pubspec.yamlを開く**（新規の地図画面）
3. `flutter_scene`: 描画の仕組み（v9を圧縮）＋fork＋有効化フラグ（#2修正）
4. `hooks`: ビルド時のGLB変換 → モデル制作（Tripo・ちくわ）
5. `madogiwa_engine`: アニメーション再生と研究の蓄積・開発期間
6. `sensors_plus`: 傾き入力 → ゲーム設計・ロジック（物理を使わない理由、#5）
7. `marionette_flutter`: Dart MCPで起動 → Marionetteで操作 → 専用拡張 → バランス検証
8. 実機とprofile: Marionetteはprofileでも使える（#3）、mobile MCPの役割
9. 性能: UI時間に出る3Dの重さ、HUD fpsと3Dの更新回数の違い、固定性能モード（#1）、メモリの経緯（#4）
10. B群のまとめ → ending

既存の図・収録を各依存に割り当てたので、v11の初版は新規画面（pubspec地図、hook、tilt、profile表、HUD fps vs 3D更新）5〜6枚の追加で作れる。
