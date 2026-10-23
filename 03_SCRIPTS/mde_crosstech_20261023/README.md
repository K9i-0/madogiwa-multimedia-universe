# 窓際クロステック：MDE育成現場に潜入

正本台本は `script.md`、発話本文は `dialogue.json`、生成条件は `voice_generation_record.json`、編集時間軸は `remotion/src/edit-manifest.json`。

## 再現

リポジトリルートから実行する。既存採用WAVがある場合、音声生成はスキップされる。台詞を変更するときは該当WAVを候補置き場へ退避し、生成記録と字幕を更新する。

```bash
python3 03_SCRIPTS/mde_crosstech_20261023/generate_voice.py
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/mde_crosstech_20261023/audit_voice.py
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/mde_crosstech_20261023/make_score.py
python3 03_SCRIPTS/mde_crosstech_20261023/prepare_edit.py
python3 03_SCRIPTS/mde_crosstech_20261023/align_captions.py
cd 03_SCRIPTS/mde_crosstech_20261023/remotion
npm ci
npm run typecheck
node render-stills.mjs
npm run render
```

`prepare_edit.py` は採用音声の実測尺から全体を配置し、共有素材をpublicへhardlinkする。`align_captions.py` はASR句単位の時刻へ表示原文を照合する。`prepare_edit.py` の再実行で暫定字幕時刻へ戻るため、後に必ずalignを実行する。音声や映像の速度は変えない。

## 編集仕様

- 1280×720 / 30fps、Remotion 4.0.538。
- Irodori：そば屋はv4-Large + 正典monsterize、アナウンサーはv4.1-Small。各WAVを-18 LUFS目標へ整音。
- 新規インタビュー映像は文字なし静止画への緩い寄り。人物のリップシンク動画を生成したものではない。
- 文字なし静止画は内蔵Imagegenで制作。入力は先に採用したMDE記事画像、実送信プロンプトは `prompt_interview_clean.txt`、採用出力は `interview_clean.png`。
- 59話の文字なし映像、51話の工作、チュアゴスティーニの文字追加前映像を再利用。通常Bロールはミュートし、51話の着座区間だけ原音を使う。
- 福ギュンの新規テロップは改名後の表記。過去映像内の名札は原素材を保持。
- 名言は今回指定の「窓際社員」で新録。59話の原発話「窓際族」と区別して表示。
- オリジナルBGMは `make_score.py` で生成。第三者の楽曲・サンプルを使用しない。
- 元ネタのYouTube本編は構成・意匠の参照のみ。映像・音声の転載なし。
- 出演者字幕色は共有の `00_TEMPLATES/subtitles/member-colors.ts` を直接参照。

## 検証の区別

ASRは台詞照合と字幕時刻の補助であり、声質・自然さ・音声の通し試聴を保証しない。最終監査結果は `qa_report.json` に記録する。採用素材、PNG、MP4のフレーム目視とデコード検証、音声の聴覚検証を分けて扱う。

完成動画・候補音声・監査画像・publicの再生成可能素材はGit管理外。採用セリフWAV、入力静止画、編集コード、lockfile、台本・軽量記録を管理する。

## FB改訂版（2026-10-23）

本編のみ。改訂出力：`final_remotion_mde_v2_16x9.mp4`。初稿は `remotion/out/before_feedback_v1.mp4` に保持。
「人材」→「人罪」は同音の表記変更で、音声の生成履歴は改変しない。

採用画像18点は `scene_images/`、各最終プロンプトは `prompt_*.txt`、生成方式・参照元・ハッシュは `image_generation_record.json`。すべて built-in image_gen で生成。窓越しの外壁席は漫画3話、落下現場は漫画6話を参照。静止画にカメラ移動を付けた編集であり、新規発話動画ではない。

取材場所：執務席 → 窓際 → 外壁ベランダ（室内から窓越し）→ 窓際落下現場 → 居酒屋 → 二軒目 → 駅ホームで酔いつぶれる。資料映像を挟みつつ進む。

再現：`python3 prepare_edit.py` → `python3 align_captions.py` → `python3 validate_edit.py` → `cd remotion && npm run typecheck && npm run render`。
ショートは本編へのFB反映後、YouTube投稿段階で初めて作る。

最終追加FB：二軒目の取材後、アナウンサーの締めを駅ホームのベンチで酔いつぶれたそば屋へ重ねる。末尾の企業スローガンは削除し、同カットの余韻で終了。仮面は装着したまま。

完成確認：7883フレーム、4分22.77秒。全編デコードと音量検証済み（-17.96 LUFS、-1.95 dBTP）。`npm run render` はRemotionのraw出力後に `finalize_audio.py` で音声のみ整音し、映像をストリームコピーする。音声の通し試聴は未実施。詳細は `qa_report.json`。

## 2026-10-23 YouTube公開・本編誘導ショート

- 本編：https://www.youtube.com/watch?v=TRf4LlHUNrc （public / processing succeeded、最初のタイトル案とヘッダー画像のサムネを採用。表記は最新指定の「新人罪」）
- Studio：mde-crosstech / MS-FGYYX22B。YouTube ready / active、制作ノート非掲載。
- ショート：`final_remotion_shorts_9x16.mp4`。720×1280、30fps、1421フレーム、47.3667秒。YouTube公開：https://www.youtube.com/shorts/5QWz-ph1qUs
- 採用範囲：本編フレーム90〜1451未満（3秒〜48.3667秒）。「エクセルを開く」から「最初から、窓際にデプロイされているんです」まで。末尾2秒に本編案内。
- 再生成：`cd remotion && npm run render:short`。字幕と資料画面を縦に再配置し、音声は採用本編からフレーム単位で抽出。発話後の無音部で0.3秒フェード、案内2秒は無音。
- 監査：全1421フレームのデコード成功、全字幕14カード中間・冒頭末尾の画像確認。AAC再エンコード前後の音声相関0.99986。通し聴取は未実施。
- 公開記録は `youtube_upload.json` / `youtube_verified.json` / `youtube_thumbnail_record.json`。ショート仕様は `remotion/src/shorts-manifest.json`、監査は `shorts_audit.json`。
