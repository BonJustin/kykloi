#!/usr/bin/env python3
"""
system/tools/fetch-tools.py - Autonomous Archive Fetcher & Verifier (Backwards-compatible wrapper).
Part of Project Kykloi.
Retrieves and validates offline toolchain archives using only Python standard libraries.
"""

import sys
from pathlib import Path

# Add project root to sys.path so system.tools is importable
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from system.tools.fetch_tools import (  # noqa: E402
    main,
)

if __name__ == "__main__":
    main()
