from pathlib import Path
import json,time,subprocess,sys
P=Path(__file__).resolve().parent
while True:
 try:
  rows=json.loads((P/'out/voice_progress.json').read_text());expected=json.loads((P/'dialogue.json').read_text())
  if len(rows)==len(expected):break
 except (OSError,json.JSONDecodeError):pass
 time.sleep(3)
# The producer writes its last manifest immediately after the last progress record.
time.sleep(3)
subprocess.run([sys.executable,str(P/'finalize.py')],check=True)
subprocess.run([sys.executable,str(P/'mix_audio.py')],check=True,cwd=P)
