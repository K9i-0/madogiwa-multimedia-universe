from pathlib import Path
import json
P=Path(__file__).resolve().parent;rows=[];scene=view='';md=['# めたんのミステリー研究所 第2回：ちくわ人工物説','\n採用方針：観察・実験・文献調査は妥当。目的や背後関係の推論で陰謀論へ飛躍する。分類・生態・研究内容・T社は作品内の架空設定。\n']
for line in (P/'dialogue.txt').read_text().splitlines():
 if line.startswith('# '):
  scene,view=line[2:].split('|');md.append(f'\n## {scene} / {view}\n');continue
 if line.startswith('@clip|'):
  rows[-1]['clipAfter']=line.split('|')[1];md.append('【過去作クリップ：'+line.split('|')[1]+'】');continue
 if not line:continue
 who,text=line.split('|',1);pause=14 if who=='Z' else 9
 if view in ['followed','leap','arrest','admission','conclusion'] :pause=25
 rows.append(dict(id=f'line-{len(rows):03}',scene=scene,view=view,who='metan' if who=='M' else 'zunda',text=text,pause=pause))
 md.append(f"**{'めたん' if who=='M' else 'ずんだもん'}**：{text}\n")
(P/'dialogue.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));(P/'script.md').write_text('\n'.join(md));print(len(rows),'lines',sum(len(r['text']) for r in rows),'characters')
