from pathlib import Path
import json
P=Path(__file__).resolve().parent;rows=[];scene=view='';md=['# めたんのミステリー研究所 第2回：ちくわ人工物説','\n採用方針v8：ずんだもんは「ちくわは生き物」という世界の常識を最後まで守る。めたんと研究員が、観察・実験から人工ちくわ流通説を唱え、さらに陰謀論へ飛躍する。人工ちくわと政府・企業による隠蔽は作品内で実在。林・江本は登場させない。分類・生態・研究内容・T社は作品内の架空設定。\n']
for line in (P/'dialogue.txt').read_text().splitlines():
 if line.startswith('# '):
  scene,view=line[2:].split('|');md.append(f'\n## {scene} / {view}\n');continue
 if line.startswith('@clip|'):
  rows[-1]['clipAfter']=line.split('|')[1];md.append('【過去作クリップ：'+line.split('|')[1]+'】');continue
 if not line:continue
 who,text=line.split('|',1);pause=14 if who=='Z' else 9
 if view in ['followed','leap','arrest','admission','conclusion','additional_charge'] :pause=25
 if text.endswith('今日は、この謎に迫るわ。'):pause=36
 if view in ['handoff_history','handoff_market']:pause=18
 if text.startswith('ここで、中口研究員'):pause=33
 if text.startswith('毒ちくわを、一匹'):pause=36
 if text.startswith('……昨日'):pause=32
 if text=='まず服を着てから告発するのだ。':pause=30
 rows.append(dict(id=f'line-{len(rows):03}',scene=scene,view=view,who='metan' if who=='M' else 'zunda',text=text,pause=pause))
 md.append(f"**{'めたん' if who=='M' else 'ずんだもん'}**：{text}\n")
md.append('\n## 編集上の間・資料開示・真相カット\n\n採用版の編集仕様は revision_v8.md、整数フレームと発話同期キューは remotion/src/edit-manifest.json を参照。\n')
(P/'dialogue.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));(P/'script.md').write_text('\n'.join(md));print(len(rows),'lines',sum(len(r['text']) for r in rows),'characters')
