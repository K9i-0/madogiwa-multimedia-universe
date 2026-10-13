"""Generate the current v5 narration and frame manifest."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name("prepare_v5_voice.py")), run_name="__main__")
