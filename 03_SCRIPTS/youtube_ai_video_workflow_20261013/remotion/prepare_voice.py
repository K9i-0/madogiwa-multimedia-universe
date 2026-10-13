"""Current cast: Yametaro and Takosan. Run with the Irodori Python environment.

The previous VOICEVOX implementation is retained in Git at commit 9aa43d7f.
"""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('prepare_duo_voice.py')), run_name='__main__')
