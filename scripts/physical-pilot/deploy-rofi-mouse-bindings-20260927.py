#!/usr/bin/env python3
"""Separate Rofi primary and secondary pointer actions in workload QuickShell."""

import datetime
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

REPO = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    'apx_rofi_deploy', REPO / 'scripts/physical-pilot/deploy-rofi-apps-selection-20260926.py')
DEPLOY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DEPLOY)
OLD_SEED = 'be6e886b5389fc4c456ea75ead50054170f92c03ef0076d395ac63d55e248f5f'
OLD_LIVE = '7488ced4baaa1b74151d702c4887b5290017a5c1675d5253a93ae991562502fc'
OLD_BINDING = b'"-me-accept-entry", "", "-me-accept-custom", "MousePrimary,MouseSecondary"'
NEW_BINDING = b'"-me-accept-entry", "MousePrimary", "-me-accept-custom", "MouseSecondary"'


def digest(data):
    return hashlib.sha256(data).hexdigest()


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
        rel = 'quickshell/apx/shell.qml'
        source = (DEPLOY.SOURCE / rel).read_bytes()
        if source.count(NEW_BINDING) != 1 or OLD_BINDING in source:
            raise RuntimeError('repository QuickShell binding differs')
        targets = [(DEPLOY.SEED / rel, OLD_SEED)] + [
            (DEPLOY.home_target(name, rel), OLD_LIVE) for name in DEPLOY.NAMES]
        planned = []
        for path, expected in targets:
            before = DEPLOY.checked(path)
            if digest(before) != expected or before.count(OLD_BINDING) != 1:
                raise RuntimeError(f'installed QuickShell differs: {path}')
            planned.append((path, before.replace(OLD_BINDING, NEW_BINDING)))
        source_runtime = REPO / 'scripts/virtual-lab/apx-lab-runtime.py'
        installed_runtime = Path('/usr/lib/apx/apx-lab-runtime.py')
        next_source_runtime = DEPLOY.update_runtime(source_runtime, {rel: source})
        next_installed_runtime = DEPLOY.update_runtime(installed_runtime, {rel: planned[0][1]})
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
            datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-rofi-mouse-bindings')
        backup.mkdir(mode=0o700)
        entries = []
        for index, (path, data) in enumerate(planned):
            if not path.is_file() or path.is_symlink():
                raise RuntimeError(f'unsafe target: {path}')
            metadata = path.stat()
            saved = backup / str(index)
            shutil.copy2(path, saved)
            entries.append({'target': str(path), 'backup': str(saved),
                            'before': digest(path.read_bytes()), 'after': digest(data),
                            'uid': metadata.st_uid, 'gid': metadata.st_gid,
                            'mode': metadata.st_mode & 0o777})
        (backup / 'manifest.json').write_text(json.dumps(entries, indent=2) + '\n')
        for (path, data), entry in zip(planned, entries):
            descriptor, temporary = tempfile.mkstemp(prefix='.apx-rofi-mouse-', dir=path.parent)
            try:
                with os.fdopen(descriptor, 'wb') as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.chown(temporary, entry['uid'], entry['gid'])
                os.chmod(temporary, entry['mode'])
                os.replace(temporary, path)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
            if digest(path.read_bytes()) != entry['after']:
                raise RuntimeError(f'installed digest differs: {path}')
        print(backup)


if __name__ == '__main__':
    main()
