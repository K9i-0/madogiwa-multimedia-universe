from pathlib import Path
import json,os,subprocess
P=Path(__file__).resolve().parent;R=P.parents[1];D=P/'remotion';(D/'public').mkdir(exist_ok=True);(D/'out').mkdir(exist_ok=True)
for name,src in json.loads((P/'assets.json').read_text()).items():
 dst=D/'public'/name
 if not dst.exists():os.link(R/src,dst)
for name,src,t in [('harbor_still.jpg','harbor.mp4',7),('giant_still.jpg','fishing.mp4',17),('harbor_sobaya.jpg','harbor.mp4',12),('forest_sobaya.jpg','autumn.mp4',51),('poison_sobaya.jpg','poison.mp4',38)]:
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(D/'public'/src),'-frames:v','1','-pix_fmt','yuvj420p',str(D/'public'/name)],check=True)

# Silent crop isolates chikuwa and sea; originals are retained.
archive=D/'public/fishing_archive_v7.mp4'
if not archive.exists():
 subprocess.run(['ffmpeg','-v','error','-y','-ss','27.6','-i',str(D/'public/fishing.mp4'),'-t','2','-vf','crop=iw*0.34:ih*0.60:iw*0.66:ih*0.30,scale=180:180:flags=area,fps=15,eq=saturation=0.55:contrast=0.92,noise=alls=6:allf=t','-an','-c:v','libx264','-crf','36','-preset','fast',str(archive)],check=True)

subprocess.run(['ffmpeg','-v','error','-y','-ss','0.4','-i',str(archive),'-frames:v','1',str(D/'public/chikuwa_archive_still_v7.jpg')],check=True)
