from pathlib import Path
import json,wave,math,subprocess
from PIL import ImageFont
P=Path(__file__).resolve().parent;m=json.loads((P/'src/edit-manifest.json').read_text());fps=m['composition']['fps']
(P/'out').mkdir(exist_ok=True)
font=ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',29)
prev=0;report=[]
ids=[d['id'] for d in m['dialogue']]
assert len(ids)==len(set(ids)), 'Duplicate dialogue IDs'
for i,d in enumerate(m['dialogue']):
 assert d['startFrame']>=prev,('overlap',i)
 with wave.open(str(P/'public'/d['audio'])) as w:duration=w.getnframes()/w.getframerate()
 assert math.ceil(duration*fps)==d['durationInFrames']
 assert len(d['envelope'])==d['durationInFrames']
 segments=d.get('captionSegments',[{'text':d['caption'],'startFrame':0,'endFrame':d['durationInFrames']}])
 assert ''.join(s['text'].replace('\n','') for s in segments)==d['text'],i
 widths=[];end=0
 for seg in segments:
  assert seg['startFrame']==end and seg['endFrame']>end,(i,seg)
  end=seg['endFrame'];assert len(seg['text'].splitlines())<=2
  caption_font=ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',d.get('captionFontSize',29))
  widths += [caption_font.getlength(x) for x in seg['text'].splitlines()]
 assert end==d['durationInFrames']
 assert max(widths)<=790,(i,widths)
 prev=d['startFrame']+d['durationInFrames'];report.append({'index':i,'maxCaptionWidth':max(widths),'durationSeconds':duration})
previous_clip_end=0
clip_report=[]
source_probes={}
for c in m['clips']:
 assert c['startFrame']>=previous_clip_end,('clip overlap',c.get('id'))
 previous_clip_end=c['startFrame']+c['durationInFrames']
 assert c['durationInFrames']>0 and c['sourceStartFrame']>=0,c
 assert c['afterId'] in ids,c
 source=P/'public'/c['src'];assert source.exists(),source
 if c['src'] not in source_probes:
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(source)]))
  source_probes[c['src']]=probe
 probe=source_probes[c['src']]
 assert (c['sourceStartFrame']+c['durationInFrames'])/fps<=float(probe['format']['duration'])+.04,('clip source too short',c)
 assert any(s['codec_type']=='audio' for s in probe['streams']),('missing clip audio',c['src'])
 for d in m['dialogue']:assert c['startFrame']+c['durationInFrames']<=d['startFrame'] or c['startFrame']>=d['startFrame']+d['durationInFrames']
 clip_report.append({'id':c.get('id'),'startFrame':c['startFrame'],'durationInFrames':c['durationInFrames'],'source':c['src'],'sourceDurationSeconds':float(probe['format']['duration'])})
assert prev<m['creditsStartFrame']<=m['composition']['durationInFrames']
assert previous_clip_end<m['creditsStartFrame']
assert 0<=m['mainStartFrame']<m['endingStartFrame']<m['creditsStartFrame']
assert m.get('creditsInDescription') and m['creditsStartFrame']==m['composition']['durationInFrames']
(P/'out/timeline_validation.json').write_text(json.dumps({'utterances':len(report),'maxCaptionWidth':max(x['maxCaptionWidth'] for x in report),'dialogueClipOverlap':False,'captionTextMatches':True,'utteranceAudioDurationsMatch':True,'clips':clip_report,'items':report},indent=2))
print('PASS',len(report),'utterances; max caption width',max(x['maxCaptionWidth'] for x in report))
