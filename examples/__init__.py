# Project name (source file without extension)
project = "boardgame_toolkit"

import sys
from pathlib import Path

# Add parent directory to the runtime search path,
# so we can import the boardgame_toolkit
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)


