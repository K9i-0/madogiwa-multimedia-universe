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
