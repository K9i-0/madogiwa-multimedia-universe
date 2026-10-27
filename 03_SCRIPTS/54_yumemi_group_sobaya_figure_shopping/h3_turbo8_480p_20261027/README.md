# Turbo 8step 480p comparison

2026-10-27ユーザー依頼。同じ30秒の通販題材、同じ入力・プロンプト・seed・純正Ref2VA INT8・LightX2V Turbo Ref2V 8step v1.0・euler/beta・shift 12/3・strength 1・A100・1worker。生成解像度だけ1344×768から864×480に変更する。ref_image_size=matchを維持するため内部の参照画像処理解像度も生成寸法に追従する。縦横比は32pxグリッドのためわずかに異なる。

768p向けのLoRAをそのまま480pで実験する。480pで同等品質を保証しない。768p Turbo版の実測37分50秒を再利用し比較する。生成は362frames×2、完成は各360framesで30秒。480p原本とIrodori音声版を保存し、完成720pはLanczosで縦横比維持・微小余白を追加する。比較は同じ表示領域に768pと480p原本を直接フィット。品質の採否はユーザー、品質リトライなし。

.local/h3-turbo8-480p-20261027のlaunch-detached.pyで起動しmonitor.pyが状態を取得、回収・ハッシュ検証・GPU停止・仕上げを行う。既存動画は上書きしない。
