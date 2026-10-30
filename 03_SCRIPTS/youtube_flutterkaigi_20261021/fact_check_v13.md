# v13 追加説明の根拠（2026-10-31）

- FragmentShader: https://docs.flutter.dev/ui/design/graphics/fragment-shaders
  dart:uiのFragmentProgramから生成しPaint.shaderでCanvasの描画領域の色計算に使う例を説明。ImageFilter.shaderの経路も存在するが今回はCanvas例に限定。独自vertex shader非対応という記載はこのruntime-effect APIの制約で、Flutter GPU全体へ広げない。3D風の表現が一切できないとは説明しない。
- Flutter GPU: https://api.flutter.dev/flutter/flutter_gpu/RenderPipeline-class.html と https://api.flutter.dev/flutter/flutter_gpu/RenderPass-class.html
  vertex/fragment shader、vertex buffer、depth compare/write、描画先を含む描画構成が比較対象。FragmentShaderの廃止や全面的置き換えとは説明しない。
- 「ネイティブ」はOS固有言語でアプリを書く意味と紛らわしいため、対象を「このゲームをiOSやAndroidのアプリとして動かす場合」と明示。図もFlutterエンジンの描画基盤へ統一。
- YouTubeチャプター: https://support.google.com/youtube/answer/9884579?hl=ja
  00:00から開始、3つ以上を昇順、各10秒以上。今回ユーザーの指定により概要欄へ手動チャプターを追加。実測の編集マニフェストから時刻を生成。YouTubeへの公開操作はしていない。
