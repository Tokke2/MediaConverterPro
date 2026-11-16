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
WAIT_FOR_PID=0
APP_ARGS=()
while (($#)); do
  case "$1" in
    --update-packages) UPDATE_PACKAGES=1 ;;
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

find_any_python() {
  local candidate candidate_path
  local candidates=("${PYTHON:-}" python3 python /usr/bin/python3 /usr/local/bin/python3 /opt/homebrew/bin/python3 /opt/local/bin/python3 /Library/Frameworks/Python.framework/Versions/Current/bin/python3)
  for candidate in "${candidates[@]}"; do
    [[ -n "$candidate" ]] || continue
    if [[ -x "$candidate" ]]; then candidate_path="$candidate"
    else candidate_path="$(command -v "$candidate" 2>/dev/null)" || continue
    fi
    if "$candidate_path" --version >/dev/null 2>&1; then
      printf '%s\n' "$candidate_path"
      return 0
    fi
  done
  return 1
}

ask_install_python() {
  local answer
  if [[ "$(uname -s)" == Darwin ]] && command -v osascript >/dev/null 2>&1; then
    osascript -e 'display dialog "No Python installation was detected. Install Python using the available OS package manager?" buttons {"Cancel", "Install"} default button "Install" with title "MediaForge"' >/dev/null 2>&1
  elif command -v zenity >/dev/null 2>&1; then
    zenity --question --title='MediaForge' --text='No Python installation was detected. Install the latest Python available for this OS?'
  elif command -v kdialog >/dev/null 2>&1; then
    kdialog --yesno 'No Python installation was detected. Install the latest Python available for this OS?' --title 'MediaForge'
  elif [[ -t 0 ]]; then
    read -r -p 'No Python installation was detected. Install Python now? [y/N] ' answer
    [[ "$answer" =~ ^[Yy]([Ee][Ss])?$ ]]
  else
    write_error 'No graphical consent dialog or terminal is available; Python installation was not attempted.'
    printf '%s\n' 'No Python installation was detected. Run this launcher from Terminal to choose whether to install Python.' >&2
    return 1
  fi
}

run_privileged() {
  if [[ -t 0 && -t 1 ]]; then sudo "$@"
  elif command -v pkexec >/dev/null 2>&1; then pkexec "$@"
  elif command -v sudo >/dev/null 2>&1; then sudo -A "$@"
  else
    write_error 'No supported privilege prompt is available for the OS package manager.'
    return 1
  fi
}

install_python_if_approved() {
  local os_name
  os_name="$(uname -s)"
  if [[ "$os_name" == Darwin ]]; then
    if command -v brew >/dev/null 2>&1; then
      log 'Installing Python through Homebrew after user approval'
      brew install python
    else
      open 'https://www.python.org/downloads/macos/' >/dev/null 2>&1 || true
      write_error 'Homebrew is unavailable; opened the official Python downloads page for manual installation.'
      printf '%s\n' 'Homebrew is not installed. The official Python download page was opened; install Python, then run MediaForge again.' >&2
      return 1
    fi
  elif command -v apt-get >/dev/null 2>&1; then
    log 'Installing the newest repository-supported Python through apt after user approval'
    run_privileged apt-get update && run_privileged apt-get install -y python3 python3-pip
  elif command -v dnf >/dev/null 2>&1; then
    log 'Installing the newest repository-supported Python through dnf after user approval'
    run_privileged dnf install -y python3 python3-pip
  elif command -v pacman >/dev/null 2>&1; then
    log 'Installing the newest repository-supported Python through pacman after user approval'
    run_privileged pacman -S --needed --noconfirm python python-pip
  elif command -v zypper >/dev/null 2>&1; then
    log 'Installing the newest repository-supported Python through zypper after user approval'
    run_privileged zypper refresh && run_privileged zypper install -y python3 python3-pip
  else
    if command -v xdg-open >/dev/null 2>&1; then xdg-open 'https://www.python.org/downloads/' >/dev/null 2>&1 || true; fi
    write_error 'No supported system package manager was found; opened the official Python downloads page when possible.'
    printf '%s\n' 'No supported package manager was found. Install Python 3.10+ using your OS method, then run MediaForge again.' >&2
    return 1
  fi
}

python_info="$(find_python || true)"
if [[ -z "$python_info" ]]; then
  existing_python="$(find_any_python || true)"
  if [[ -n "$existing_python" ]]; then
    write_error "Python was detected at $existing_python, but MediaForge requires Python 3.10 or newer; startup will not offer or install another Python."
    printf 'Python was detected at %s, but MediaForge requires Python 3.10+. Upgrade that installation manually and run MediaForge again.\n' "$existing_python" >&2
    exit 1
  fi
  if ! ask_install_python; then
    log 'Python installation offer declined or unavailable; no Python was detected.'
    exit 0
  fi
  install_python_if_approved
  python_info="$(find_python || true)"
  [[ -n "$python_info" ]] || {
    write_error 'Python installation completed or was attempted, but no compatible Python 3.10+ was detected.'
    printf '%s\n' 'No compatible Python 3.10+ was detected after installation. Check the installer, then run MediaForge again.' >&2
    exit 1
  }
fi
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
