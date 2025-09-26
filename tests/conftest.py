from __future__ import annotations

from pathlib import Path
import sys

# Ensure the src directory is on the import path so tests can import project modules.
SRC_PATH = Path(__file__).resolve().parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
