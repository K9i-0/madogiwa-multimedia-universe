"""Render the revised opening while the remaining narration is generated."""
from pathlib import Path
from collections import defaultdict
import json,subprocess,sys
P=Path(__file__).resolve().parent
progress={d['id']:d for d in json.loads((P/'out/v5_progress.json').read_text())};clips_after=defaultdict(list)
for c in json.loads((P/'clips_config.json').read_text()):clips_after[c['afterId']].append(c)
rows=[];clips=[];cursor=15
for r in json.loads((P/'dialogue.json').read_text()):
 if r['chapter']!='導入':break
 d=progress[r['id']];d['startFrame']=cursor;rows.append(d);cursor+=d['durationInFrames']+d.get('pause',9)
 for c in clips_after[d['id']]:clips.append(dict(c,startFrame=cursor));cursor+=c['durationInFrames']+15
n=cursor+45
m={'composition':{'width':1280,'height':720,'fps':30,'durationInFrames':n},'dialogue':rows,'clips':clips,'creditsStartFrame':n,'mainStartFrame':n,'endingStartFrame':n,'voiceModel':'v5','creditsInDescription':True}
(P/'out/v5_preview_manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
subprocess.run([sys.executable,str(P/'mix_audio.py'),'--manifest','out/v5_preview_manifest.json','--output','public/v5_preview_mix.wav','--record','out/v5_preview_mix_record.json'],cwd=P,check=True)
(P/'out/v5_preview.tsx').write_text('''import React from 'react';
import {Composition,registerRoot} from 'remotion';
import {Explainer} from '../src/Explainer';
import manifest from './v5_preview_manifest.json';
registerRoot(()=> <Composition id="V5Preview" component={Explainer} {...manifest.composition} defaultProps={{manifest,audioSrc:'v5_preview_mix.wav'}}/>);
''')
subprocess.run(['npx','remotion','render','out/v5_preview.tsx','V5Preview','out/opening_v5_01.mp4','--concurrency=2','--crf=18','--log=error'],cwd=P,check=True)
print('PREVIEW',n/30)
