# v8 / v8b 空中移動・最後3秒の部分修正候補

ユーザー承認分のみ: 空中移動7秒720P、飲酒3秒720Pの2タスク。task ID等はgeneration_v8.json。動画料金概算0.70 USD、実請求未照会。森参照は内蔵image_genによる新規作成reference_forest_v8.png。実プロンプトprompt_image_forest_v8.txt、参照記録reference_manifest_v8.json。画像の画素数増加を保証するものではなく、樹冠と奥行きの分離を改善する目的。

飲酒のfirst_frameはv7生成原本の810フレーム目（27秒）、PNGを無加工抽出。first_frameモードのため追加のreference_imageは同送せず。開始の構図は継承するが、生成結果は口元から地面へ大量に流れる動きが残り、ユーザーが求める飲酒修正は未達。完全合格とはしない。追加の有料再試行なし。

空中移動の新生成は約1秒の通過が残ったため、ユーザーの条件付き許可に従いローカル編集で短縮。ソース[18,54)の36フレームを11フレーム（0.367秒）へ圧縮、前18フレームと残りの衝撃波を合わせ189フレームへ。詳細timing_refinement_v8b.json。木の前景・中景の分離は変わったが、動く細部の粗さは残り、全面的な画質改善を断定しない。

差し替えはv7[350,539)、[810,900)。その他621フレームはlossless中間でv7とframemd5一致。30秒900フレーム、1280×720、48kHzステレオ。完成全編デコード成功。音楽26〜56秒とゲイン、序盤7.8秒生成音除去を保持。全編の聴感監査は未実施。

納品候補final_sobaya_brewery_bgm_v8b_720p.mp4、短縮前比較final_sobaya_brewery_bgm_v8_720p.mp4。旧版v7を保持。各生成原本も保持。再現refine_v8b.py → assemble_v8b.py → render_bgm_v8b.py。全編用の次回プロンプトprompt_wan3_v10_forest_controlled_drink.txtも更新したが、この全編プロンプトは未送信。
