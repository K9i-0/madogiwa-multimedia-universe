from pathlib import Path
import subprocess
EP=Path(__file__).resolve().parent
for slug,comp in [('hau','Hau'),('himari','Himari'),('sayo','Sayo')]:
 subprocess.run(['npx','remotion','render','src/index.ts',comp,f'../final_remotion_sample_{slug}.mp4','--concurrency=2','--log=error'],cwd=EP/'remotion',check=True)
 print('Rendered',slug,flush=True)
