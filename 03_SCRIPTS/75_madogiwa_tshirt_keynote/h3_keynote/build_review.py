from pathlib import Path
import json,html
p=Path(__file__).resolve().parent;spec=json.loads((p/'scene_specs.json').read_text());audio={r['id']:r for r in json.loads((p/'audio_manifest.json').read_text())}
parts=['<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>H3 基調講演・シーン参照</title><style>body{background:#111827;color:#eef2ff;font-family:system-ui;margin:32px auto;max-width:1440px;padding:0 20px}h1{font-size:28px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:24px}article{background:#1f2937;border-radius:12px;overflow:hidden;padding-bottom:16px}img{width:100%;display:block}h2,p,details{margin:16px}audio{width:100%;height:32px}summary{cursor:pointer}small{color:#cbd5e1}</style><h1>窓際族Tシャツ発表会 — H3シーン参照</h1><p>スクリーンの静止スライドを含めてH3で生成。字幕はRemotion。画像をクリックすると原寸、台詞欄で採用済み音声を再生できます。</p><main>']
for s in spec:
 img=f"scenes/{s['id']}.png";parts.append(f'<article><a href="{img}"><img src="{img}" loading="lazy"></a><h2>{html.escape(s["id"])}</h2><details><summary>台詞と音声（{len(s["lines"])}本）</summary>')
 for idx in s['lines']:
  r=audio[idx];parts.append(f'<p>{html.escape(r["text"])}<audio controls preload="none" src="{r["input"]}"></audio></p>')
 parts.append('</details></article>')
parts.append('</main></html>');(p/'review.html').write_text('\n'.join(parts))
