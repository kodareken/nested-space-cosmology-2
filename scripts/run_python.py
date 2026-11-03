#!/usr/bin/env python3
"""Run Python commands using the isolated science-runtime environment."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = [
    ROOT / ".venv" / "science-runtime" / "python.exe",
    ROOT.parent / "nested-space-cosmology" / ".venv" / "science-runtime" / "python.exe",
    ROOT / ".venv" / "science-runtime" / "bin" / "python",
    ROOT.parent / "nested-space-cosmology" / ".venv" / "science-runtime" / "bin" / "python",
]


def main() -> int:
    python_exe = next((p for p in CANDIDATES if p.exists()), Path(sys.executable))
    env = os.environ.copy()
    src_path = str(ROOT / "src")
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src_path + (os.pathsep + existing if existing else "")
    proc = subprocess.run([str(python_exe), *sys.argv[1:]], cwd=ROOT, env=env)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
