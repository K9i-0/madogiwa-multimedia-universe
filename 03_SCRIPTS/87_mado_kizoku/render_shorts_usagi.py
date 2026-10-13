"""Render the existing Shorts layout with adopted v12 audio and updated credit."""
from pathlib import Path
import json,os,subprocess,hashlib
E=Path(__file__).resolve().parent;R=E.parents[1];P=E.parent/'shorts_queue_20261011/remotion';M=E/'shorts-manifest-usagi.json';V=E/'final_remotion_subtitles_v12_usagi_normal.mp4';O=E/'final_remotion_shorts_usagi_9x16.mp4'
for c in json.loads(M.read_text())['clips']:
 dst=P/'public'/c['file']
 if not dst.exists():os.link(R/c['source'],dst)
subprocess.run(['npx','tsc','--noEmit'],cwd=P,check=True)
subprocess.run(['npx','remotion','render','src/index.tsx','Shorts','out/ojousama-usagi-silent.mp4','--props='+str(M),'--muted','--crf=18','--concurrency=2','--log=error'],cwd=P,check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'out/ojousama-usagi-silent.mp4'),'-i',str(V),'-map','0:v:0','-map','1:a:0','-t',str(1102/30),'-c','copy','-movflags','+faststart',str(O)],check=True)
print(O)
