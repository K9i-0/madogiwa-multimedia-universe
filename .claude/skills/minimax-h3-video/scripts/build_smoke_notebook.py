#!/usr/bin/env python3
"""Rebuild a self-contained Colab smoke test. No Drive mount or private inputs."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
cells = []
def cell(kind, source):
    c = {'cell_type': kind, 'metadata': {}, 'source': source}
    if kind == 'code':
        c.update(execution_count=None, outputs=[])
    cells.append(c)

cell('markdown', '''# MMU MiniMax H3 — 480p smoke test

同僚リポジトリのCUDA/Colab経路を参考に作成。**2026-10-26にColab L4でT2V実生成・MP4回収を確認済み**。
初回は架空人物・正典素材を使わない「窓辺のコーヒーの湯気」1カット。
864×480 / 124 frames / 24fps / 約5.17秒 / seed 42 / base 20 steps。

1. AI Plusと同じアカウントで開き、残高・CU/時を記録。L4を選ぶ。
2. 最初のセルでGPUと配置地域を確認する。モデルはまだDLしない。
3. [現行ライセンス](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)の対象地域と実行場所を照合。
   配置地域が取得できなければunknownとして記録し、動作確認を続ける。
4. 次のセルから順番に実行。地域情報は任意の記録項目。
5. 出力zipを回収してからランタイムを削除。失敗時も放置せずログを回収して削除。

このノートブックはDriveをマウントせず、全データは一時ランタイム内に置く。
画面を閉じる前に結果をDLすること。Google One増量・GCS・MiniMax APIキーは不要。
''')
cell('code', '''#@title 1. GPU / region preflight (no model downloads)
import json, os, shutil, urllib.request
import torch
print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')
print('Free GiB:', round(shutil.disk_usage('/content').free / 2**30, 1))
try:
    req = urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/zone',
                                 headers={'Metadata-Flavor': 'Google'})
    with urllib.request.urlopen(req, timeout=5) as r:
        DEPLOYMENT_ZONE = r.read().decode()
except Exception as e:
    DEPLOYMENT_ZONE = 'UNKNOWN: ' + type(e).__name__
print('Deployment zone:', DEPLOYMENT_ZONE)
print('Do not infer region from your account, browser locale or timezone.')
''')
cell('code', '''#@title 2. Deployment evidence and work directory
TERRITORY_EVIDENCE = globals().get("DEPLOYMENT_ZONE", "unknown") # Informational; not a generation gate
from pathlib import Path
import subprocess, sys, time
ROOT = Path('/content/mmu-h3')
ROOT.mkdir(exist_ok=True)
STARTED = time.time()
''')
embedded = {name: (HERE / name).read_text() for name in ['build_workflow.py', 'setup_cuda.py', 'run_workflow.py']}
cell('code', '#@title 3. Write tools and test prompt\nTOOLS = ' + repr(embedded) + '''
for name, source in TOOLS.items():
    (ROOT / name).write_text(source)
prompt = "A locked-off cinematic close-up of one white ceramic coffee cup on a wooden desk beside a sunlit office window. A thin wisp of steam rises and curls gently throughout the shot. The cup and camera remain still. Warm natural daylight, realistic materials. No people, no writing, no logos. Soundscape: quiet room tone. Music: none. Speech: none."
(ROOT / 'prompt.txt').write_text(prompt)
subprocess.run([sys.executable, str(ROOT/'build_workflow.py'), '--mode', 't2v',
    '--prompt-file', str(ROOT/'prompt.txt'), '--frames', '124', '--profile', '768p-base', '--width', '864', '--height', '480',
    '--out', str(ROOT/'smoke.json')], check=True)
''')
cell('code', '''#@title 4. Install and start ComfyUI (~54 GB download; consumes GPU runtime)
subprocess.run([sys.executable, str(ROOT/'setup_cuda.py'), str(ROOT/'smoke.json'),
    '--root', str(ROOT), '--territory-evidence', TERRITORY_EVIDENCE], check=True)
''')
cell('code', '''#@title 5. Generate exactly one clip (resume with same job state; never blind retry)
subprocess.run([sys.executable, str(ROOT/'run_workflow.py'), str(ROOT/'smoke.runtime.json'),
    '--out', str(ROOT/'smoke_480p.mp4'), '--timeout', '7200'], check=True)
''')
cell('code', '''#@title 6. Export 720p, preview and download evidence
# 864x480 is the model's 32-pixel grid. Preserve aspect ratio, pad to 1280x720.
subprocess.run(['ffmpeg', '-n', '-i', str(ROOT/'smoke_480p.mp4'), '-vf',
    'scale=1280:720:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1',
    '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'copy', str(ROOT/'smoke_720p.mp4')], check=True)
(ROOT/'elapsed.json').write_text(json.dumps({'wall_seconds': time.time()-STARTED}))
from IPython.display import Video, display
display(Video(str(ROOT/'smoke_720p.mp4'), embed=True))
import zipfile
with zipfile.ZipFile('/content/mmu_h3_smoke_results.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for name in ['smoke_480p.mp4','smoke_720p.mp4','smoke_480p.job.json','setup.json',
                 'elapsed.json','smoke.runtime.json','prompt.txt','comfy.log']:
        z.write(ROOT/name, name)
from google.colab import files
files.download('/content/mmu_h3_smoke_results.zip')
print('After verifying download: Runtime > Disconnect and delete runtime. Record ending CU balance.')
''')
nb = dict(nbformat=4, nbformat_minor=5,
          metadata={'colab': {'name': 'mmu_h3_smoke.ipynb'},
                    'kernelspec': {'display_name': 'Python 3', 'name': 'python3'}, 'accelerator': 'GPU'}, cells=cells)
for i, c in enumerate(cells):
    c['id'] = f'mmu-h3-{i}'
out = HERE.parent / 'assets' / 'mmu_h3_smoke.ipynb'
out.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + '\n')
print(out)
