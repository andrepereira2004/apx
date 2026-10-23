#!/usr/bin/env python3
"""Read-only, pilot-bound report for a native Windows v3 recovery review.

This script never repairs GPT, mounts a filesystem, or changes BootNext.
"""
import argparse
import json
from pathlib import Path
import stat
import subprocess
import sys

sys.path.insert(0, '/usr/lib/apx')
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
from apx_native_instances_v3 import validate_plan, canonical_layout
from apx_native_recovery_v3 import assess, hash_extent


def optional_status(path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(info.st_mode) or info.st_size > 256:
        raise ValueError('untrusted recovery status file')
    return path.read_text().strip()


def inspect(plan_path, manifest_path, action, status_dir):
    plan = validate_plan(json.loads(plan_path.read_bytes()))
    if action not in {'relocate', 'rollback'}:
        raise ValueError('unknown recovery action')
    disk = plan['before']['device']
    if disk != '/dev/nvme0n1' or Path('/etc/hostname').read_text().strip() != 'apx-host' or Path('/sys/class/dmi/id/product_name').read_text().strip() != '82JU':
        raise ValueError('recovery report belongs to a different pilot')
    if Path('/sys/class/block/nvme0n1/device/serial').read_text().strip() != plan['disk_serial']:
        raise ValueError('recovery disk serial differs')
    manifest = json.loads(manifest_path.read_bytes())
    assess(plan, manifest, action, None)
    generation = plan['new']['generation']
    status = optional_status(status_dir / ('native-v3-' + generation + '.status'))
    marker = optional_status(status_dir / ('native-v3-' + generation + '.copy-verified'))
    result = subprocess.run(['/usr/bin/sfdisk', '--json', disk], capture_output=True, text=True,
                            timeout=15, env={'PATH': '/usr/bin', 'LC_ALL': 'C'})
    try:
        observed = json.loads(result.stdout)['partitiontable'] if result.returncode == 0 else None
    except (ValueError, KeyError, TypeError):
        observed = None
    table = plan['after'] if action == 'relocate' else plan['before']
    partition = table['partitions'][2]
    sector = table['sectorsize']
    digest = hash_extent(disk, partition['start'] * sector, partition['size'] * sector)
    old_digest = backup_digest = None
    if action == 'relocate' and observed is not None:
        try:
            starting = canonical_layout(observed) == canonical_layout(plan['before'])
        except (ValueError, KeyError, TypeError, AttributeError):
            starting = False
        if starting and isinstance(status, str) and status.startswith(f"{generation}:{plan['plan_sha256']}:relocate:"):
            old = plan['before']['partitions'][2]
            old_digest = hash_extent(disk, old['start'] * sector, old['size'] * sector)
            if old_digest != manifest['original']['sha256']:
                backup = manifest_path.parent / 'original.ntfs.raw'
                info = backup.lstat()
                if not stat.S_ISREG(info.st_mode) or info.st_size != manifest['original']['bytes']:
                    raise ValueError('original backup file identity differs')
                backup_digest = hash_extent(backup, 0, manifest['original']['bytes'])
    return assess(plan, manifest, action, observed, status=status,
                  copy_marker=marker, destination_sha256=digest,
                  original_destination_sha256=old_digest, original_backup_sha256=backup_digest)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True, type=Path)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--action', choices=['relocate', 'rollback'], required=True)
    parser.add_argument('--status-dir', type=Path, default=Path('/boot/EFI/APX/recovery'))
    args = parser.parse_args()
    print(json.dumps(inspect(args.plan, args.manifest, args.action, args.status_dir), sort_keys=True))


if __name__ == '__main__':
    main()
