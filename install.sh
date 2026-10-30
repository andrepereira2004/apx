#!/usr/bin/env bash
# GitHub entry point for a FRESH, already installed Arch host.
set -euo pipefail
readonly repository=https://github.com/andrepereira2004/apx.git
readonly revision=${APX_REF:-apx-arch-base-v1}
mode=${1:---check}
[[ $# -le 1 && ( $mode == --check || $mode == --apply ) ]] || { echo 'Usage: install.sh [--check|--apply]' >&2; exit 2; }
[[ $revision =~ ^[a-zA-Z0-9][a-zA-Z0-9._/-]*$ ]] || { echo 'Invalid APX_REF' >&2; exit 2; }
[[ $EUID -eq 0 ]] || { echo 'Run from the root console of the new Arch installation.' >&2; exit 2; }
source /etc/os-release
[[ $ID == arch && $(uname -m) == x86_64 && -d /run/systemd/system ]] || { echo 'A booted Arch x86_64 installation is required.' >&2; exit 2; }
for path in /var/lib/apx /usr/lib/apx /usr/share/apx /usr/bin/apx /etc/apx-physical-pilot /etc/systemd/system/apx-portable-hub.service /etc/systemd/system/apx-lab-executor.service /etc/systemd/system/apx-portable-network.service /etc/systemd/network/70-apx-portable.network; do
    [[ ! -e $path && ! -L $path ]] || { echo "Existing APX path: $path. Installation refused." >&2; exit 2; }
done
systemd-detect-virt --container --quiet && { echo 'Containers are unsupported.' >&2; exit 2; }
[[ $(findmnt -n -T /var/lib -o FSTYPE) == btrfs ]] || { echo '/var/lib must be on Btrfs.' >&2; exit 2; }
available=$(df -B1 --output=avail /var/lib | tail -n 1)
(( available >= 110 * 1024 * 1024 * 1024 )) || { echo 'At least 110 GiB free is required.' >&2; exit 2; }
if ! command -v git >/dev/null || ! command -v python3 >/dev/null; then
    [[ $mode == --apply ]] || { echo 'Inspection needs git and python; --apply installs them.' >&2; exit 2; }
    pacman -Syu --needed --noconfirm git python
fi
checkout=$(mktemp -d /tmp/apx-install.XXXXXXXX)
trap 'rm -rf -- "$checkout"' EXIT
git clone --depth 1 --single-branch --branch "$revision" "$repository" "$checkout/source"
printf 'Installing APX from GitHub commit: '
git -C "$checkout/source" rev-parse HEAD
bash "$checkout/source/scripts/portable/install-apx-arch.sh" "$mode"
