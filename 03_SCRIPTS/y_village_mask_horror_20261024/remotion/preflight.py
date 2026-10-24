from pathlib import Path
import json
P=Path(__file__).resolve().parent;m=json.loads((P/'src/edit-manifest.json').read_text());n=m['composition']['durationInFrames']
assert m['composition']['width']==1280 and m['composition']['height']==720
assert n<=18000
for group in ['narration','captions','shots','soundRegions']:
 for row in m[group]:assert 0<=row['from']<row['to']<=n,(group,row)
for group in ['narration','captions','shots']:
 for a,b in zip(m[group],m[group][1:]):assert a['to']<=b['from'],(group,a,b)
for a,b in zip(m['shots'],m['shots'][1:]):assert a['to']==b['from']
assert m['shots'][0]['from']==0 and m['shots'][-1]['to']==n
for row in m['captions']:
 lines=row['text'].split('\n');assert len(lines)<=2 and max(map(len,lines))<=32
 assert (row['to']-row['from'])/30>=.95,(row['id'],'too short')
for row in m['shots']:assert (P/'public/art'/f"{row['image']}.png").is_file()
for row in m['narration']:assert (P/'public'/row['file']).is_file()
speech=''.join(r['text'] for r in m['narration'])
source=json.loads((P/'dialogue-source.json').read_text())
assert [r['text'] for r in m['narration']]==[r['text'] for r in source]
assert ''.join(c['text'].replace('\n','') for c in m['captions'])==speech
for old in ['ビール','二日酔い','メガジョッキ','祠','猿','エクセル','窓際族ですか']:assert old not in speech,old
assert speech.count('中口')==1
assert all(r['engine']!='voicevox' or json.loads((P.parent/'queries'/f"{r['id']}.json").read_text())['speedScale']==1 for r in m['narration'])
out={'passed':True,'frames':n,'duration':n/30,'narration':len(m['narration']),'captions':len(m['captions']),'shots':len(m['shots']),'maxCaptionLines':2,'speed':1,'sourceTextUnaltered':True}
(P/'out/preflight.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
