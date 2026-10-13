"""Current user-selected casting; v3 Irodori workflow remains in prepare_duo_voice.py."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name("prepare_usagi_voice.py")),run_name="__main__")
