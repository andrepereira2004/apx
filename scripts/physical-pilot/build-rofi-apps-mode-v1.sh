#!/usr/bin/env bash
# Run in a development Environment with the installed Rofi ABI 7 headers.
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo=$(cd -- "$script_dir/../.." && pwd)
read -r -a native_flags <<< "$(pkg-config --cflags --libs gio-2.0 json-glib-1.0 cairo gmodule-2.0)"
cc -shared -fPIC -Wall -Wextra -Werror -O2 \
  "$script_dir/apx-rofi-apps-mode-v1.c" \
  -o "${1:-$repo/config/environment-shell-v1/local/lib/rofi/apx-rofi-apps-v1.so}" \
  "${native_flags[@]}"
