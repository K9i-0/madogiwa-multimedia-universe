from pathlib import Path
import json,os,subprocess
P=Path(__file__).resolve().parent;R=P.parents[1];D=P/'remotion';(D/'public').mkdir(exist_ok=True);(D/'out').mkdir(exist_ok=True)
for name,src in json.loads((P/'assets.json').read_text()).items():
 dst=D/'public'/name
 if not dst.exists():os.link(R/src,dst)
for name,src,t in [('harbor_still.jpg','harbor.mp4',7),('giant_still.jpg','fishing.mp4',17),('harbor_sobaya.jpg','harbor.mp4',12),('forest_sobaya.jpg','autumn.mp4',51),('poison_sobaya.jpg','poison.mp4',38)]:
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(D/'public'/src),'-frames:v','1','-pix_fmt','yuvj420p',str(D/'public'/name)],check=True)
