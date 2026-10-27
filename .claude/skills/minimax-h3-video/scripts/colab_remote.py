#!/usr/bin/env python3
"""Executed in the Colab kernel by the official CLI; all data stays on the VM."""
import fcntl
import hashlib
import json
import os
import shutil
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
        if (root/'workflow.runtime.json').exists():
            try:
                with urllib.request.urlopen('http://127.0.0.1:8188/system_stats', timeout=5):
                    ready = True
            except OSError:
                pass
        if not ready:
            run([sys.executable, '-u', 'setup_cuda.py', 'workflow.json', '--root', str(root)], 'setup')
        graph = json.loads((root/'workflow.runtime.json').read_text())
        dims = next(n['inputs'] for n in graph.values() if n['class_type'] in ('MiniMaxH3ImageToVideo','MiniMaxH3ReferenceToVideo'))
        w,h = dims['width'],dims['height']
        native = f'video_{min(w,h)}p.mp4'
        final = 'video_720p.mp4' if min(w,h) < 720 else 'video_final.mp4'
        run([sys.executable, '-u', 'run_workflow.py', 'workflow.runtime.json', '--out', native], 'generate')
        if not (root/final).exists():
            if min(w,h) >= 720:
                shutil.copy2(root/native, root/final)
            else:
                target = (1280,720) if w > h else (720,1280) if h > w else (720,720)
                run(['ffmpeg','-y','-i',native,'-vf',f'scale={target[0]}:{target[1]}:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos,pad={target[0]}:{target[1]}:(ow-iw)/2:(oh-ih)/2,setsar=1','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','copy','video_export.part.mp4'], 'export')
                (root/'video_export.part.mp4').replace(root/final)
        state['outputs'] = {'native': native, 'final': final, 'generation_resolution': [w,h]}
        state.update(status='complete',elapsed_seconds=time.time()-state['started_unix'])
        state['sha256']={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in (native,final)}
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
