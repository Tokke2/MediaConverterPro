#!/usr/bin/env bash
# Cross-platform launcher for macOS and Linux. All MediaForge-managed state lives
# alongside the application; the operating-system Python runtime is not copied here.
set -euo pipefail

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_FILE="$APP_DIR/fotoverktyg.pyw"
DATA_DIR="$APP_DIR/MediaForge_Data"
VENV_ROOT="$DATA_DIR/PythonEnv"
LOG_DIR="$DATA_DIR/Logs"
CACHE_DIR="$DATA_DIR/PipCache"
TEMP_DIR="$DATA_DIR/Temp"
STARTUP_LOG="$LOG_DIR/launcher.log"
mkdir -p "$VENV_ROOT" "$LOG_DIR" "$CACHE_DIR" "$TEMP_DIR" "$DATA_DIR/Settings"
export PIP_CACHE_DIR="$CACHE_DIR" TMPDIR="$TEMP_DIR" TEMP="$TEMP_DIR" TMP="$TEMP_DIR" PYTHONNOUSERSITE=1

log() { printf '%s | %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$STARTUP_LOG" 2>/dev/null || true; }

UPDATE_PACKAGES=0
INSTALL_LATEST_PYTHON=0
WAIT_FOR_PID=0
while (($#)); do
  case "$1" in
    --update-packages) UPDATE_PACKAGES=1 ;;
    --install-latest-python) INSTALL_LATEST_PYTHON=1 ;;
    --wait-for-pid)
      shift
      [[ $# -gt 0 ]] || { printf '%s\n' 'Missing PID after --wait-for-pid.' >&2; exit 2; }
      WAIT_FOR_PID="$1"
      ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
  esac
  shift
done

if [[ ! -f "$APP_FILE" ]]; then
  printf 'MediaForge could not find %s\n' "$APP_FILE" >&2
  exit 1
fi
if [[ "$WAIT_FOR_PID" =~ ^[1-9][0-9]*$ ]]; then
  while kill -0 "$WAIT_FOR_PID" 2>/dev/null; do sleep 0.4; done
fi

find_python() {
  local candidate version
  for candidate in "${PYTHON:-}" python3 python; do
    [[ -n "$candidate" ]] || continue
    command -v "$candidate" >/dev/null 2>&1 || continue
    if "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
      version="$("$candidate" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
      printf '%s\n' "$candidate" "$version"
      return 0
    fi
  done
  return 1
}

install_or_update_python() {
  if [[ "$(uname -s)" == Darwin ]] && command -v brew >/dev/null 2>&1; then
    printf '%s\n' 'Updating the OS-managed Python runtime with Homebrew…'
    brew update && brew upgrade python || brew install python
  elif command -v apt-get >/dev/null 2>&1; then
    printf '%s\n' 'Updating Python 3 using the system package manager (sudo may be requested)…'
    sudo apt-get update && sudo apt-get install --only-upgrade -y python3 python3-venv || sudo apt-get install -y python3 python3-venv
  elif command -v dnf >/dev/null 2>&1; then
    printf '%s\n' 'Updating Python 3 using the system package manager (sudo may be requested)…'
    sudo dnf upgrade -y python3 || sudo dnf install -y python3
  elif command -v pacman >/dev/null 2>&1; then
    printf '%s\n' 'Updating Python 3 using the system package manager (sudo may be requested)…'
    sudo pacman -Syu --needed python python-pip
  elif command -v zypper >/dev/null 2>&1; then
    printf '%s\n' 'Updating Python 3 using the system package manager (sudo may be requested)…'
    sudo zypper refresh && sudo zypper update -y python3 || sudo zypper install -y python3 python3-venv
  else
    printf '%s\n' 'No supported Python package manager was found. Install the latest stable Python 3.10+ for this OS, then rerun MediaForge.' >&2
    if command -v open >/dev/null 2>&1; then open 'https://www.python.org/downloads/' >/dev/null 2>&1 || true; fi
    return 1
  fi
}

if ((INSTALL_LATEST_PYTHON)); then
  log 'User requested OS Python runtime update'
  install_or_update_python
fi

python_info="$(find_python)" || {
  printf '%s\n' 'Python 3.10+ was not found. Install it with your OS package manager, then run this launcher again.' >&2
  if [[ "$(uname -s)" == Darwin ]] && command -v open >/dev/null 2>&1; then open 'https://www.python.org/downloads/' >/dev/null 2>&1 || true; fi
  exit 1
}
PYTHON="$(sed -n '1p' <<<"$python_info")"
PYTHON_VERSION="$(sed -n '2p' <<<"$python_info")"
VENV_DIR="$VENV_ROOT/py$PYTHON_VERSION"
VENV_PYTHON="$VENV_DIR/bin/python"

if [[ ! -x "$VENV_PYTHON" ]]; then
  "$PYTHON" -m venv "$VENV_DIR" >> "$STARTUP_LOG" 2>&1 || {
    printf 'Could not create a private Python environment. Install venv support for Python %s and retry.\n' "$PYTHON_VERSION" >&2
    exit 1
  }
fi

PROBE='import PyQt6, PIL, pillow_heif, piexif'
if ! "$VENV_PYTHON" -c "$PROBE" >/dev/null 2>&1 || ((UPDATE_PACKAGES)); then
  if ((!UPDATE_PACKAGES)); then
    printf 'MediaForge needs PyQt6, Pillow, pillow-heif and piexif in its private environment.\n'
    read -r -p 'Install the missing Python packages now? [Y/n] ' answer || answer='n'
    case "$answer" in
      ''|y|Y|yes|YES|Yes) ;;
      *) printf 'Installation cancelled. No packages were installed.\n'; exit 1 ;;
    esac
  fi
  log 'Installing/updating app-local Python packages'
  "$VENV_PYTHON" -m pip install --upgrade pip PyQt6 Pillow pillow-heif piexif >> "$STARTUP_LOG" 2>&1 || {
    printf 'Package installation failed. See %s\n' "$STARTUP_LOG" >&2
    exit 1
  }
fi

"$VENV_PYTHON" -c "$PROBE" >/dev/null || {
  printf 'Required Python packages could not be verified. See %s\n' "$STARTUP_LOG" >&2
  exit 1
}
log "Starting MediaForge with Python $PYTHON_VERSION"
exec "$VENV_PYTHON" "$APP_FILE" "$@"
