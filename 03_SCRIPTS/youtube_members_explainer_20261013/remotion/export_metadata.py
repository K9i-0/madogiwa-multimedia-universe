from pathlib import Path
import json
P=Path(__file__).resolve().parent;m=json.loads((P/'src/edit-manifest.json').read_text())
titles={'intro':'窓際族物語とは','sobaya':'そば屋','fukugyun':'福ギュン','tokun':'とーくん','yametaro':'やめ太郎','yotan':'よーたん','okayaman':'おかやまん','takosan':'たこさん','yumemin':'ゆめみん','ending':'まとめ'}
chapters=[]
for c in m['chapters']:
 t=int(c['startFrame']/30) if c['id']!='intro' else 0;chapters.append(f"{t//60:02}:{t%60:02} {titles[c['id']]}")
f=P.parent/'youtube_description.txt';s=f.read_text().split('\nチャプター\n')[0];f.write_text(s+'\nチャプター\n'+'\n'.join(chapters)+'\n')
def stamp(fr):
 ms=round(fr/30*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
rows=[]
for d in m['dialogue']:
 for c in d['captions']:rows.append({'from':d['startFrame']+c['from'],'to':d['startFrame']+c['to'],'text':c['text']})
for cc in json.loads((P/'src/clip-captions.json').read_text()):
 c=next(c for c in m['clips'] if c['id']==cc['clip']);rows.append({'from':c['startFrame']+cc['from'],'to':c['startFrame']+cc['to'],'text':cc['text']})
rows.sort(key=lambda x:x['from']);lines=[f"{i+1}\n{stamp(r['from'])} --> {stamp(r['to'])}\n{r['text']}\n" for i,r in enumerate(rows)]
(P.parent/'captions_ja.srt').write_text('\n'.join(lines))
# Audio reconstruction needs only adopted WAVs. Preserve unused takes in ignored out/.
used={d['audio'] for d in m['dialogue']};unused=P/'out/unused_voices';unused.mkdir(exist_ok=True)
for f in P.parent.glob('voice_*.wav'):
 if f.name not in used:f.rename(unused/f.name)
f=P.parent/'.gitignore';f.write_text(f.read_text().replace('*.wav\n',''))
print('adopted',len(used),'duration',m['composition']['durationInFrames']/30)
