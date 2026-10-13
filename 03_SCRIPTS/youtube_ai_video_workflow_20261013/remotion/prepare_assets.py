"""Link adopted source media and extract reproducible, unaltered source frames.

Sources are never modified. Existing links must continue to refer to the declared
source, so a stale public file cannot silently replace the adopted material.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess

P = Path(__file__).resolve().parent
R = P.parents[2]
manifest = json.loads((P.parent / 'asset_sources.json').read_text())
(P / 'public').mkdir(exist_ok=True)
(P / 'out').mkdir(exist_ok=True)


def sha256(path):
    with path.open('rb') as file:
        return hashlib.file_digest(file, 'sha256').hexdigest()


for name, relative_source in manifest['assets'].items():
    source = R / relative_source
    target = P / 'public' / name
    if not source.is_file():
        raise FileNotFoundError(source)
    if target.exists():
        if not target.samefile(source) and sha256(target) != sha256(source):
            raise RuntimeError(f'Public asset differs from declared source: {name}')
    else:
        os.link(source, target)

for name, extraction in manifest['extractedFrames'].items():
    subprocess.run([
        'ffmpeg', '-v', 'error', '-y', '-ss', str(extraction['seconds']),
        '-i', str(P / 'public' / extraction['asset']),
        '-frames:v', '1', '-q:v', '2', str(P / 'public' / name),
    ], check=True)

print(f"Prepared {len(manifest['assets'])} source assets and "
      f"{len(manifest['extractedFrames'])} source frames.")
