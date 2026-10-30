# v14 裏取り（2026-10-31）
- GPU APIはFlutter 3.47.2 SDK engine/src/flutter/lib/gpu/lib/src/context.dart / render_pass.dartと公式API https://api.flutter.dev/flutter/flutter_gpu/RenderPass-class.html を照合。createRenderPipeline(Shader,Shader)、bindPipeline、bindVertexBuffer(BufferView)、draw(int)。サンプルは初期化・バッファ等を省いたAPI抜粋で、完成アプリや同一結果のコード量比較ではない。
- Scene APIは採用flutter_scene@2606511のpackages/flutter_scene/example/README.mdとゲームapp/lib/drop_models.dart。loadScene(assetPath)で変換済みモデルをロード、scene.add、SceneView(scene,camera:PerspectiveCamera(position:eye,target:center))。読み込み後・初期化済みを前提にした抜粋。
- Tripo公式 https://www.tripo3d.ai/ および https://www.tripo3d.ai/research ：画像・テキストから3D、3D生成の専用AIモデル。特定の公開モデルと商用サービスの内部モデルを同一視しない。ロゴは採用済みTripo解説inputs/webrefs_v3/tripo_logo.svgを再利用。
- ちくわ：tools/build_chikuwa.pyでは通常/毒でbase-color textureを変更。roughness、normalは共有。recolor_chikuwa_variant.pyもbase colorのみ転送。app/lib/drop_models.dartではMaterialsVariantsComponent.selectでマテリアルを選択。映像では「テクスチャ切替」と説明し、実装の選択単位も補足。
- Marionette Issue #27はK9i-0の提案。PR #30はメンテナーが作成・マージし、K9i-0のコードをほぼそのまま使い登録/発見を追加したと明記。PR commits APIからK9i-0の3件 e5d1abb / 42010d6 / bbe0883 を確認。単独開発・PR作成者とは説明しない。
  https://github.com/leancodepl/marionette_mcp/issues/27
  https://github.com/leancodepl/marionette_mcp/pull/30
- GitHubスクリーンショットはcapture_github_v14.cjsで実ページを取得。周辺UIを切り出し、内容改変なし。コミット一覧の右/下カードはAPIで確認した履歴の要約。
- 50%はおだてつの来場者目標、77%は200体ボットの採用配置(seed 8)での検証結果。ボットの約80%が配置比較の目安。人の50%を保証する校正ではない。v9のゲームREADME検証を継承。
