#!/usr/bin/env bash
# Build the Environment-local Rofi secondary-click adapter.
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo=$(cd -- "$script_dir/../.." && pwd)
read -r -a native_flags <<< "$(pkg-config --cflags --libs glib-2.0)"
cc -shared -fPIC -Wall -Wextra -Werror -O2 \
    "$script_dir/apx-rofi-secondary-v1.c" \
    -o "${1:-$repo/config/environment-shell-v1/local/libexec/apx-rofi-secondary-v1.so}" \
    "${native_flags[@]}" -ldl
