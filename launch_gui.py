"""Launch the archived PyQt UI from its expected working directory."""
from pathlib import Path
import os
import runpy
import sys

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / "show_0"))
os.chdir(root / "show_0")
runpy.run_path(str(root / "show_0" / "pyqt.py"), run_name="__main__")
