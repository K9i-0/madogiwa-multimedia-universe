"""Extract each spoken interval from the actual final PCM mix for ASR audit."""
import json, subprocess, sys
from pathlib import Path
EP=Path(__file__).resolve().parent
m=json.loads((EP/'remotion/src/edit-manifest.json').read_text())
assert not m['pending'],m['pending']
out=EP/'generated/mix-audit';out.mkdir(parents=True,exist_ok=True)
paths=[]
for s in m['segments']:
    if s['type'] not in ('scene','explanation'):continue
    path=out/('mix_'+s['id']+'.wav')
    subprocess.run(['ffmpeg','-y','-v','error','-ss',str(s['start']/24),'-i',str(EP/'remotion/public/master.wav'),'-t',str(s['duration']/24),'-c:a','pcm_s16le',str(path)],check=True)
    paths.append(str(path))
subprocess.run([sys.executable,str(EP/'audit_audio.py'),*paths],check=True)
