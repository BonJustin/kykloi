#!/usr/bin/env sh
set -e

REQ_MAJ="${REQ_MAJ:-3}"
REQ_MIN="${REQ_MIN:-10}"

# ---------------------------------------------------------------------------
# 1. EVALUATE HOST PYTHON
# ---------------------------------------------------------------------------
USE_HOST_PY=0

if [ "${KYKLOI_FORCE_FALLBACK}" != "1" ] && command -v python3 >/dev/null 2>&1; then
    PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
    MAJ=$(echo "$PY_VER" | cut -d. -f1)
    MIN=$(echo "$PY_VER" | cut -d. -f2)
    if [ "$MAJ" -eq "$REQ_MAJ" ] && [ "$MIN" -ge "$REQ_MIN" ]; then
        USE_HOST_PY=1
    fi
fi

if [ "$USE_HOST_PY" -eq 1 ]; then
    echo "[Kykloi] Using host Python runtime: $(which python3) (${PY_VER})"
    exec python3 system/launch.py "$@"
fi

# ---------------------------------------------------------------------------
# 2. RESOLVE PLATFORM TARGET IDENTIFIER
# ---------------------------------------------------------------------------
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
    Linux)
        case "$ARCH" in
            x86_64)        TARGET="linux-x86_64" ;;
            aarch64|arm64) TARGET="linux-arm64" ;;
            *) echo "[FATAL] Unsupported Linux architecture: $ARCH" >&2; exit 1 ;;
        esac
        ;;
    Darwin)
        case "$ARCH" in
            x86_64) TARGET="macos-x86_64" ;;
            arm64)  TARGET="macos-arm64" ;;
            *) echo "[FATAL] Unsupported macOS architecture: $ARCH" >&2; exit 1 ;;
        esac
        ;;
    *)
        echo "[FATAL] Unsupported operating system: $OS" >&2; exit 1
        ;;
esac

# ---------------------------------------------------------------------------
# 3. HYDRATE RUNTIME TO LOCAL TEMPORARY STORAGE (WITH SHA-256 VERIFICATION)
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ARCHIVE_PY="$SCRIPT_DIR/system/tools/archives/python-${TARGET}.tar.gz"
MANIFEST_PATH="$SCRIPT_DIR/system/tools/tools_manifest.json"
RUNTIME_ROOT="/tmp/kykloi_runtime_${TARGET}"
LOCAL_PY="$RUNTIME_ROOT/bin/python3"
STAMP_FILE="$RUNTIME_ROOT/.verified_sha256"

compute_sha256() {
    target_file="$1"
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$target_file" | cut -d' ' -f1
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$target_file" | cut -d' ' -f1
    elif command -v openssl >/dev/null 2>&1; then
        openssl dgst -sha256 "$target_file" | awk '{print $NF}'
    else
        echo "[FATAL] No SHA-256 verification utility (sha256sum, shasum, openssl) available." >&2
        exit 1
    fi
}

extract_expected_hash() {
    archive_name="$1"
    manifest="$2"
    sed -n "/\"${archive_name}\"/,/}/p" "$manifest" | grep '"sha256"' | head -n 1 | sed -E 's/.*"sha256":[[:space:]]*"([^"]+)".*/\1/'
}

if [ ! -f "$LOCAL_PY" ] || [ ! -f "$STAMP_FILE" ]; then
    if [ ! -f "$ARCHIVE_PY" ]; then
        echo "[FATAL] Python >= ${REQ_MAJ}.${REQ_MIN} missing on host, and fallback archive not found at:" >&2
        echo "        $ARCHIVE_PY" >&2
        exit 1
    fi

    if [ ! -f "$MANIFEST_PATH" ]; then
        echo "[FATAL] Verification manifest missing at: $MANIFEST_PATH" >&2
        exit 1
    fi

    EXPECTED_SHA=$(extract_expected_hash "python-${TARGET}.tar.gz" "$MANIFEST_PATH")
    if [ -z "$EXPECTED_SHA" ]; then
        echo "[FATAL] Could not locate SHA-256 definition for python-${TARGET}.tar.gz in manifest." >&2
        exit 1
    fi

    echo "[Kykloi] Verifying SHA-256 for python-${TARGET}.tar.gz..."
    ACTUAL_SHA=$(compute_sha256 "$ARCHIVE_PY")

    if [ "$ACTUAL_SHA" != "$EXPECTED_SHA" ]; then
        echo "[FATAL] Checksum verification failed for $ARCHIVE_PY" >&2
        echo "        Expected: $EXPECTED_SHA" >&2
        echo "        Actual:   $ACTUAL_SHA" >&2
        exit 1
    fi

    echo "[Kykloi] Checksum verified. Extracting portable Python runtime to $RUNTIME_ROOT..."
    rm -rf "$RUNTIME_ROOT"
    mkdir -p "$RUNTIME_ROOT"
    tar -xzf "$ARCHIVE_PY" -C "$RUNTIME_ROOT" --strip-components=1
    printf "%s" "$ACTUAL_SHA" > "$STAMP_FILE"

    if [ "$OS" = "Darwin" ]; then
        xattr -dr com.apple.quarantine "$RUNTIME_ROOT" 2>/dev/null || true
    fi
fi

# ---------------------------------------------------------------------------
# 4. EXECUTE APPLICATION LAUNCHER
# ---------------------------------------------------------------------------
echo "[Kykloi] Using fallback Python runtime: $LOCAL_PY"
exec "$LOCAL_PY" "$SCRIPT_DIR/system/launch.py" "$@"
