from pathlib import Path
import sys

from . import gui
# app_name = Path(sys.argv[0]).stem.lower()
# if app_name == "maya":
#     from . import gui_maya as gui
# else:
#     from . import gui

DEBUG = True

if DEBUG:
    print("Reloading gui.py")
    import importlib
    importlib.reload(gui)

_build = gui.build

