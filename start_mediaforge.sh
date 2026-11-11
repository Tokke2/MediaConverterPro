#!/usr/bin/env bash
# Cross-platform launcher for macOS and Linux. App data stays beside the application;
# Python packages use the shared user installation, not an app-specific environment.
set -Eeuo pipefail

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_FILE="$APP_DIR/fotoverktyg.pyw"
DATA_DIR="$APP_DIR/MediaForge_Data"
LOG_DIR="$APP_DIR/Logs"
ARCHIVE_DIR="$LOG_DIR/Archive"
CACHE_DIR="$DATA_DIR/PipCache"
TEMP_DIR="$DATA_DIR/Temp"
STARTUP_LOG="$LOG_DIR/launcher.log"
ERROR_LOG="$LOG_DIR/errors.log"
mkdir -p "$LOG_DIR" "$ARCHIVE_DIR" "$CACHE_DIR" "$TEMP_DIR" "$DATA_DIR/Settings"

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
export PIP_CACHE_DIR="$CACHE_DIR" TMPDIR="$TEMP_DIR" TEMP="$TEMP_DIR" TMP="$TEMP_DIR"
unset PYTHONNOUSERSITE

log() { printf '%s | %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$STARTUP_LOG" 2>/dev/null || true; }
write_error() {
  local message="$*"
  printf '%s | ERROR | %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$message" >> "$ERROR_LOG" 2>/dev/null || true
  log "ERROR: $message"
}
write_warning() {
  local message="$*"
  printf '%s | WARNING | %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$message" >> "$ERROR_LOG" 2>/dev/null || true
  log "WARNING: $message"
}
on_error() {
  local status=$?
  write_error "Launcher command failed (exit $status) at line $1: $2"
  exit "$status"
}
trap 'on_error "$LINENO" "$BASH_COMMAND"' ERR

UPDATE_PACKAGES=0
UPDATE_SYSTEM_PYTHON=0
WAIT_FOR_PID=0
APP_ARGS=()
while (($#)); do
  case "$1" in
    --update-packages) UPDATE_PACKAGES=1 ;;
    --update-system-python|--install-latest-python) UPDATE_SYSTEM_PYTHON=1 ;;
    --wait-for-pid)
      shift
      [[ $# -gt 0 ]] || { write_error 'Missing PID after --wait-for-pid'; printf '%s\n' 'Missing PID after --wait-for-pid.' >&2; exit 2; }
      WAIT_FOR_PID="$1"
      ;;
    -* ) write_error "Unknown launcher option: $1"; printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
    *) APP_ARGS+=("$1") ;;
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
  local candidate candidate_path base_python_path version
  local candidates=("${PYTHON:-}" python3 python /usr/bin/python3 /usr/local/bin/python3 /opt/homebrew/bin/python3 /opt/local/bin/python3 /Library/Frameworks/Python.framework/Versions/Current/bin/python3)
  for candidate in "${candidates[@]}"; do
    [[ -n "$candidate" ]] || continue
    if [[ -x "$candidate" ]]; then
      candidate_path="$candidate"
    else
      candidate_path="$(command -v "$candidate" 2>/dev/null)" || continue
    fi
    if "$candidate_path" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
      base_python_path="$("$candidate_path" -c 'import sys; print(getattr(sys, "_base_executable", sys.executable))' 2>/dev/null)"
      [[ -x "$base_python_path" ]] && candidate_path="$base_python_path"
      version="$("$candidate_path" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
      printf '%s\n' "$candidate_path" "$version"
      return 0
    fi
  done
  return 1
}

update_existing_python() {
  local existing_python="$1"
  [[ -n "$existing_python" ]] || { printf '%s\n' 'No compatible system Python is available; MediaForge will not install one.' >&2; return 1; }
  if [[ "$(uname -s)" == Darwin ]] && command -v brew >/dev/null 2>&1; then
    brew list --versions python >/dev/null 2>&1 || { printf '%s\n' 'The installed Python is not managed by Homebrew; it was left unchanged. No other Python will be installed.' >&2; return 1; }
    printf '%s\n' 'Updating the existing Homebrew Python runtime…'
    brew update && brew upgrade python
  elif command -v apt-get >/dev/null 2>&1; then
    dpkg-query -S "$existing_python" >/dev/null 2>&1 || { printf '%s\n' 'The installed Python is not managed by apt; it was left unchanged. No other Python will be installed.' >&2; return 1; }
    printf '%s\n' 'Updating the existing apt-managed Python runtime…'
    sudo apt-get update && sudo apt-get install --only-upgrade -y python3 python3-pip
  elif command -v dnf >/dev/null 2>&1; then
    rpm -qf "$existing_python" >/dev/null 2>&1 || { printf '%s\n' 'The installed Python is not managed by dnf; it was left unchanged. No other Python will be installed.' >&2; return 1; }
    printf '%s\n' 'Updating the existing dnf-managed Python runtime…'
    sudo dnf upgrade -y python3
  elif command -v pacman >/dev/null 2>&1; then
    pacman -Qo "$existing_python" >/dev/null 2>&1 || { printf '%s\n' 'The installed Python is not managed by pacman; it was left unchanged. No other Python will be installed.' >&2; return 1; }
    printf '%s\n' 'Updating the existing pacman-managed Python runtime…'
    sudo pacman -Syu --needed python python-pip
  elif command -v zypper >/dev/null 2>&1; then
    rpm -qf "$existing_python" >/dev/null 2>&1 || { printf '%s\n' 'The installed Python is not managed by zypper; it was left unchanged. No other Python will be installed.' >&2; return 1; }
    printf '%s\n' 'Updating the existing zypper-managed Python runtime…'
    sudo zypper refresh && sudo zypper update -y python3
  else
    printf '%s\n' 'No supported system package manager was found. The existing Python was left unchanged.' >&2
    return 1
  fi
}

python_info="$(find_python || true)"
if ((UPDATE_SYSTEM_PYTHON)); then
  [[ -n "$python_info" ]] || {
    write_error 'No compatible system Python was found; runtime installation is disabled'
    printf '%s\n' 'No compatible system Python 3.10+ was found. MediaForge will not install a separate Python runtime.' >&2
    exit 1
  }
  log 'User requested an update of the existing system Python runtime'
  update_existing_python "$(sed -n '1p' <<<"$python_info")"
  python_info="$(find_python || true)"
fi

[[ -n "$python_info" ]] || {
  write_error 'No compatible system Python 3.10+ was found; runtime installation is disabled'
  printf '%s\n' 'No compatible system Python 3.10+ was found. MediaForge uses an existing system Python and will not install its own. Install a system Python with your preferred OS method, then launch MediaForge again.' >&2
  exit 1
}
PYTHON="$(sed -n '1p' <<<"$python_info")"
PYTHON_VERSION="$(sed -n '2p' <<<"$python_info")"

PROBE='import PyQt6, PIL, pillow_heif, piexif'
if ! "$PYTHON" -m pip --version >/dev/null 2>&1; then
  if ! "$PYTHON" -m ensurepip --upgrade --user >> "$STARTUP_LOG" 2>&1; then
    write_error "pip is unavailable for existing system Python $PYTHON_VERSION; no Python runtime was installed"
    printf 'pip is not available for the existing Python %s. Enable or install pip for that same runtime, then rerun MediaForge; the launcher will not install Python.\n' "$PYTHON_VERSION" >&2
    exit 1
  fi
  if ! "$PYTHON" -m pip --version >/dev/null 2>&1; then
    write_error "pip could not be enabled for existing system Python $PYTHON_VERSION"
    printf 'pip could not be enabled for the existing Python %s. Install pip for that runtime and retry.\n' "$PYTHON_VERSION" >&2
    exit 1
  fi
fi
packages_available=0
if "$PYTHON" -c "$PROBE" >/dev/null 2>&1; then packages_available=1; fi
if ((UPDATE_PACKAGES)) || ((!packages_available)); then
  PIP_HELP="$("$PYTHON" -m pip install --help 2>/dev/null || true)"
  PIP_ARGS=(install --user --upgrade)
  if [[ "$PIP_HELP" == *--break-system-packages* ]]; then PIP_ARGS+=(--break-system-packages); fi
  PIP_ARGS+=(PyQt6 Pillow pillow-heif piexif)
  if ((UPDATE_PACKAGES)); then
    log 'User requested a shared Python package refresh'
  else
    log 'Required shared Python packages are missing; installing them for this user'
  fi
  if ! "$PYTHON" -m pip "${PIP_ARGS[@]}" >> "$STARTUP_LOG" 2>&1; then
    if ! "$PYTHON" -c "$PROBE" >/dev/null 2>&1; then
      write_error 'Python package installation failed and required shared packages are unavailable'
      printf 'Python package installation failed and required packages are unavailable. See %s\n' "$STARTUP_LOG" >&2
      exit 1
    fi
    write_warning 'Shared Python package update failed; continuing with already installed packages'
  fi
else
  log 'Skipping shared Python package refresh; required packages are available and no manual refresh was requested'
fi
"$PYTHON" -c "$PROBE" >/dev/null || {
  write_error 'Required Python packages could not be verified after the startup update'
  printf 'Required Python packages could not be verified. See %s\n' "$STARTUP_LOG" >&2
  exit 1
}
log "Starting MediaForge with Python $PYTHON_VERSION"
if command -v nohup >/dev/null 2>&1; then
  nohup "$PYTHON" "$APP_FILE" "${APP_ARGS[@]}" </dev/null >> "$STARTUP_LOG" 2>&1 &
else
  "$PYTHON" "$APP_FILE" "${APP_ARGS[@]}" </dev/null >> "$STARTUP_LOG" 2>&1 &
fi
APP_PID=$!
if command -v disown >/dev/null 2>&1; then disown "$APP_PID" 2>/dev/null || true; fi
log "Started MediaForge without an attached console (PID $APP_PID, Python $PYTHON_VERSION)"
