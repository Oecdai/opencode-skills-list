#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).with_name("skills_list.py")


def main() -> int:
    args = sys.argv[1:] or ["summary"]
    command = [sys.executable, str(SCRIPT), *args]
    result = subprocess.run(command)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
