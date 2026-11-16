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
# 2. RESOLVE PLATFORM TARGET IDENTIFIER (GNU vs MUSL DETECTION)
# ---------------------------------------------------------------------------
OS="$(uname -s)"
ARCH="$(uname -m)"

detect_linux_libc() {
    # 1. Allow explicit user override
    if [ -n "$KYKLOI_LIBC" ]; then
        echo "$KYKLOI_LIBC"
        return
    fi

    # 2. Check for glibc via getconf (standard on Fedora, Debian, Ubuntu, etc.)
    if getconf GNU_LIBC_VERSION >/dev/null 2>&1; then
        echo "gnu"
        return
    fi

    # 3. Check ldd signature
    if ldd --version 2>&1 | grep -iq "glibc\|gnu"; then
        echo "gnu"
        return
    fi

    if ldd --version 2>&1 | grep -iq "musl"; then
        echo "musl"
        return
    fi

    # 4. Check for dynamic linkers in /lib or /lib64
    if ls /lib/ld-musl-*.so* >/dev/null 2>&1 || ls /lib64/ld-musl-*.so* >/dev/null 2>&1; then
        echo "musl"
        return
    fi

    # 5. Default to GNU
    echo "gnu"
}

case "$OS" in
    Linux)
        LIBC="$(detect_linux_libc)"
        case "$ARCH" in
            x86_64)
                if [ "$LIBC" = "musl" ]; then
                    TARGET="linux-x86_64-musl"
                else
                    TARGET="linux-x86_64"
                fi
                ;;
            aarch64|arm64)
                if [ "$LIBC" = "musl" ]; then
                    TARGET="linux-arm64-musl"
                else
                    TARGET="linux-arm64"
                fi
                ;;
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
# 3. HYDRATE RUNTIME TO LOCAL STORAGE (WITH SHA-256 VERIFICATION)
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST_PATH="$SCRIPT_DIR/system/tools/tools_manifest.json"

# Support hardened systems where /tmp is mounted noexec
BASE_RUNTIME="/tmp"
if [ -n "$XDG_RUNTIME_DIR" ] && [ -w "$XDG_RUNTIME_DIR" ]; then
    BASE_RUNTIME="$XDG_RUNTIME_DIR"
elif [ -d "$HOME/.cache" ] && [ -w "$HOME/.cache" ]; then
    BASE_RUNTIME="$HOME/.cache"
fi

RUNTIME_ROOT="${BASE_RUNTIME}/kykloi_runtime_${TARGET}"
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

extract_python_field() {
    target="$1"
    field="$2"
    manifest="$3"
    awk -v tgt="$target" -v fld="$field" '
        BEGIN { in_py=0; in_tgt=0 }
        /"python"[[:space:]]*:/ { in_py=1; next }
        in_py && $0 ~ "\"" tgt "\"[[:space:]]*:" { in_tgt=1; next }
        in_tgt && $0 ~ "\"" fld "\"[[:space:]]*:" {
            sub(/.*"[^"]+"[[:space:]]*:[[:space:]]*"/, "")
            sub(/".*/, "")
            print $0
            exit
        }
        in_tgt && /}[[:space:]]*,?[[:space:]]*$/ { in_tgt=0 }
    ' "$manifest"
}

if [ ! -f "$LOCAL_PY" ] || [ ! -f "$STAMP_FILE" ]; then
    if [ ! -f "$MANIFEST_PATH" ]; then
        echo "[FATAL] Verification manifest missing at: $MANIFEST_PATH" >&2
        exit 1
    fi

    ARCHIVE_NAME=$(extract_python_field "$TARGET" "archive" "$MANIFEST_PATH")
    EXPECTED_SHA=$(extract_python_field "$TARGET" "sha256" "$MANIFEST_PATH")
    DOWNLOAD_URL=$(extract_python_field "$TARGET" "url" "$MANIFEST_PATH")

    if [ -z "$ARCHIVE_NAME" ] || [ -z "$EXPECTED_SHA" ]; then
        echo "[FATAL] Target ${TARGET} not found in manifest python definitions." >&2
        exit 1
    fi

    ARCHIVE_PY="$SCRIPT_DIR/system/tools/archives/$ARCHIVE_NAME"

    if [ ! -f "$ARCHIVE_PY" ]; then
        echo "[Kykloi] Pre-packaged archive not found locally: $ARCHIVE_NAME"
        echo "[Kykloi] Attempting automatic download..."
        mkdir -p "$SCRIPT_DIR/system/tools/archives"
        if command -v curl >/dev/null 2>&1; then
            curl -fSL "$DOWNLOAD_URL" -o "$ARCHIVE_PY"
        elif command -v wget >/dev/null 2>&1; then
            wget "$DOWNLOAD_URL" -O "$ARCHIVE_PY"
        else
            echo "[FATAL] No network downloader (curl, wget) available and local archive missing." >&2
            exit 1
        fi
    fi

    echo "[Kykloi] Verifying SHA-256 for $ARCHIVE_NAME..."
    ACTUAL_SHA=$(compute_sha256 "$ARCHIVE_PY")

    if [ "$ACTUAL_SHA" != "$EXPECTED_SHA" ]; then
        echo "[FATAL] Checksum verification failed for $ARCHIVE_NAME" >&2
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
