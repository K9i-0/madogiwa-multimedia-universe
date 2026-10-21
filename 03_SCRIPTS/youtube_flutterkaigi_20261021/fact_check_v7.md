# v7 追加技術解説の裏付け（2026-10-21）

- [Understanding constraints](https://docs.flutter.dev/ui/layout/constraints)：制約を下へ、サイズを上へ、親が位置を決定。幅300に幅100を中央配置する図は、この規則を説明する独自の数値例。
- [Flutter architectural overview](https://docs.flutter.dev/resources/architectural-overview)：Widget / Element / RenderObject、layout、paint、エンジンからGPUへの流れ。図は概念上の流れであり、全Widgetが固有のRenderObjectを持つという意味ではない。
- [Flutter GPU API](https://api.flutter.dev/flutter/flutter_gpu/)：バッファ、シェーダー、RenderTarget、RenderPass、ラスタライズ関連のAPI。
- [RenderPass](https://api.flutter.dev/flutter/flutter_gpu/RenderPass-class.html)：vertex buffer、pipelineのbindとdraw。

通常UIもGPUで描画することを台詞で明示。Flutter GPUをRow/Columnの代替レイアウトAPIとして扱わない。三角形の図は概念説明であり、このゲームのシェーダーの実測可視化ではない。既存のFlutter Scene/SDK/ゲーム検証はfact_check_v3.md・fact_check_v4.mdを継続。
