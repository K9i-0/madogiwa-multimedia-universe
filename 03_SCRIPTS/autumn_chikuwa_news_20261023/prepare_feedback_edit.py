"""Adopt the four requested takes and rebuild timing; no synthesis calls here."""
from pathlib import Path
import hashlib
import json
import math
import re
import shutil
import subprocess

P=Path(__file__).resolve().parent
ROOT=P.parent.parent
OUT=P/'remotion/out/feedback_20261024'
PUBLIC=P/'remotion/public'
MANIFEST=P/'remotion/src/edit-manifest.json'

def run(args):
    return subprocess.run(list(map(str,args)),check=True,capture_output=True,text=True)

def ff(args):
    return run(['ffmpeg','-y','-v','error',*args])

def duration(f):
    return float(run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]).stdout)

def sha(f):
    return hashlib.sha256(f.read_bytes()).hexdigest()

lines=[
    ('anchor_to_expert','voice_anchor_to_expert.wav','ちくわ生物学が専門のおかやまんさん、注意点は？','voice_forest.wav',2026),
    ('okayaman_comparison','voice_comparison_matched.wav','食用と非常によく似ていますので、見た目だけで判断しないでください。','voice_ref_okayaman_visible.wav',42),
    ('anchor_to_field','voice_anchor_to_field.wav','では、もう一度、現場に戻ります。','voice_forest.wav',2026),
    ('sobaya_poison','voice_sobaya_poison.wav','ど、毒……','../../02_CHARACTERS/Sobaya_voice.wav',42),
]
assert all((OUT/f'{key}.wav').is_file() for key,*_ in lines), 'Missing take; no automatic generation/retry.'
records=[]
for key,name,text,reference,seed in lines:
    raw=OUT/f'{key}.wav'
    source=raw
    if key=='sobaya_poison':
        source=OUT/'sobaya_poison_monster.wav'
        run(['bash',ROOT/'tools/sobaya_monsterize.sh',raw,source])
    trimmed=OUT/f'{key}_trim.wav'
    # Silence only: keep the consonants, breath and natural tempo.
    ff(['-i',source,'-af','silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.08,areverse,silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.16,areverse',
        '-ar','48000','-ac','1','-c:a','pcm_s16le',trimmed])
    analysis=run(['ffmpeg','-hide_banner','-i',trimmed,'-af','loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-']).stderr
    levels=json.loads(re.findall(r'\{[^{}]+\}',analysis)[-1])
    gain=min(-18-float(levels['input_i']),-1.5-float(levels['input_tp']))
    target=P/name
    ff(['-i',trimmed,'-af',f'volume={gain:.4f}dB','-c:a','pcm_s16le',target])
    shutil.copy2(target,PUBLIC/name)
    ref=P/reference
    records.append({'key':key,'file':name,'text':text,'ttsText':'ど、どく……。' if key=='sobaya_poison' else text,
                    'model':'Aratako/Irodori-TTS-v4-Large','seed':seed,'reference':reference,
                    'caption':('落ち着いた地方局ニュース読み。標準語で、明瞭かつ均一な速度、抑制された抑揚で真面目に話す。' if key.startswith('anchor_') else '息が詰まり、苦しげにかすれた声で途切れ途切れにつぶやく。' if key=='sobaya_poison' else ''),
                    'textCfg':5,'durationScale':1,'uncut':True,
                    'referenceSha256':sha(ref),'rawSha256':sha(raw),'adoptedSha256':sha(target),
                    'rawSeconds':duration(raw),'seconds':duration(target),'frames':math.ceil(duration(target)*30),
                    'gainDb':gain,'generationAttempts':1,
                    'postprocessing':'sobaya_monsterize + silence trim + constant gain' if key=='sobaya_poison' else 'silence trim + constant gain',
                    'speedChange':False})

bykey={r['key']:r for r in records}
# Start from the reviewed v1 every time; don't append bridges on repeated preparation.
m=json.loads((OUT/'edit-manifest-v1.json').read_text())
spec=m['final']
cue=12
sobaya_from=187
theft_frames=max(235,sobaya_from+bykey['sobaya_poison']['frames']+6)
spec['theftSourceEdits'][-1]['frames']=theft_frames-205
spec['feedback']={'date':'2026-10-24','studioCueFrames':cue,'sobayaFrom':sobaya_from,
                  'sobayaFrames':bykey['sobaya_poison']['frames'],'generatedTakes':4}
new=[]
for s in spec['sequences']:
    if s['id']=='expert':new.append({'id':'bridge_expert','duration':cue+bykey['anchor_to_expert']['frames']+6})
    if s['id']=='theft':new.append({'id':'bridge_field','duration':cue+bykey['anchor_to_field']['frames']+6})
    item=dict(s)
    if s['id']=='comparison':item['duration']=bykey['okayaman_comparison']['frames']+6
    if s['id']=='theft':item['duration']=theft_frames
    new.append(item)
start=0
for s in new:s['from']=start;start+=s['duration']
spec['sequences']=new
spec['composition']['durationInFrames']=start
spec.pop('reaction',None)
spec['audioGainDb'].pop('reaction',None)
MANIFEST.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')

ff(['-ss','2','-i',PUBLIC/'anchor_intro.mp4','-t',cue/30,'-an','-c:v','libx264','-crf','16',PUBLIC/'anchor_bridge.mp4'])
shutil.copy2(P/'wan3_expert_listening_480p.mp4',PUBLIC/'expert_listening.mp4')
record={'authorization':'User feedback 2026-10-24: two anchor bridges, comparison voice matching, Sobaya final utterance.',
        'generationAttempts':4,'videoGenerationRequests':0,'imageGenerationRequests':0,
        'referenceExtraction':{'file':'voice_ref_okayaman_visible.wav','source':'wan3_expert_480p.mp4','startSeconds':0.95,'endSeconds':3.55,'channels':1,'sampleRate':48000},
        'voices':records,'compositionFrames':start,'compositionSeconds':start/30,
        'listeningAudit':'Not claimed; ASR and measured audio checks are separate from listening.'}
(P/'feedback_20261024.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(record,ensure_ascii=False,indent=2))
