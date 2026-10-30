#!/usr/bin/env python3
"""One-shot owner-requested cleanup of audited, already deleted pilot data.

Never selects current Windows partitions or whole mixed system snapshots.
Default is inspection. --apply unlinks the exact retired lab disk in each
system snapshot, restoring its read-only property even if unlink fails.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess

REPO = Path(__file__).resolve().parents[2]
NAMES = ('developer', 'trabalharei', 'workkk-from-jome')
DATES = ('20260927T161241Z', '20260929T142237Z')
LAB = Path('root/apx-host-development-mode-v1/apx/audit/2026-09-21-input-monitors/windows-lab/disk.raw')


def command(*args):
    return subprocess.check_output(args, text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if os.geteuid() != 0 or os.uname().nodename != 'apx-host' or Path('/sys/class/dmi/id/product_name').read_text().strip() != '82JU':
        raise RuntimeError('only the audited physical pilot is admitted')
    spec = importlib.util.spec_from_file_location('purge_runtime', REPO / 'scripts/virtual-lab/apx-lab-runtime.py')
    runtime = importlib.util.module_from_spec(spec); spec.loader.exec_module(runtime)
    with runtime.local_recovery_lock():
        events = [json.loads(line) for line in runtime.JOURNAL.read_text().splitlines()]
        for name in NAMES:
            if runtime.environment_dir(name).exists() or runtime.registration_path(name).exists() or runtime.machine_running(name):
                raise RuntimeError('cleanup target is no longer absent: ' + name)
            if not any(e.get('name') == name and e.get('recovery') == 'approved-clean-unpublished' and e.get('status') == 'complete' for e in events):
                raise RuntimeError('missing prior approved cleanup evidence: ' + name)
        copies = {name: runtime.local_recovery_snapshots(name) for name in NAMES}
        expected_ids = {417, 427, 423, 433, 424, 434}
        for paths in copies.values():
            for path in paths:
                if int(command('btrfs', 'inspect-internal', 'rootid', str(path))) not in expected_ids:
                    raise RuntimeError('recovery snapshot identity changed')
        snapshots = [runtime.LOCAL_RECOVERY / 'system' / date for date in DATES]
        disks = [(None, Path('/') / LAB)] + [(snapshot, snapshot / LAB) for snapshot in snapshots]
        active_loops = json.loads(command('losetup', '--json'))['loopdevices']
        if active_loops:
            raise RuntimeError('loop devices must be detached before this cleanup')
        qemu = subprocess.run(['pgrep', '-f', '[q]emu-system'], capture_output=True)
        if qemu.returncode != 1:
            raise RuntimeError('QEMU must be stopped before this cleanup')
        report = {'profile': 'audited-deleted-copies-20261004', 'applied': args.apply,
                  'home_snapshots': [str(p) for paths in copies.values() for p in paths], 'lab_disks': []}
        for snapshot, path in disks:
            runtime.trusted_recovery_directory(path.parent)
            if snapshot and command('btrfs', 'property', 'get', '-ts', str(snapshot), 'ro') != 'ro=true':
                raise RuntimeError('system snapshot is not read-only')
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_size != 512110190592:
                raise RuntimeError('retired laboratory disk identity differs')
            report['lab_disks'].append({'path': str(path), 'logical_bytes': info.st_size, 'allocated_bytes': info.st_blocks * 512})
        if args.apply:
            for name, paths in copies.items():
                runtime.purge_local_recovery(name, paths)
                runtime.purge_environment_copies(name)
                runtime.purge_environment_backups(name)
                runtime.purge_environment_plans(name)
            for snapshot, path in disks:
                if snapshot:
                    command('btrfs', 'property', 'set', '-ts', str(snapshot), 'ro', 'false')
                try:
                    path.unlink()
                finally:
                    if snapshot:
                        command('btrfs', 'property', 'set', '-ts', str(snapshot), 'ro', 'true')
                if path.exists():
                    raise RuntimeError('retired disk remains')
            command('btrfs', 'filesystem', 'sync', '/')
            report['verified_absent'] = all(not p.exists() for _, p in disks) and all(not runtime.local_recovery_snapshots(n) for n in NAMES)
            report['system_snapshots_readonly'] = all(command('btrfs', 'property', 'get', '-ts', str(s), 'ro') == 'ro=true' for s in snapshots)
            report['at'] = runtime.now()
            output = REPO / 'audit/2026-10-04-portable/deletion-cleanup.json'
            output.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
