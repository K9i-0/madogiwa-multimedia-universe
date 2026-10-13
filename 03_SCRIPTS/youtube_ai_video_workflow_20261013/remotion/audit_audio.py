"""Screen current Irodori narration; preserve v2 evidence in speech_audit_v2.json."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('audit_duo_audio.py')), run_name='__main__')
