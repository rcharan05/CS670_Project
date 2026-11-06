#!/usr/bin/env bash
# One-step setup: check prerequisites, install MP-SPDZ, create the Python
# environment and run a smoke test. Works on Linux and on Windows via WSL2.
#
#   bash setup/setup.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "ERROR: $*" >&2; exit 1; }
note() { echo "==> $*"; }

# --- platform -----------------------------------------------------------------
case "$(uname -s)" in
    Linux) ;;
    Darwin) fail "macOS is not supported by the MP-SPDZ release binaries; use a Linux VM." ;;
    *) fail "Run this inside WSL2 (Ubuntu) on Windows, not in Git Bash/MSYS. See README." ;;
esac
[ "$(uname -m)" = x86_64 ] || fail "MP-SPDZ release binaries need an x86-64 CPU (found $(uname -m))."

if grep -qi microsoft /proc/version 2>/dev/null; then
    note "Running under WSL"
    case "$ROOT" in
        /mnt/*) echo "WARNING: the project is on the Windows drive ($ROOT)." >&2
                echo "         It will work, but is much slower. Prefer cloning into your WSL home (~)." >&2 ;;
    esac
fi

# A Windows checkout with CRLF line endings breaks every shell script.
if grep -q $'\r' "$ROOT/setup/install_mpspdz.sh"; then
    fail "setup scripts have Windows (CRLF) line endings. Clone the repository inside WSL,
       or run: git config --global core.autocrlf input && re-clone."
fi

# --- prerequisites ------------------------------------------------------------
missing=()
for cmd in curl tar xz openssl c_rehash python3; do
    command -v "$cmd" >/dev/null || missing+=("$cmd")
done
if [ ${#missing[@]} -gt 0 ]; then
    fail "missing commands: ${missing[*]}
       On Ubuntu/WSL install them with:
         sudo apt update && sudo apt install -y curl xz-utils openssl python3 python3-venv"
fi
python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))' \
    || fail "Python >= 3.10 required (found $(python3 --version))."
python3 -c 'import ensurepip, venv' 2>/dev/null \
    || fail "Python venv support missing. Install it with: sudo apt install -y python3-venv"

# --- MP-SPDZ ------------------------------------------------------------------
note "Installing MP-SPDZ"
mkdir -p "$ROOT/third_party"
bash "$ROOT/setup/install_mpspdz.sh" > "$ROOT/third_party/install.log" 2>&1 \
    || { tail -20 "$ROOT/third_party/install.log" >&2; fail "MP-SPDZ installation failed (see third_party/install.log)"; }

# --- Python environment -------------------------------------------------------
note "Creating Python environment in .venv"
[ -x .venv/bin/python ] || python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt

# --- smoke test ---------------------------------------------------------------
note "Smoke test: 3-server Vickrey auction (arithmetic and binary domain)"
.venv/bin/python -m auction --bids 11 13 9 -k 4 --mech vickrey --check
.venv/bin/python -m auction --bids 11 13 9 -k 4 --mech vickrey --binary --check

note "Setup complete. Try:  .venv/bin/python -m auction --help"
