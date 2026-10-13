from pathlib import Path
import json,wave,math
from PIL import ImageFont
P=Path(__file__).resolve().parent;m=json.loads((P/'src/edit-manifest.json').read_text());fps=30
font=ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',29)
prev=0;report=[]
for i,d in enumerate(m['dialogue']):
 assert d['startFrame']>=prev,('overlap',i)
 with wave.open(str(P/'public'/d['audio'])) as w:duration=w.getnframes()/w.getframerate()
 assert math.ceil(duration*fps)==d['durationInFrames']
 assert len(d['envelope'])==d['durationInFrames']
 assert len(d['caption'].splitlines())<=2
 widths=[font.getlength(x) for x in d['caption'].splitlines()]
 assert max(widths)<=1050,(i,widths)
 assert d['caption'].replace('\n','')==d['text'],i
 prev=d['startFrame']+d['durationInFrames'];report.append({'index':i,'maxCaptionWidth':max(widths),'durationSeconds':duration})
for c in m['clips']:
 for d in m['dialogue']:assert c['startFrame']+c['durationInFrames']<=d['startFrame'] or c['startFrame']>=d['startFrame']+d['durationInFrames']
assert prev<m['creditsStartFrame']<m['composition']['durationInFrames']
(P/'out/timeline_validation.json').write_text(json.dumps({'utterances':len(report),'maxCaptionWidth':max(x['maxCaptionWidth'] for x in report),'dialogueClipOverlap':False,'captionTextMatches':True,'utteranceAudioDurationsMatch':True,'items':report},indent=2))
print('PASS',len(report),'utterances; max caption width',max(x['maxCaptionWidth'] for x in report))
