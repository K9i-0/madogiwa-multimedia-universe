"""Rebuild H3 audio inputs from adopted episode75 WAVs; no TTS or GPU invocation."""
from pathlib import Path
import json,hashlib,shutil,subprocess
out=Path(__file__).resolve().parent;root=out.parents[2]
for r in json.loads((out/'audio_manifest.json').read_text()):
 src=root/r['source'];assert hashlib.sha256(src.read_bytes()).hexdigest()==r['source_sha256']
 dst=out/r['input'];dst.parent.mkdir(exist_ok=True)
 if r['padding']:
  subprocess.run(['ffmpeg','-y','-v','error','-i',str(src),'-af','apad','-t','2','-c:a','pcm_s16le',str(dst)],check=True)
 else:shutil.copy2(src,dst)
print('32 adopted dialogue inputs ready; no audio generation.')
