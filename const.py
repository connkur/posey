import os.path
from pathlib import Path

TOOL_NAME  ="Posey"
CLIPBOARD  = Path(os.path.dirname(__file__), "Clipboard.json")
LOG_FILE   = Path(os.path.dirname(__file__), f"{TOOL_NAME}.log")
POSE_DIR   = Path(os.path.dirname(__file__), "poses")
IMG_DIR    = Path(os.path.dirname(__file__), "data", "images")
MIRROR_MAP = {'x': 0, 'y': 1, 'z': 2}