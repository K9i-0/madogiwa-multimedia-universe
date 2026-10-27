from pathlib import Path
import json,urllib.request,subprocess,math,hashlib
from array import array
r=Path(__file__).resolve().parent;p=r/'public/familiar-local';p.mkdir(exist_ok=True)
(r/'public/.gitignore').open('a').write('\n/familiar-local/\n')
m=json.loads((r/'src/solo-manifest.json').read_text());gaps=[8,7,10,20];shift=0
for i,(s,l) in enumerate(zip(m['scenes'],m['lines'])):
 s['startFrame']+=shift;s['durationInFrames']+=gaps[i];s['playbackRate']=(s['sourceEndFrame']-s['sourceStartFrame'])/s['durationInFrames']
 l['startFrame']+=shift;l['endFrame']+=shift
 shift+=gaps[i]
m['durationInFrames']+=shift
(r/'src/relaxed-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
cues=[(3,'drum-japanese2',-18,'和太鼓でドドン'),(104,'pafu1',-18,'パフ'),(153,'levelup1',-21,'レベルアップ'),(249,'drum-japanese2',-20,'和太鼓でドドン'),(319,'amount-display1',-18,'金額表示'),(None,'chan-chan2',-18,'ちゃんちゃん♪2')];events=[]
for sf,name,db,label in cues:
 path=p/(name+'.mp3');url='https://soundeffect-lab.info/sound/anime/mp3/'+path.name
 subprocess.run(['curl','-fLs','-e','https://soundeffect-lab.info/sound/anime/','-A','Mozilla/5.0',url,'-o',str(path)],check=True)
 d=array('f',subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-f','f32le','-ac','2','-ar','48000','-']))
 if sf is None:frame=m['lines'][-1]['endFrame']+1
 else:
  s=next(s for s in m['scenes'] if s['sourceStartFrame']<=sf<s['sourceEndFrame']);frame=round(s['startFrame']+(sf-s['sourceStartFrame'])/s['playbackRate'])
 dur=min(math.ceil(len(d)/2/1600),m['durationInFrames']-frame)
 events.append(dict(startFrame=frame,durationInFrames=dur,file='familiar-local/'+path.name,volume=10**(db/20)/max(abs(v) for v in d),label=label,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
(r/'src/familiar-sfx-manifest.json').write_text(json.dumps(dict(events=events,source='https://soundeffect-lab.info/sound/anime/',terms='https://soundeffect-lab.info/agreement/'),ensure_ascii=False,indent=2)+'\n')
s=(r/'src/Solo.tsx').read_text().replace("import m from './solo-manifest.json';","import m from './relaxed-manifest.json';").replace('export const Solo:', 'export const Relaxed:')
(r/'src/Relaxed.tsx').write_text(s)
(r/'src/Familiar.tsx').write_text('''import {AbsoluteFill,Html5Audio,Sequence,staticFile} from 'remotion';
import {Relaxed} from './Relaxed';
import sfx from './familiar-sfx-manifest.json';
export const Familiar: React.FC=()=> <AbsoluteFill><Relaxed/>{sfx.events.map((e,i)=><Sequence key={i} from={e.startFrame} durationInFrames={e.durationInFrames}><Html5Audio src={staticFile(e.file)} volume={f=>e.volume*Math.min(1,(e.durationInFrames-f)/4)}/></Sequence>)}</AbsoluteFill>;
''')
pth=r/'src/Root.tsx';s=pth.read_text();s="import {Relaxed} from './Relaxed';\nimport {Familiar} from './Familiar';\nimport relaxed from './relaxed-manifest.json';\n"+s;s=s.replace('    <>','    <>\n    <Composition id="YumemiFamiliar" component={Familiar} width={1920} height={1080} fps={30} durationInFrames={relaxed.durationInFrames}/>\n    <Composition id="YumemiRelaxed" component={Relaxed} width={1920} height={1080} fps={30} durationInFrames={relaxed.durationInFrames}/>');
if 'id="YumemiFamiliar"' not in pth.read_text():pth.write_text(s)
print('duration',m['durationInFrames'], 'events',events)
