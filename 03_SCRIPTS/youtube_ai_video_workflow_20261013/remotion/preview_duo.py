"""Build an opening-only review from the generated first eight utterances."""
from pathlib import Path
from collections import defaultdict
import json,subprocess,sys
P=Path(__file__).resolve().parent
progress={d['id']:d for d in json.loads((P/'out/duo_progress.json').read_text())};clips_after=defaultdict(list)
for c in json.loads((P/'clips_config.json').read_text()):clips_after[c['afterId']].append(c)
rows=[];clips=[];cursor=15
for i in range(8):
 d=progress[f'u{i:03}'];d['startFrame']=cursor;rows.append(d);cursor+=d['durationInFrames']+d.get('pause',12)
 for c in clips_after[d['id']]:clips.append(dict(c,startFrame=cursor));cursor+=c['durationInFrames']
 if clips_after[d['id']]:cursor+=15
n=cursor+45
m={'composition':{'width':1280,'height':720,'fps':30,'durationInFrames':n},'dialogue':rows,'clips':clips,'creditsStartFrame':n+1,'mainStartFrame':n,'endingStartFrame':n,'voiceModel':'Aratako/Irodori-TTS-v4.1-Small'}
(P/'out/duo_preview_manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
subprocess.run([sys.executable,str(P/'mix_audio.py'),'--manifest','out/duo_preview_manifest.json','--output','public/duo_preview_mix.wav','--record','out/duo_preview_mix_record.json'],cwd=P,check=True)
(P/'out/duo_preview.tsx').write_text('''import React from 'react';
import {Composition,registerRoot} from 'remotion';
import {Explainer} from '../src/Explainer';
import manifest from './duo_preview_manifest.json';
registerRoot(()=> <Composition id="DuoPreview" component={Explainer} {...manifest.composition} defaultProps={{manifest,audioSrc:'duo_preview_mix.wav'}}/>);
''')
subprocess.run(['npx','remotion','render','out/duo_preview.tsx','DuoPreview','out/duo_opening_v3.mp4','--concurrency=2','--crf=18','--log=error'],cwd=P,check=True)
print('PREVIEW',n/30)
