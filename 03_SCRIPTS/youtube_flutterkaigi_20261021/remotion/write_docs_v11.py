"""Write captions_ja.srt and script.md from the edit manifest and dialogue.txt."""
from pathlib import Path
import json
P=Path(__file__).resolve().parent;m=json.loads((P/'src/edit-manifest.json').read_text())
def ts(f):
 ms=round(f/30*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
out=[];n=0
for d in m['dialogue']:
 for c in d['captions']:
  n+=1;out.append(f"{n}\n{ts(d['startFrame']+c['fromFrame'])} --> {ts(d['startFrame']+c['toFrame'])}\n{c['text']}\n")
(P.parent/'captions_ja.srt').write_text('\n'.join(out))
sec=m['composition']['durationInFrames']/30
lines=[f"# ゆめみ採用試験：Flutter 3DとMCPによる開発・検証 — 改訂v13\n",f"2026-10-31。ずんだもん＆四国めたん。{int(sec//60)}分{sec%60:04.1f}秒。本編挨拶・BGM切替を揃え、FragmentShaderとの比較を追加。3つのツリーを軽く紹介し、技術画面に参考資料を表示。MarionetteはprofileでもVM Service経由で使えることを反映し、MCPの図からmobile MCPを除外。性能の数値は計測条件（固定性能モード）を明示。\n"]
for line in (P/'dialogue.txt').read_text().splitlines():
 if line.startswith('# '):lines.append(f"## {line[2:]}\n");continue
 if not line:continue
 who,view,text=line.split('|',2)
 lines.append(f"**{'めたん' if who=='M' else 'ずんだもん'}**「{text}」\n画面：`{view}`\n")
(P.parent/'script.md').write_text('\n'.join(lines))
print(n,'captions',round(sec,1),'s')
