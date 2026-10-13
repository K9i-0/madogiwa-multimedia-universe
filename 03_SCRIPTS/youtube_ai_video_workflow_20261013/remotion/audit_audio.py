"""Screen the current v4 narration; preserve v3 audit helpers separately."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('audit_usagi_audio.py')),run_name='__main__')
