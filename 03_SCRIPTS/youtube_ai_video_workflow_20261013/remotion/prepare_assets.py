from pathlib import Path
import json,os,subprocess
P=Path(__file__).resolve().parent;R=P.parents[2]
(P/'public').mkdir(exist_ok=True);(P/'out').mkdir(exist_ok=True)
for name,src in json.loads((P.parent/'asset_sources.json').read_text())['assets'].items():
 if not (P/'public'/name).exists():os.link(R/src,P/'public'/name)
for name,t in [('comedy',4),('news',3),('news_raw',3),('cm',3)]:
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(P/'public'/f'{name}.mp4'),'-frames:v','1',str(P/'public'/f'{name}.jpg')],check=True)
