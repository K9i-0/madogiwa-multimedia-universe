import json,subprocess,time
from pathlib import Path
EP=Path(__file__).resolve().parent
job=EP/'generated/h3-cloth-production-v2';out=job/'partials';out.mkdir(exist_ok=True)
session='mmu-bbq-shirt-test-20261030-v1';remote='/content/'+session
shown=set();start=time.time()
plan=json.loads((EP/'cloth_production_plan_v2.json').read_text());names={c['id']:c['id'] for c in plan}
while time.time()-start<7200:
 state=job/'remote-status.json'
 r=subprocess.run(['colab','--auth','oauth2','download','-s',session,remote+'/status.json',str(state)],capture_output=True,text=True)
 if r.returncode==0:
  for c in json.loads(state.read_text()).get('completed',[]):
   id=c['id']
   if id in shown or id not in names:continue
   src=out/(id+'_480p.mp4')
   subprocess.run(['colab','--auth','oauth2','download','-s',session,remote+'/'+src.name,str(src)],check=True,stdout=subprocess.DEVNULL)
   preview=EP/('test_cloth_'+names[id]+'_720p_v2.mp4')
   subprocess.run(['ffmpeg','-y','-v','error','-i',str(src),'-vf','scale=1280:720:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(preview)],check=True)
   subprocess.run(['ffmpeg','-y','-v','error','-i',str(src),'-vf','fps=2,scale=432:240,tile=6x6','-frames:v','1',str(out/(id+'_contact.jpg'))],check=True)
   shown.add(id);print('PLAYABLE',names[id],preview,flush=True)
 if len(shown)==3:break
 time.sleep(35)
