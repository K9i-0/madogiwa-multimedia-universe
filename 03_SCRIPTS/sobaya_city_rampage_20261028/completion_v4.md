# v4 / v4b 部分再生成・完成編集

ユーザー指示により冒頭と空中移動のみ480P再生成。5秒+7秒の2タスク成功。全編再生成なし。設定・task ID・参照hashはgeneration_v4.json。実費未照会。

採用編集: final_sobaya_brewery_bgm_v4b_720p.mp4。30秒、1280×720、30fps/900frames、48kHzステレオ。480p版と未調整v4版、各生成原本を保持。

更新全編プロンプト: prompt_wan3_v8_standing_instant_flyby.txt。実送信はprompt_wan3_v8_patch_opening.txt / prompt_wan3_v8_patch_flyby.txt。

生成結果は冒頭に走り込みが残り、飛翔の画面通過が約1.3秒だったため無料ローカル編集で補正。冒頭は立ち姿になった30フレーム目から150未満を146フレームへ緩やかに延長。空中移動は18〜57未満の39フレームを11フレーム（約0.367秒）に短縮し、残りは衝撃波の余韻へ配分。効果音も同じ区間でatempo処理、BGMは伸縮せず26〜56秒。詳細はtiming_refinement_v4b.json。

差し替え: [0,146), [350,538)。保持: v3[146,350), [538,900)。 lossless編集中間で保持566フレームのframemd5完全一致を確認。720pへの拡大はlosslessから一度だけLanczos。最終全編デコード成功。コンタクトシートで立ち姿・東京タワー・後着の衝撃波・接続順を目視。全編音声の聴感監査は未実施。飛翔の顔は小さく短いため細部の同一性を完全検証済みとはしない。

再現: python3 refine_v4b.py → python3 assemble_v4b.py → python3 render_bgm_v4b.py。元動画はGit対象外。
