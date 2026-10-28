# v3生成・BGM編集完了

タスク94190b7d-e896-4198-83c7-bae3fdfd25d7。ユーザー指定の追加1回を実行。Wan3.0-video、480P、30秒、seed281030、参照8枚。送信本文prompt_wan3_v7_sprint_sidepass_lowlanding.txt、実設定wan3_config_v3.json。過去版は保持。

- [BGM付き720p](final_sobaya_brewery_bgm_v3_720p.mp4)
- [BGM付き480p](final_sobaya_brewery_bgm_v3_480p.mp4)
- [元480p](wan3_sobaya_brewery_v3_480p.mp4)

指定曲26〜56秒を映像0〜30秒へ配置し、Wan効果音を残す。render_bgm_v3.pyとedit_manifest_v3.jsonで再現。映像の尺・速度・カット位置は変更なし。720pは元映像からLanczos一度、480pは映像コピー。

## 確認

720p・480pとも最後までデコードしてエラーなし。完成720pは1280×720、30fps、映像音声とも30.000秒、AAC48kHz stereo。最終音量-15.33LUFS、true peak -4.76dBTP。
全編2秒間隔の静止画15枚を目視。助走、横方向の遠方通過、森林への余波、足元の低い着地、長い制動痕、タンクを持って飲む場面を確認。タンクは登場時から小型になり、保持時にも梯子・配管などを残す。
全フレームの寸法不変・人物同一性やフレーム単位の音楽同期を合格としたものではない。発見と終盤で工場の細部・周囲地形に揺れがある。追加の有料再生成は実施していない。
