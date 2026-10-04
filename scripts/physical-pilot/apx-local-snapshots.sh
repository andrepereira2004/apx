#!/usr/bin/bash
set -euo pipefail

# Serialize with APX deletion: a snapshot must not resurrect deleted data.
exec 9>/run/lock/apx-local-recovery.lock
flock -x 9

snapshot_root=/.snapshots/local-recovery
minimum_free=$((30 * 1024 * 1024 * 1024))
timestamp=$(date -u +%Y%m%dT%H%M%SZ)

snapshot_one() {
  local name=$1 source=$2 target free old
  [[ -d $source && ! -L $source ]] || return 0
  btrfs subvolume show "$source" >/dev/null
  target="$snapshot_root/$name"
  install -d -m 0700 "$target"
  mapfile -t old < <(find "$target" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort)
  while (( ${#old[@]} > 1 )); do
    btrfs subvolume delete "$target/${old[0]}"
    old=("${old[@]:1}")
  done
  free=$(stat -f -c '%a %S' / | awk '{print $1 * $2}')
  if (( free < minimum_free )); then
    logger -t apx-local-snapshots "skipped $name: free space below 30 GiB reserve"
    return 0
  fi
  btrfs subvolume snapshot -r "$source" "$target/$timestamp"
}

snapshot_one system /
snapshot_one host-home /home
for environment in /var/lib/apx/environments/*; do
  [[ -d $environment && ! -L $environment ]] || continue
  [[ -f $environment/registration.json && ! -L $environment/registration.json ]] || continue
  name=${environment##*/}
  [[ $name =~ ^[a-z][a-z0-9-]*$ ]] || continue
  snapshot_one "environment-$name-home" "$environment/home"
done
