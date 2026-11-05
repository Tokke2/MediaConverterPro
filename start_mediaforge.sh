#!/usr/bin/env bash
# Cross-platform launcher for macOS and Linux. All MediaForge-managed state lives
# alongside the application; the operating-system Python runtime is not copied here.
set -Eeuo pipefail

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_FILE="$APP_DIR/fotoverktyg.pyw"
DATA_DIR="$APP_DIR/MediaForge_Data"
VENV_ROOT="$DATA_DIR/PythonEnv"
LOG_DIR="$APP_DIR/Logs"
ARCHIVE_DIR="$LOG_DIR/Archive"
CACHE_DIR="$DATA_DIR/PipCache"
TEMP_DIR="$DATA_DIR/Temp"
STARTUP_LOG="$LOG_DIR/launcher.log"
ERROR_LOG="$LOG_DIR/errors.log"
mkdir -p "$VENV_ROOT" "$LOG_DIR" "$ARCHIVE_DIR" "$CACHE_DIR" "$TEMP_DIR" "$DATA_DIR/Settings"

archive_previous_launcher_log() {
  [[ -f "$STARTUP_LOG" ]] || return 0
  local modified_date today target
  modified_date="$(stat -f '%Sm' -t '%Y-%m-%d' "$STARTUP_LOG" 2>/dev/null || true)"
  if [[ ! "$modified_date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    modified_date="$(stat -c '%y' "$STARTUP_LOG" 2>/dev/null || true)"
    modified_date="${modified_date%% *}"
  fi
  today="$(date '+%Y-%m-%d')"
  [[ "$modified_date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ && "$modified_date" < "$today" ]] || return 0
  target="$ARCHIVE_DIR/launcher-$modified_date.log"
  [[ -e "$target" ]] && target="$ARCHIVE_DIR/launcher-$modified_date-$(date '+%H%M%S').log"
  mv "$STARTUP_LOG" "$target" 2>/dev/null || true
}
archive_previous_launcher_log
export PIP_CACHE_DIR="$CACHE_DIR" TMPDIR="$TEMP_DIR" TEMP="$TEMP_DIR" TMP="$TEMP_DIR" PYTHONNOUSERSITE=1

log() { printf '%s | %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$STARTUP_LOG" 2>/dev/null || true; }
write_error() {
  local message="$*"
  printf '%s | ERROR | %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$message" >> "$ERROR_LOG" 2>/dev/null || true
  log "ERROR: $message"
}
on_error() {
  local status=$?
  write_error "Launcher command failed (exit $status) at line $1: $2"
  exit "$status"
}
trap 'on_error "$LINENO" "$BASH_COMMAND"' ERR

UPDATE_PACKAGES=0
INSTALL_LATEST_PYTHON=0
WAIT_FOR_PID=0
while (($#)); do
  case "$1" in
    --update-packages) UPDATE_PACKAGES=1 ;;
    --install-latest-python) INSTALL_LATEST_PYTHON=1 ;;
    --wait-for-pid)
      shift
      [[ $# -gt 0 ]] || { write_error 'Missing PID after --wait-for-pid'; printf '%s\n' 'Missing PID after --wait-for-pid.' >&2; exit 2; }
      WAIT_FOR_PID="$1"
      ;;
    *) write_error "Unknown launcher option: $1"; printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
  esac
  shift
done

if [[ ! -f "$APP_FILE" ]]; then
  write_error "MediaForge could not find $APP_FILE"
  printf 'MediaForge could not find %s\n' "$APP_FILE" >&2
  exit 1
fi
if [[ "$WAIT_FOR_PID" =~ ^[1-9][0-9]*$ ]]; then
  while kill -0 "$WAIT_FOR_PID" 2>/dev/null; do sleep 0.4; done
fi

find_python() {
  local candidate candidate_path version
  for candidate in "${PYTHON:-}" python3 python; do
    [[ -n "$candidate" ]] || continue
    candidate_path="$(command -v "$candidate" 2>/dev/null)" || continue
    if "$candidate_path" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
      version="$("$candidate_path" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
      printf '%s\n' "$candidate_path" "$version"
      return 0
    fi
  done
  return 1
}

install_or_update_python() {
  local action="$1" existing_python="${2:-}"
  if [[ "$(uname -s)" == Darwin ]] && command -v brew >/dev/null 2>&1; then
    if [[ "$action" == update ]]; then
      brew list --versions python >/dev/null 2>&1 || { printf '%s\n' 'The installed Python is not managed by Homebrew; it was left unchanged and no second Python was installed.' >&2; return 1; }
      printf '%s\n' 'Updating the existing Homebrew Python runtime…'
      brew update && brew upgrade python
    else
      printf '%s\n' 'No compatible Python was found; installing Python with Homebrew…'
      brew update && brew install python
    fi
  elif command -v apt-get >/dev/null 2>&1; then
    if [[ "$action" == update ]]; then
      dpkg-query -S "$existing_python" >/dev/null 2>&1 || { printf '%s\n' 'The installed Python is not managed by apt; it was left unchanged and no second Python was installed.' >&2; return 1; }
      printf '%s\n' 'Updating the existing apt-managed Python runtime…'
      sudo apt-get update && sudo apt-get install --only-upgrade -y python3 python3-venv
    else
      printf '%s\n' 'No compatible Python was found; installing Python through apt…'
      sudo apt-get update && sudo apt-get install -y python3 python3-venv
    fi
  elif command -v dnf >/dev/null 2>&1; then
    if [[ "$action" == update ]]; then
      rpm -qf "$existing_python" >/dev/null 2>&1 || { printf '%s\n' 'The installed Python is not managed by dnf; it was left unchanged and no second Python was installed.' >&2; return 1; }
      printf '%s\n' 'Updating the existing dnf-managed Python runtime…'
      sudo dnf upgrade -y python3
    else
      printf '%s\n' 'No compatible Python was found; installing Python through dnf…'
      sudo dnf install -y python3
    fi
  elif command -v pacman >/dev/null 2>&1; then
    if [[ "$action" == update ]]; then
      pacman -Qo "$existing_python" >/dev/null 2>&1 || { printf '%s\n' 'The installed Python is not managed by pacman; it was left unchanged and no second Python was installed.' >&2; return 1; }
      printf '%s\n' 'Updating the existing pacman-managed Python runtime…'
      sudo pacman -Syu --needed python python-pip
    else
      printf '%s\n' 'No compatible Python was found; installing Python through pacman…'
      sudo pacman -Syu --needed python python-pip
    fi
  elif command -v zypper >/dev/null 2>&1; then
    if [[ "$action" == update ]]; then
      rpm -qf "$existing_python" >/dev/null 2>&1 || { printf '%s\n' 'The installed Python is not managed by zypper; it was left unchanged and no second Python was installed.' >&2; return 1; }
      printf '%s\n' 'Updating the existing zypper-managed Python runtime…'
      sudo zypper refresh && sudo zypper update -y python3
    else
      printf '%s\n' 'No compatible Python was found; installing Python through zypper…'
      sudo zypper refresh && sudo zypper install -y python3 python3-venv
    fi
  else
    printf '%s\n' 'No supported Python package manager was found. Existing Python was not replaced; no second installation was attempted.' >&2
    if [[ "$action" == install ]]; then
      printf '%s\n' 'Install Python 3.10+ manually, then rerun MediaForge.' >&2
      if command -v open >/dev/null 2>&1; then open 'https://www.python.org/downloads/' >/dev/null 2>&1 || true; fi
    fi
    return 1
  fi
}

python_info="$(find_python || true)"
if ((INSTALL_LATEST_PYTHON)); then
  if [[ -n "$python_info" ]]; then
    log 'User requested an update of the existing OS Python runtime'
    install_or_update_python update "$(sed -n '1p' <<<"$python_info")"
  else
    log 'No compatible Python found; user requested installation of the latest runtime'
    install_or_update_python install
  fi
  python_info="$(find_python || true)"
fi

[[ -n "$python_info" ]] || {
  write_error 'Python 3.10+ was not found'
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
    write_error "Could not create private Python environment for Python $PYTHON_VERSION"
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
    write_error 'Python package installation failed'
    printf 'Package installation failed. See %s\n' "$STARTUP_LOG" >&2
    exit 1
  }
fi

"$VENV_PYTHON" -c "$PROBE" >/dev/null || {
  write_error 'Required Python packages could not be verified after installation'
  printf 'Required Python packages could not be verified. See %s\n' "$STARTUP_LOG" >&2
  exit 1
}
log "Starting MediaForge with Python $PYTHON_VERSION"
if command -v nohup >/dev/null 2>&1; then
  nohup "$VENV_PYTHON" "$APP_FILE" "$@" </dev/null >> "$STARTUP_LOG" 2>&1 &
else
  "$VENV_PYTHON" "$APP_FILE" "$@" </dev/null >> "$STARTUP_LOG" 2>&1 &
fi
APP_PID=$!
if command -v disown >/dev/null 2>&1; then disown "$APP_PID" 2>/dev/null || true; fi
log "Started MediaForge without an attached console (PID $APP_PID, Python $PYTHON_VERSION)"
