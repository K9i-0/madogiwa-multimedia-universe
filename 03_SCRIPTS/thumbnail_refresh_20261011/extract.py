"""Re-extract adopted actual video frames. Run from repository root."""
import json,subprocess,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent
for t in json.loads((root/'selections.json').read_text()):
 dest=root/t['thumbnail']
 subprocess.run(['ffmpeg','-v','error','-ss',str(t['seconds']),'-i',t['source'],'-frames:v','1','-vf','scale=1280:720:force_original_aspect_ratio=decrease:flags=lanczos,pad=1280:720:(ow-iw)/2:(oh-ih)/2','-q:v','2','-y',str(dest)],check=True)
print('Extracted adopted frames')
