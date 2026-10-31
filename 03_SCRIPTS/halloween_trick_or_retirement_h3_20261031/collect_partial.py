"""Fetch only completed chapters through official Colab CLI; never submit generation."""
import json,subprocess,hashlib
from pathlib import Path
EP=Path(__file__).resolve().parent
SESSION='mmu-h3-halloween-20261031-v1';REMOTE='/content/'+SESSION
OUT=EP/'generated/partials';OUT.mkdir(parents=True,exist_ok=True)
state=EP/'generated/remote-status.json'
subprocess.run(['colab','--auth','oauth2','download','-s',SESSION,REMOTE+'/status.json',str(state)],check=True)
data=json.loads(state.read_text());print('STATUS',data,flush=True)
for c in data.get('completed',[]):
 name=c['id']+'_480p.mp4';dst=OUT/name
 if dst.exists():continue
 subprocess.run(['colab','--auth','oauth2','download','-s',SESSION,REMOTE+'/'+name,str(dst)],check=True)
 subprocess.run(['ffmpeg','-v','error','-i',str(dst),'-f','null','-'],check=True)
 print('READY',str(dst),hashlib.sha256(dst.read_bytes()).hexdigest(),flush=True)
