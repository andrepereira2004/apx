#!/usr/bin/bash
set -euo pipefail
exec /usr/bin/python "$(dirname -- "${BASH_SOURCE[0]}")/install_apx_full.py" "$@"
