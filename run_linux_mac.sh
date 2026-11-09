#!/usr/bin/env bash
# ===========================================================================
# run_linux_mac.sh - Project Kykloi Portable USB Launcher (POSIX)
# ===========================================================================
set -e

# Change to the project directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Initializing Kykloi Local Appliance ==="

# 1. Identify Python interpreter
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
elif command -v uv >/dev/null 2>&1; then
    PYTHON_BIN="uv run python"
else
    echo "[ERROR] Python 3 was not found in your system PATH."
    echo "Please install Python 3 (>= 3.12) to run Kykloi."
    exit 1
fi

# 2. Check if the build output exists; build if missing
if [ ! -f "dist/index.html" ] || [ ! -f "dist/search.db" ]; then
    echo "[INFO] Artifacts missing in dist/. Running initial build..."
    $PYTHON_BIN build/build_site.py
fi

# 3. Launch HTTP daemon with browser launch flag
echo "[INFO] Starting local daemon and opening browser..."
exec $PYTHON_BIN serve.py --browser
