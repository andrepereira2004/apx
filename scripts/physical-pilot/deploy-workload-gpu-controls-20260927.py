#!/usr/bin/env python3
"""Expose confirmed GPU switching in the four physical pilot Environments."""

import datetime
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

REPO = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    'apx_rofi_deploy', REPO / 'scripts/physical-pilot/deploy-rofi-apps-selection-20260926.py')
DEPLOY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DEPLOY)
REL = 'quickshell/apx/shell.qml'
OLD_SEED = '2ff4d51675209f5d0fc5708ca5ce306025a637d9db0f4abe61cd311452d488cf'
OLD_WORKLOAD = 'ba67959632884f259d2a6979451e857b3bb2e4d3aeabb0940812e7a0fc751161'
OLD_BACKEND = 'd97486b97fe26eae994f1a12e4e1d9a0e38e1e2370a693e39c6ae0098b3cc528'
REPLACEMENTS = (
    (b'Rectangle { width: parent.width; height: 1; color: root.controlButtonOutline; visible: root.isHub }',
     b'Rectangle { width: parent.width; height: 1; color: root.controlButtonOutline }'),
    (b'visible: root.isHub\n                            text: "Gr\xc3\xa1ficos',
     b'text: "Gr\xc3\xa1ficos'),
    (b'visible: root.isHub && !root.hardwareConfirmOpen',
     b'visible: !root.hardwareConfirmOpen'),
    (b'visible: root.isHub && root.hardwareConfirmOpen',
     b'visible: root.hardwareConfirmOpen'),
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def updated_qml(data):
    for old, new in REPLACEMENTS:
        if data.count(old) != 1:
            raise RuntimeError('installed GPU control block differs')
        data = data.replace(old, new, 1)
    return data


def main():
    if (Path('/etc/hostname').read_text().strip(),
            Path('/sys/class/dmi/id/product_name').read_text().strip(),
            Path('/sys/class/dmi/id/board_name').read_text().strip()) != (
                'apx-host', '82JU', 'LNVNB161216'):
        raise RuntimeError('physical Host identity differs')
    if 'profile=apx-physical-headless-pilot-v1' not in Path('/etc/apx-physical-pilot').read_text().splitlines():
        raise RuntimeError('physical pilot marker differs')
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if Path('/run/apx/system-power-v1.reserved').exists():
            raise RuntimeError('system power transition reserved')
        if subprocess.run(['/usr/bin/machinectl', 'list', '--no-legend', '--no-pager'],
                          capture_output=True, text=True, check=True).stdout.count('apx-') != 1:
            raise RuntimeError('a workload may be running')
        source_qml = (DEPLOY.SOURCE / REL).read_bytes()
        for _, new in REPLACEMENTS:
            if new not in source_qml:
                raise RuntimeError('repository GPU control block differs')
        targets = [(DEPLOY.SEED / REL, OLD_SEED)] + [
            (DEPLOY.home_target(name, REL), OLD_WORKLOAD) for name in DEPLOY.NAMES]
        planned = []
        for path, expected in targets:
            data = DEPLOY.checked(path)
            if digest(data) != expected:
                raise RuntimeError(f'installed QuickShell differs: {path}')
            planned.append((path, updated_qml(data)))
        backend = Path('/usr/lib/apx/apx-environment-hardware-v1.py')
        if digest(DEPLOY.checked(backend)) != OLD_BACKEND:
            raise RuntimeError('installed workload hardware service differs')
        planned.append((backend, (REPO / 'scripts/physical-pilot/apx-environment-hardware-v1.py').read_bytes()))
        source_runtime = REPO / 'scripts/virtual-lab/apx-lab-runtime.py'
        installed_runtime = Path('/usr/lib/apx/apx-lab-runtime.py')
        next_source_runtime = DEPLOY.update_runtime(source_runtime, {REL: source_qml})
        next_installed_runtime = DEPLOY.update_runtime(installed_runtime, {REL: planned[0][1]})
        recovery = REPO / 'scripts/physical-pilot/recover-development-quota-v1.sh'
        updated_recovery, count = re.subn(
            r'(?m)^readonly RUNTIME_SHA256=[0-9a-f]{64}$',
            'readonly RUNTIME_SHA256=' + digest(next_source_runtime), recovery.read_text())
        if count != 1:
            raise RuntimeError('recovery runtime pin differs')
        planned.extend(((source_runtime, next_source_runtime),
                        (installed_runtime, next_installed_runtime),
                        (recovery, updated_recovery.encode())))
        backup = Path('/var/lib/apx/backups') / (
            datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-workload-gpu-controls')
        backup.mkdir(mode=0o700)
        entries = []
        for index, (path, value) in enumerate(planned):
            if not path.is_file() or path.is_symlink():
                raise RuntimeError(f'unsafe target: {path}')
            meta = path.stat(); saved = backup / str(index)
            shutil.copy2(path, saved)
            entries.append({'target': str(path), 'backup': str(saved),
                            'before': digest(path.read_bytes()), 'after': digest(value),
                            'uid': meta.st_uid, 'gid': meta.st_gid, 'mode': meta.st_mode & 0o777})
        (backup / 'manifest.json').write_text(json.dumps(entries, indent=2) + '\n')
        for (path, value), entry in zip(planned, entries):
            descriptor, temporary = tempfile.mkstemp(prefix='.apx-workload-gpu-', dir=path.parent)
            try:
                with os.fdopen(descriptor, 'wb') as stream:
                    stream.write(value); stream.flush(); os.fsync(stream.fileno())
                os.chown(temporary, entry['uid'], entry['gid'])
                os.chmod(temporary, entry['mode'])
                os.replace(temporary, path)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
            if digest(path.read_bytes()) != entry['after']:
                raise RuntimeError(f'installed digest differs: {path}')
    subprocess.run(['/usr/bin/systemctl', 'restart', 'apx-environment-hardware-v1.service'], check=True)
    print(backup)


if __name__ == '__main__':
    main()
