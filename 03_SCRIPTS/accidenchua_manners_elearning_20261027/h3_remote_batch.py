"""Official Colab kernel entrypoint; one setup, five sequential resumable H3 jobs."""
import fcntl,hashlib,json,os,shutil,subprocess,sys,threading,time,urllib.request,zipfile
from pathlib import Path

def main(root):
 root=Path(root);root.mkdir(parents=True,exist_ok=True)
 lock=(root/'run.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 os.chdir(root)
 with zipfile.ZipFile('/content/'+root.name+'.zip') as z:
  if any(Path(n).name!=n for n in z.namelist()):raise ValueError('Non-flat bundle')
  z.extractall(root)
 state={'status':'running','started_unix':time.time(),'completed':[]}
 def record():(root/'status.json').write_text(json.dumps(state,indent=2)+'\n')
 def run(args,stage):
  state['stage']=stage;record();done=threading.Event()
  def heartbeat():
   while not done.wait(10):print(stage,'running; elapsed',round(time.time()-state['started_unix']),'seconds',flush=True)
  t=threading.Thread(target=heartbeat,daemon=True);t.start()
  try:
   with (root/(stage+'.log')).open('a') as log:subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,check=True)
  finally:
   done.set();t.join();print((root/(stage+'.log')).read_text(errors='replace')[-2200:],flush=True)
 try:
  ready=False
  if (root/'setup.json').exists():
   try:
    with urllib.request.urlopen('http://127.0.0.1:8188/system_stats',timeout=5):ready=True
   except OSError:pass
  workflows=sorted(root.glob('*_workflow.json'))
  if not ready:run([sys.executable,'-u','setup_cuda.py',workflows[0].name,'--root',str(root)],'setup')
  for wf in workflows:
   name=wf.stem.removesuffix('_workflow');graph=json.loads(wf.read_text())
   for node in graph.values():
    key={'LoadImage':'image','LoadAudio':'audio'}.get(node['class_type'])
    if key:
     filename=node['inputs'][key];shutil.copy2(root/filename,root/'ComfyUI/input'/filename)
   runtime=root/f'{name}_workflow.runtime.json';runtime.write_text(json.dumps(graph,indent=2))
   native=f'{name}_480p.mp4'
   run([sys.executable,'-u','run_workflow.py',runtime.name,'--out',native],name+'_generate')
   state['completed'].append(name);record()
  state.update(status='complete',elapsed_seconds=time.time()-state['started_unix'])
  state['sha256']={f'{name}_480p.mp4':hashlib.sha256((root/f'{name}_480p.mp4').read_bytes()).hexdigest() for name in state['completed']}
 except BaseException as e:
  state.update(status='failed',error=str(e));raise
 finally:
  record()
  with zipfile.ZipFile(root/'results.zip','w',zipfile.ZIP_DEFLATED) as z:
   for f in root.iterdir():
    if f.is_file() and f.suffix in ('.json','.log','.mp4') and '.part.' not in f.name:z.write(f,f.name)
  print(json.dumps(state),flush=True)
