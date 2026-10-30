# v9 技術・開発履歴の照合（2026-10-30）

## 描画

- Flutter公式Architecture: https://docs.flutter.dev/resources/architectural-overview
  Widgetは構成、RenderObjectは配置・ペイントを担い、エンジンが合成されたシーンをラスタライズする。概略を4段階に整理。Elementの詳細・制約の数値例は省略。
- Flutter GPU API: https://api.flutter.dev/flutter/flutter_gpu/
  低レベル描画API。DeviceBuffer, Shader, RenderPass, RenderTarget, DepthStencilAttachment等。
- Impeller: https://github.com/flutter/flutter/blob/master/engine/src/flutter/impeller/README.md
  impeller/renderer（低レベル）とimpeller/entity等のUI描画を区別。「Impellerは2D専用なので置換する」としない。
- Flutter GPU: https://github.com/flutter/flutter/blob/master/docs/engine/impeller/Flutter-GPU.md
- Scene: https://fscene.dev/getting-started/ / https://pub.dev/documentation/flutter_scene/latest/scene/
  ネイティブでFlutter GPUとImpellerを使う3D描画ライブラリ。Stable SDKとAPI安定性を区別。

## 開発期間

ゲームrepositoryの確認HEAD: `08b21618ac22a61b38ee78428d8f04ba69e1c470`（10月28日）。
`git log --date=short --format='%h %ad %s' -- app`で確認。

- `f47a416` 10月2日：横画面の試作。
- `ca42535`, `f39df9b`, `033907b` 10月20日：キャラクター、専用落下物、展示タイトル。
- `d710997`, `4f3ffba` 10月21日：ブース向け機能・実機性能。
- `9fefd6d`, `332b47d`, `c166401`, `e77c332` 10月27日：100点採点、固定配置、判定猶予、配置再選定、カウントダウン。

履歴にある日付は作業時間の記録ではない。「約1〜2週間」は作者の記憶と集中期間による概算。7月から継承したMMU全体の初回コミットを本ゲーム開始日と数えない。元のMMUには9月以前のFlutterゲーム研究があり、`21_SOBAYA_HAZARD_LAB`等のモデル・移動・描画負荷の蓄積を参照。20秒ゲームの企画上の苦労はユーザー本人の制作証言。

## バランス

固定参照： https://github.com/K9i-0/flutterkaigi2026/tree/08b21618ac22a61b38ee78428d8f04ba69e1c470/app

- `README.md` の「100点満点」「当たり判定のゆるさ」：来場者目標90/50/5%、200体のボット、0.15秒猶予、seed 60→8、77%の採用理由。
- `tool/balance_sim.dart`：ゲーム本体を自動実行。反応と操作誤差、種類・着地位置既知というモデル化の限界。
- `test/layout_test.dart`：難易度順とTAS満点。現在のnormalボット率は70〜90%の範囲。
- `lib/catch_game.dart`：100点満点・80点で合格。

READMEの先頭表には古いseed 60時点の62%が残る。後段の採用更新（seed 8、77%）を使った。来場者の実測合格率・クリア率目標の達成保証にはしない。AIが映像を見て200回操作したとは説明せず、AIが作る自動プレイプログラムの話にした。

## 既存の映像・計測

導入と既存のゲーム素材はユーザーが評価したv8の10月25日収録版を維持。新しい採点やバランスは図で説明する。inspect画面はv8収録時のデータで、新しい固定配置の結果ではない。性能の数値は既存の4f3ffba実機profile記録を維持し、今回測定した値としない。
