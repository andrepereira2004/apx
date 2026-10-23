#!/usr/bin/env bash
# Install onto an already installed Arch. Never partitions or formats disks.
set -euo pipefail
readonly here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
exec python3 "$here/install_apx_arch.py" "$@"
