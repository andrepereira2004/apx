#!/usr/bin/bash
# Keep the upstream launch handshake, but leave crash recovery to APX's
# lifecycle supervisor. A generic safe-mode desktop must not replace APX login.
set -euo pipefail
for argument in "$@"; do
    if [[ $argument == --safe-mode ]]; then
        echo 'APX supervisor owns compositor crash recovery.' >&2
        exit 1
    fi
done
exec /usr/bin/Hyprland "$@"
