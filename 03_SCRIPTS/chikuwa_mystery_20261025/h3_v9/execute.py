import zipfile
from pathlib import Path
p=Path('/content/mmu-chikuwa-v9-20261027');p.mkdir(exist_ok=True)
with zipfile.ZipFile('/content/mmu-chikuwa-v9-20261027.zip') as z: source=z.read('colab_batch.py').decode()
ns={'__name__':'mmu_remote'};exec(compile(source,'colab_batch.py','exec'),ns);ns['main'](str(p))
