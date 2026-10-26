"""Two checkpoint replacements, identical graphs, separate setup/download/job timings."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.request
import zipfile

# Use serial HTTP download for recovery; avoid concurrent Xet chunk requests.
os.environ['HF_HUB_DISABLE_XET']='1'
os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN']='1'


def main(root):
    root = Path(root); root.mkdir(parents=True, exist_ok=True)
    lock = (root/'run.lock').open('w'); fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    os.chdir(root)
    with zipfile.ZipFile(str(root)+'.zip') as z:
        assert all(Path(n).name == n for n in z.namelist())
        z.extractall(root)
    state = {'status':'running','started_unix':time.time(),'completed':[], 'models':[]}
    def record():
        tmp=root/'status.tmp'; tmp.write_text(json.dumps(state,indent=2)); tmp.replace(root/'status.json')
    def run(args, stage):
        state['stage']=stage; record(); start=time.monotonic(); done=threading.Event()
        def beat():
            while not done.wait(30): print(stage, round(time.monotonic()-start),'seconds',flush=True)
        th=threading.Thread(target=beat,daemon=True);th.start()
        try:
            with (root/(stage+'.log')).open('a') as f:
                subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,check=True)
        finally:
            done.set();th.join();print((root/(stage+'.log')).read_text(errors='replace')[-2500:],flush=True)
        return time.monotonic()-start
    def stop_comfy():
        pidfile=root/'comfy.pid'
        if pidfile.exists():
            try: os.kill(int(pidfile.read_text()),signal.SIGTERM)
            except ProcessLookupError: pass
            time.sleep(5)
    def start_comfy(name):
        logfile=root/('comfy_'+name+'.log')
        with logfile.open('a') as f:
            proc=subprocess.Popen([sys.executable,'main.py','--listen','127.0.0.1','--port','8188'],cwd=root/'ComfyUI',stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
        (root/'comfy.pid').write_text(str(proc.pid))
        for _ in range(120):
            if proc.poll() is not None: raise RuntimeError('ComfyUI exited: '+name)
            try:
                with urllib.request.urlopen('http://127.0.0.1:8188/system_stats',timeout=5) as r: json.load(r)
                return
            except OSError: time.sleep(2)
        raise TimeoutError('ComfyUI start timeout')
    try:
        state['setup_wall_seconds']=run([sys.executable,'-u','setup_cuda.py','ch01.json','--root',str(root)],'setup')
        stop_comfy()
        # The official checkpoint is only used to bootstrap the pinned environment.
        for p in (root/'ComfyUI/models/diffusion_models').glob('*.safetensors'): p.unlink()
        from huggingface_hub import hf_hub_download
        models=json.loads((root/'models.json').read_text())
        for spec in models:
            state['stage']='download_'+spec['id'];record();start=time.monotonic()
            for attempt in range(4):
                try:
                    path=Path(hf_hub_download(spec['repo'],spec['filename'],revision=spec['revision'],local_dir=root/'ComfyUI/models/diffusion_models',token=False))
                    break
                except Exception as exc:
                    if attempt==3:raise
                    pause=60*(2**attempt)
                    state['download_retry']={'attempt':attempt+1,'wait_seconds':pause,'error':type(exc).__name__};record()
                    time.sleep(pause)
            download_seconds=time.monotonic()-start;start=time.monotonic()
            with path.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
            assert digest==spec['sha256'], 'Checkpoint hash mismatch'
            model={**spec,'download_seconds':download_seconds,'hash_seconds':time.monotonic()-start}
            state['models'].append(model);record()
            start_comfy(spec['id'])
            for ch in ['ch01','ch02']:
                name=spec['id']+'_'+ch;graph=json.loads((root/(ch+'.json')).read_text())
                for node in graph.values():
                    if node['class_type']=='UNETLoader': node['inputs']['unet_name']=spec['filename']
                    if node['class_type']=='SaveVideo':node['inputs']['filename_prefix']='video/'+name
                    field={'LoadImage':'image','LoadAudio':'audio'}.get(node['class_type'])
                    if field:shutil.copy2(root/node['inputs'][field],root/'ComfyUI/input'/node['inputs'][field])
                (root/(name+'.json')).write_text(json.dumps(graph,indent=2))
                seconds=run([sys.executable,'-u','run_workflow.py',name+'.json','--out',name+'.mp4'],'generate_'+name)
                state['completed'].append({'model':spec['id'],'chapter':ch,'seconds':seconds,'file':name+'.mp4'});record()
            stop_comfy();path.unlink()
        state['status']='complete'
    except BaseException as e:
        state.update(status='failed',error=repr(e));raise
    finally:
        state['elapsed_seconds']=time.time()-state['started_unix']
        state['sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob('*.mp4')}
        record()
        with zipfile.ZipFile(root/'results.zip','w',zipfile.ZIP_DEFLATED) as z:
            for p in root.iterdir():
                if p.is_file() and p.suffix in ('.json','.log','.mp4') and '.part.' not in p.name:z.write(p,p.name)
        print(json.dumps(state),flush=True)
