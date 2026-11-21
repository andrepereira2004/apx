#!/usr/bin/bash
set -euo pipefail
while IFS= read -r member; do
    [[ "$member" =~ ^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$ ]] || exit 2
    device="/dev/disk/by-partuuid/$member"
    for ((attempt=0; attempt<60; attempt++)); do
        [[ -b "$device" ]] && break
        /usr/bin/sleep 1
    done
    [[ -b "$device" ]] || { echo "APX: missing Linux storage member $member" >&2; exit 2; }
    /usr/bin/btrfs device scan "$device"
done </etc/apx-portable-btrfs-members-v4
