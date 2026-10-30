#!/usr/bin/bash
# Executed as the unprivileged Environment account, inside its private bus.
set -euo pipefail
export HOME=/home/apx USER=apx LOGNAME=apx
export XDG_RUNTIME_DIR=/run/apx/session-1000
export XDG_CONFIG_HOME=/home/apx/.config XDG_CACHE_HOME=/home/apx/.cache
export XDG_DATA_HOME=/home/apx/.local/share XDG_SESSION_TYPE=wayland
export XDG_CURRENT_DESKTOP=Hyprland XDG_SESSION_DESKTOP=Hyprland
export LIBSEAT_BACKEND=seatd SEATD_SOCK=/run/seatd.sock
cd /home/apx
children=()
cleanup() {
    for child in "${children[@]}"; do kill -TERM "$child" 2>/dev/null || true; done
    wait || true
}
trap cleanup EXIT HUP INT TERM
pipewire & children+=("$!")
wireplumber & children+=("$!")
pipewire-pulse & children+=("$!")
/usr/bin/start-hyprland --path /usr/lib/apx/apx-portable-compositor.sh -- --config /home/apx/.config/hypr/hyprland.lua &
compositor=$!
children+=("$compositor")
# The reviewed Lua config starts the duplicate-protected APX shell normally.
# A fallback handles a start-event race without bypassing its login flow.
for _ in {1..200}; do
    kill -0 "$compositor" 2>/dev/null || break
    for socket in "$XDG_RUNTIME_DIR"/hypr/*/.socket.sock; do
        [[ -S $socket ]] || continue
        export HYPRLAND_INSTANCE_SIGNATURE=${socket%/.socket.sock}
        HYPRLAND_INSTANCE_SIGNATURE=${HYPRLAND_INSTANCE_SIGNATURE##*/}
        for display_socket in "$XDG_RUNTIME_DIR"/wayland-*; do
            [[ -S $display_socket ]] || continue
            export WAYLAND_DISPLAY=${display_socket##*/}
            break
        done
        [[ -n ${WAYLAND_DISPLAY:-} ]] || continue
        if ! pgrep -u "$(id -u)" -f '/home/apx/.local/bin/apx-shell-v1' >/dev/null; then
            /home/apx/.local/bin/apx-shell-v1 & children+=("$!")
        fi
        break 2
    done
    sleep 0.05
done
wait "$compositor"
