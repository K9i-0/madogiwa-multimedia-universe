#!/usr/bin/env python3
"""Install pinned ComfyUI and only the weights needed by an H3 API workflow.
Run on a dedicated Linux CUDA runtime, not on the author's Mac.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request

COMFY_REV = 'fe298e4e20f1ff26d30e8639267bbd0b57811390'
HF_REV = 'e5eb578a89295337b8ff433a035929ce0279e0b6'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('workflow', type=Path)
    p.add_argument('--root', type=Path, default=Path('/content/mmu-h3'))
    p.add_argument('--territory-evidence', default='unknown',
                   help='Optional deployment note recorded in setup.json; unknown does not block execution')
    a = p.parse_args()
    import torch
    if sys.platform != 'linux' or not torch.cuda.is_available():
        p.error('A Linux NVIDIA CUDA runtime is required')
    cap = torch.cuda.get_device_capability(0)
    if cap < (8, 0):
        p.error('This setup targets Ampere or newer (L4/A100); T4 is not supported')
    a.root.mkdir(parents=True, exist_ok=True)
    graph = json.loads(a.workflow.read_text())
    for n in graph.values():
        if n['class_type'] == 'UNETLoader':
            name = n['inputs']['unet_name']
            if cap >= (8, 9):
                n['inputs']['unet_name'] = name.replace('int8_convrot', 'fp8_scaled')
    runtime_wf = a.workflow.with_name(a.workflow.stem + '.runtime.json')
    runtime_wf.write_text(json.dumps(graph, indent=2))
    mapping = {'UNETLoader': ('diffusion_models', 'unet_name'),
               'CLIPLoader': ('text_encoders', 'clip_name'),
               'VAELoader': ('vae', 'vae_name'),
               'LoraLoaderModelOnly': ('loras', 'lora_name')}
    files = [f'{mapping[n["class_type"]][0]}/{n["inputs"][mapping[n["class_type"]][1]]}'
             for n in graph.values() if n['class_type'] in mapping]
    if shutil.disk_usage(a.root).free < 60 * 2**30:
        p.error('Provide at least 60 GiB free disk for the first install (~54 GB weights plus dependencies)')
    started = time.time()
    comfy = a.root / 'ComfyUI'
    if not (comfy / '.git').exists():
        subprocess.run(['git', 'clone', '--no-checkout', '--filter=blob:none',
                        'https://github.com/Comfy-Org/ComfyUI.git', str(comfy)], check=True)
        subprocess.run(['git', 'checkout', COMFY_REV], cwd=comfy, check=True)
    actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=comfy, text=True).strip()
    if actual != COMFY_REV:
        p.error('Existing ComfyUI revision differs; use a new --root rather than overwrite it')
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(comfy / 'requirements.txt'),
                    'huggingface_hub'], check=True)
    from huggingface_hub import hf_hub_download
    for name in files:
        print('Downloading', name, flush=True)
        hf_hub_download('Comfy-Org/MiniMax-H3', name, revision=HF_REV,
                       local_dir=comfy / 'models')
    for n in graph.values():
        key = {'LoadImage': 'image', 'LoadAudio': 'audio'}.get(n['class_type'])
        if key:
            name = n['inputs'][key]
            if Path(name).name != name:
                p.error('Input references must use flat filenames')
            shutil.copy2(a.workflow.parent / name, comfy / 'input' / name)
    report = dict(gpu=torch.cuda.get_device_name(0), cuda=torch.version.cuda, torch=torch.__version__,
                  comfy_revision=actual, weights_revision=HF_REV, model_files=files,
                  territory_evidence=a.territory_evidence, setup_seconds=time.time() - started)
    (a.root / 'setup.json').write_text(json.dumps(report, indent=2))
    log = a.root / 'comfy.log'
    with log.open('a') as f:
        proc = subprocess.Popen([sys.executable, 'main.py', '--listen', '127.0.0.1', '--port', '8188'],
                                cwd=comfy, stdout=f, stderr=subprocess.STDOUT, start_new_session=True)
    (a.root / 'comfy.pid').write_text(str(proc.pid))
    for _ in range(120):
        if proc.poll() is not None:
            raise RuntimeError(f'ComfyUI exited; inspect {log}')
        try:
            with urllib.request.urlopen('http://127.0.0.1:8188/object_info', timeout=5) as r:
                info = json.load(r)
            missing = {n['class_type'] for n in graph.values()} - set(info)
            if missing:
                raise RuntimeError(f'Missing nodes: {missing}')
            print('Ready:', runtime_wf)
            return
        except (OSError, TimeoutError):
            time.sleep(2)
    raise TimeoutError(f'ComfyUI startup timed out; inspect {log}')


if __name__ == '__main__':
    main()
