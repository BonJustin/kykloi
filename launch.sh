#!/usr/bin/env sh
set -e

REQ_MAJ="${REQ_MAJ:-3}"
REQ_MIN="${REQ_MIN:-10}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ---------------------------------------------------------------------------
# 0. PARSE CLI FLAGS (e.g. --force-fallback)
# ---------------------------------------------------------------------------
KYKLOI_FORCE_FALLBACK=0
for arg; do
  shift
  case "$arg" in
  --force-fallback)
    KYKLOI_FORCE_FALLBACK=1
    ;;
  *)
    set -- "$@" "$arg"
    ;;
  esac
done
export KYKLOI_FORCE_FALLBACK

# ---------------------------------------------------------------------------
# 1. EVALUATE HOST PYTHON (WITH CANDIDATE PATH PROBING)
# ---------------------------------------------------------------------------
USE_HOST_PY=0
HOST_PY_BIN=""

if [ "${KYKLOI_FORCE_FALLBACK}" != "1" ]; then
  # Probe default PATH, version-explicit binaries, Homebrew, MacPorts, and POSIX trees
  for candidate in \
    "$(command -v python3 2>/dev/null)" \
    "$(command -v python3.14 2>/dev/null)" \
    "$(command -v python3.13 2>/dev/null)" \
    "$(command -v python3.12 2>/dev/null)" \
    "$(command -v python3.11 2>/dev/null)" \
    "$(command -v python3.10 2>/dev/null)" \
    "/opt/homebrew/bin/python3" \
    "/opt/homebrew/bin/python3.14" \
    "/opt/homebrew/bin/python3.13" \
    "/opt/homebrew/bin/python3.12" \
    "/opt/homebrew/bin/python3.11" \
    "/opt/homebrew/bin/python3.10" \
    "/usr/local/bin/python3" \
    "/usr/local/bin/python3.14" \
    "/usr/local/bin/python3.13" \
    "/usr/local/bin/python3.12" \
    "/usr/local/bin/python3.11" \
    "/usr/local/bin/python3.10" \
    "/opt/local/bin/python3" \
    "/opt/local/bin/python3.13" \
    "/opt/local/bin/python3.12" \
    "/opt/local/bin/python3.11" \
    "/opt/local/bin/python3.10" \
    "/usr/pkg/bin/python3" \
    "$HOME/.local/bin/python3"; do

    [ -z "$candidate" ] && continue
    [ ! -x "$candidate" ] && continue

    PY_VER=$("$candidate" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
    MAJ=$(echo "$PY_VER" | cut -d. -f1)
    MIN=$(echo "$PY_VER" | cut -d. -f2)
    MAJ="${MAJ%%[^0-9]*}"
    MIN="${MIN%%[^0-9]*}"
    MAJ="${MAJ:-0}"
    MIN="${MIN:-0}"

    if [ "$MAJ" -eq "$REQ_MAJ" ] && [ "$MIN" -ge "$REQ_MIN" ]; then
      USE_HOST_PY=1
      HOST_PY_BIN="$candidate"
      break
    fi
  done
fi

if [ "$USE_HOST_PY" -eq 1 ]; then
  echo "[Kykloi] Using host Python runtime: ${HOST_PY_BIN} (${PY_VER})"
  exec "$HOST_PY_BIN" "$SCRIPT_DIR/system/launch.py" "$@"
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
  aarch64 | arm64)
    if [ "$LIBC" = "musl" ]; then
      TARGET="linux-arm64-musl"
    else
      TARGET="linux-arm64"
    fi
    ;;
  *)
    echo "[FATAL] Unsupported Linux architecture: $ARCH" >&2
    exit 1
    ;;
  esac
  ;;
Darwin)
  case "$ARCH" in
  x86_64) TARGET="macos-x86_64" ;;
  arm64) TARGET="macos-arm64" ;;
  *)
    echo "[FATAL] Unsupported macOS architecture: $ARCH" >&2
    exit 1
    ;;
  esac
  ;;
MINGW* | MSYS* | CYGWIN*)
  # Delegate Windows POSIX environments directly to launch.bat
  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -W 2>/dev/null || pwd)"
  exec cmd.exe /c "${SCRIPT_DIR}\\launch.bat" "$@"
  ;;
*)
  echo "[FATAL] Unsupported operating system: $OS" >&2
  exit 1
  ;;
esac

# ---------------------------------------------------------------------------
# 3. HYDRATE RUNTIME TO LOCAL STORAGE (WITH SHA-256 VERIFICATION)
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST_PATH="$SCRIPT_DIR/system/tools/tools-manifest.json"

test_exec_mount() {
  candidate_dir="$1"
  mkdir -p "$candidate_dir" 2>/dev/null || return 1
  probe_file="$candidate_dir/.probe_$$"
  printf '#!/bin/sh\nexit 0\n' >"$probe_file" 2>/dev/null || return 1
  chmod +x "$probe_file" 2>/dev/null || {
    rm -f "$probe_file"
    return 1
  }
  if "$probe_file" 2>/dev/null; then
    rm -f "$probe_file"
    return 0
  fi
  rm -f "$probe_file"
  return 1
}

resolve_runtime_base() {
  if [ -n "$KYKLOI_RUNTIME_DIR" ]; then
    if test_exec_mount "$KYKLOI_RUNTIME_DIR"; then
      echo "$KYKLOI_RUNTIME_DIR"
      return 0
    else
      echo "[ERROR] Specified KYKLOI_RUNTIME_DIR='$KYKLOI_RUNTIME_DIR' is not executable (noexec or permission denied)." >&2
    fi
  fi

  CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/kykloi"
  if test_exec_mount "$CACHE_DIR"; then
    echo "$CACHE_DIR"
    return 0
  fi

  if test_exec_mount "/var/tmp/kykloi"; then
    echo "/var/tmp/kykloi"
    return 0
  fi

  if test_exec_mount "/tmp/kykloi"; then
    echo "/tmp/kykloi"
    return 0
  fi

  return 1
}

if ! BASE_RUNTIME="$(resolve_runtime_base)"; then
  echo "" >&2
  echo "==================== [FATAL EXECUTION BOUNDARY ERROR] ====================" >&2
  echo "Kykloi could not identify an executable location to unpack portable tools." >&2
  echo "All standard cache and temporary directories reject execution (noexec mount" >&2
  echo "or insufficient filesystem permissions):" >&2
  echo "  - \${XDG_CACHE_HOME:-~/.cache}/kykloi" >&2
  echo "  - /var/tmp/kykloi" >&2
  echo "  - /tmp/kykloi" >&2
  echo "" >&2
  echo "Remediation Options:" >&2
  echo "  1. Install system Python (>= 3.10) and Pandoc using your OS package manager." >&2
  echo "     Kykloi will automatically prioritize native host tools over bundled archives." >&2
  echo "  2. Designate an authorized executable partition via environment variable:" >&2
  echo "     export KYKLOI_RUNTIME_DIR=\"/path/to/executable/directory\"" >&2
  echo "==========================================================================" >&2
  exit 1
fi

RUNTIME_ROOT="${BASE_RUNTIME}/runtime_${TARGET}"
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

  if [ -z "$ARCHIVE_NAME" ] || [ -z "$EXPECTED_SHA" ]; then
    echo "[FATAL] Target ${TARGET} not found in manifest python definitions." >&2
    exit 1
  fi

  ARCHIVE_PY="$SCRIPT_DIR/system/tools/archives/$ARCHIVE_NAME"

  if [ ! -f "$ARCHIVE_PY" ]; then
    echo "[FATAL] Pre-packaged archive not found: $ARCHIVE_NAME" >&2
    echo "        Expected at: $ARCHIVE_PY" >&2
    exit 1
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
  printf "%s" "$ACTUAL_SHA" >"$STAMP_FILE"

  if [ "$OS" = "Darwin" ]; then
    xattr -dr com.apple.quarantine "$RUNTIME_ROOT" 2>/dev/null || true
  fi
fi

# ---------------------------------------------------------------------------
# 4. EXECUTE APPLICATION LAUNCHER
# ---------------------------------------------------------------------------
echo "[Kykloi] Using fallback Python runtime: $LOCAL_PY"
exec "$LOCAL_PY" "$SCRIPT_DIR/system/launch.py" "$@"
