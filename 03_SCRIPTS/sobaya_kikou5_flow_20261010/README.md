# そば屋の奇行5選・構成改訂版

59→34→48→76→53。仕事への姿勢、優先順位、行動力、周囲への影響、代理出社という流れ。
自己紹介、自然な語感、短いツッコミ、資料映像後の間を追加。
既存の `sobaya_kikou5_20261010` は保持。

## 再生成

ルートから `python3 <episode>/prepare_assets.py`、`python3 <episode>/generate_voice.py`。
Irodori環境のPythonで `remotion/prepare.py`、`remotion/mix_audio.py`。
remotionで `npm ci`、`npm run typecheck`、`npm run render`。
既存Chromeがあれば `--browser-executable` を指定可能。
`verify.py`でフレーム数・720p・30fps・音声・終端デコード確認。

台詞はdialogue.json、資料範囲はclip_plan.json、生成後の時刻正本はremotion/src/edit-manifest.json。
元動画に含まれる旧名・旧デザインは引用のまま保存。
ASRは台詞照合の補助であり、人耳の通し試聴・精密な口パク監査とは区別する。

## 公開済み改訂2・登録状況

採用動画は`final_remotion_kikou5_revision02.mp4`（361.9秒）。旧MP4・中間動画の削除記録は`cleanup_record.json`。Studio登録完了：MS-NTKH2QT8。YouTube ID `nSvhSLkvZlg`、公開・処理完了・公式サイト掲載済み。採用素材102点はready。制作ノートは非公開。詳細は`studio_registration.json`、素材送信結果は`studio_inputs_uploaded.jsonl`。


## 中国うさぎ・ノーマル音高版（2026-10-13）

ローカル再編集版は `final_remotion_kikou5_usagi_normal.mp4`。たこさん29行を中国うさぎ・ノーマル（style61、速度1.1、音高0）で再生成。やめ太郎28行と引用10区間を維持し、実測尺で字幕・口パク・BGMを再配置。全382.2333秒、11467フレーム、1280×720、30fps。

`方`は`かた`、`その間`は`そのあいだ`、`翌朝`はVOICEVOXの漢字読み（よくあさ）を使用。字幕本文は維持。字幕色は共通メンバー色を参照。声のクレジットを更新。

再生成はルートから `python3 <episode>/generate_usagi.py`、Irodori環境のPythonで `remotion/prepare.py` と `remotion/mix_audio.py`、remotionで `npm run typecheck`、`npm run render`。`verify.py` と `audit_usagi_video.py` で出力・素材同一性・実フレームを確認する。音声設定とクエリは `voice_usagi_record.json`、新音声は `usagi_line*_takosan.wav`。

前版の動画・音声・公開記録を保持。前版台詞は `dialogue_revision02.json`、前版タイミングは `remotion/src/edit-manifest-revision02.json`。新しい説明欄は `youtube_description_usagi.txt`。この再編集版はまだ外部公開していない。
