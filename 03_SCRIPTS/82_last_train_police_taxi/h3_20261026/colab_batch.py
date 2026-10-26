#!/usr/bin/env python3
"""Executed in the Colab kernel by the official CLI; all data stays on the VM."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import urllib.request
import zipfile


def main(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    lock = (root / 'run.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    os.chdir(root)
    with zipfile.ZipFile('/content/' + root.name + '.zip') as z:
        for name in z.namelist():
            if Path(name).name != name:
                raise ValueError('Bundle entries must be flat')
        z.extractall(root)
    state = {'status': 'running', 'started_unix': time.time()}
    def record():
        (root / 'status.json').write_text(json.dumps(state, indent=2))
    def run(args, stage):
        state['stage'] = stage
        record()
        logpath = root / (stage + '.log')
        done = threading.Event()
        def heartbeat():
            while not done.wait(10):
                print(stage, 'running; elapsed', round(time.time()-state['started_unix']), 'seconds', flush=True)
        thread = threading.Thread(target=heartbeat, daemon=True)
        thread.start()
        try:
            with logpath.open('a') as log:
                subprocess.run(args, stdout=log, stderr=subprocess.STDOUT, check=True)
        finally:
            done.set()
            thread.join()
            print(logpath.read_text(errors='replace')[-5000:], flush=True)
    try:
        ready = False
        if (root/'ch1.runtime.json').exists():
            try:
                with urllib.request.urlopen('http://127.0.0.1:8188/system_stats', timeout=5):
                    ready = True
            except OSError:
                pass
        if not ready:
            run([sys.executable, '-u', 'setup_cuda.py', 'ch1.json', '--root', str(root)], 'setup')
        runtime = json.loads((root/'ch1.runtime.json').read_text())
        second = json.loads((root/'ch2.json').read_text())
        for key, node in second.items():
            if node['class_type'] in ('UNETLoader','CLIPLoader','VAELoader'):
                node['inputs'] = runtime[key]['inputs']
        (root/'ch2.runtime.json').write_text(json.dumps(second, indent=2))
        for chapter in (1,2):
            run([sys.executable, '-u', 'run_workflow.py', f'ch{chapter}.runtime.json', '--out', f'ch{chapter}_480p.mp4'], f'generate_ch{chapter}')
        state.update(status='complete',elapsed_seconds=time.time()-state['started_unix'])
        state['sha256']={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ('ch1_480p.mp4','ch2_480p.mp4')}
    except BaseException as e:
        state.update(status='failed', error=str(e))
        raise
    finally:
        record()
        with zipfile.ZipFile(root/'results.zip','w',zipfile.ZIP_DEFLATED) as z:
            for p in root.iterdir():
                if p.is_file() and p.suffix in ('.json','.log','.mp4') and '.part.' not in p.name:
                    z.write(p,p.name)
        print(json.dumps(state), flush=True)


if __name__ == '__main__':
    main(sys.argv[1])
