"""
run.py
-------
Convenience entry point so you can run the whole pipeline from the
project root with:

    python run.py

This just delegates to src/main.py.
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from main import run_pipeline  # noqa: E402

if __name__ == "__main__":
    run_pipeline()
