#!/usr/bin/env python3
"""Prepare immutable 17-shot Colab input bundle; does not allocate GPU."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

SOURCE = Path(__file__).resolve().parent
REPO = SOURCE.parents[2]
SCRIPTS = REPO/'.claude/skills/minimax-h3-video/scripts'

def main():
    job = Path(sys.argv[1]).resolve()
    job.mkdir(parents=True, exist_ok=False)
    bundle = job/'bundle'
    bundle.mkdir()
    chapters = json.loads((SOURCE/'chapter_plan.json').read_text())
    manifest = []
    for index, chapter in enumerate(chapters):
        name = chapter['id']
        images = [chapter['visual_reference'], 'refs/sobaya_canonical.png', 'refs/sobaya_face.jpg']
        if int(chapter['scene'][1:3]) >= 8:
            images.append('refs/product_original.webp')
        prompt = (SOURCE/'prompts'/f'{name}.txt').read_text()
        args = [sys.executable, str(SCRIPTS/'build_workflow.py'), '--mode', 'r2v', '--frames', str(chapter['frames']), '--seed', str(75002601+index), '--prefix', 'video/keynote_'+name, '--out', str(bundle/f'{name}.json'), '--prompt-file', str(bundle/f'{name}.txt')]
        for kind, assets in [('image', images), ('audio', chapter['audio'])]:
            for asset in assets:
                src = SOURCE/asset
                target = bundle/src.name
                if target.exists() and target.read_bytes() != src.read_bytes():
                    raise ValueError('Filename collision: '+asset)
                shutil.copy2(src, target)
                prompt = prompt.replace(asset, src.name)
                args += ['--'+kind, src.name]
        (bundle/f'{name}.txt').write_text(prompt)
        subprocess.run(args, check=True)
        manifest.append({'id': name, 'seed':75002601+index, 'images':images, 'audio':chapter['audio'], 'frames':chapter['frames']})
    shutil.copy2(SOURCE/'chapter_plan.json',bundle/'chapter_plan.json')
    shutil.copy2(SOURCE/'colab_batch.py',bundle/'colab_remote.py')
    for name in ('setup_cuda.py','run_workflow.py'):
        shutil.copy2(SCRIPTS/name,bundle/name)
    (bundle/'input_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    with zipfile.ZipFile(job/'inputs.zip','w',zipfile.ZIP_DEFLATED) as z:
        for path in sorted(bundle.iterdir()):
            z.write(path,path.name)
    digest=hashlib.sha256((job/'inputs.zip').read_bytes()).hexdigest()
    (job/'job.json').write_text(json.dumps({'status':'prepared','bundle_sha256':digest},indent=2))
    print('Prepared',len(chapters),'shots:',job)

if __name__=='__main__': main()
