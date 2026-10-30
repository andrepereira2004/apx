#!/usr/bin/env python3
"""Repair the APPS button and Super+R calls in the installed workload shell."""

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
SPEC = importlib.util.spec_from_file_location('apx_rofi_deploy',
    REPO / 'scripts/physical-pilot/deploy-rofi-apps-selection-20260926.py')
DEPLOY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DEPLOY)
OLD_SEED = '489157208ad56631ac70f31029a415eb540f81288d647c8d11bc2edb7f1b4461'
OLD_LIVE = '193ffb4de53ef129df05b10d44576e0f2d6f546e1cb9f1813c48c1359e817cb7'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fixed(data):
    text = data.decode()
    anchor = '    function popupBarTargetAt(x, y) {'
    insert = ('    function toggleApplicationLauncher() {\n'
              '        if (isHub) return\n'
              '        if (popup.open) closePopup()\n'
              '        environmentAppsProcess.running = !environmentAppsProcess.running\n'
              '    }\n\n')
    changes = (
        (anchor, insert + anchor),
        ('            if (root.popup.open) root.closePopup()\n'
         '            environmentAppsProcess.running = !environmentAppsProcess.running',
         '            root.toggleApplicationLauncher()'),
        ('                    onActivated: root.openApplications()',
         '                    onActivated: root.toggleApplicationLauncher()'),
    )
    for old, new in changes:
        if text.count(old) != 1:
            raise RuntimeError('installed QuickShell integration differs')
        text = text.replace(old, new, 1)
    return text.encode()


def main():
    if (Path('/etc/hostname').read_text().strip(),
            Path('/sys/class/dmi/id/product_name').read_text().strip()) != ('apx-host', '82JU'):
        raise RuntimeError('physical Host differs')
    if 'profile=apx-physical-headless-pilot-v1' not in Path('/etc/apx-physical-pilot').read_text().splitlines():
        raise RuntimeError('physical pilot marker differs')
    lock = open('/run/apx/machine-transition-v1.lock', 'a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    rel = 'quickshell/apx/shell.qml'
    targets = [(DEPLOY.SEED / rel, OLD_SEED)] + [(DEPLOY.home_target(name, rel), OLD_LIVE) for name in DEPLOY.NAMES]
    planned = []
    for path, before in targets:
        data = DEPLOY.checked(path)
        if digest(data) != before:
            raise RuntimeError(f'installed QuickShell digest differs: {path}')
        planned.append((path, fixed(data)))
    source = DEPLOY.SOURCE / rel
    if planned[0][1] == source.read_bytes():
        pass
    elif b'function toggleApplicationLauncher()' not in source.read_bytes():
        raise RuntimeError('repository source lacks hotfix')
    source_runtime = REPO / 'scripts/virtual-lab/apx-lab-runtime.py'
    installed_runtime = Path('/usr/lib/apx/apx-lab-runtime.py')
    source_runtime_data = DEPLOY.update_runtime(source_runtime, {rel: source.read_bytes()})
    installed_runtime_data = DEPLOY.update_runtime(installed_runtime, {rel: planned[0][1]})
    planned += [(source_runtime, source_runtime_data), (installed_runtime, installed_runtime_data)]
    recovery = REPO / 'scripts/physical-pilot/recover-development-quota-v1.sh'
    updated, count = re.subn(r'(?m)^readonly RUNTIME_SHA256=[0-9a-f]{64}$',
                             'readonly RUNTIME_SHA256=' + digest(source_runtime_data), recovery.read_text())
    if count != 1:
        raise RuntimeError('recovery runtime pin differs')
    planned.append((recovery, updated.encode()))
    backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-rofi-launcher-hotfix')
    backup.mkdir(mode=0o700)
    manifest = []
    for index, (path, data) in enumerate(planned):
        metadata = path.stat()
        saved = backup / str(index)
        shutil.copy2(path, saved)
        manifest.append({'target': str(path), 'backup': str(saved), 'before': digest(path.read_bytes()),
                         'after': digest(data), 'uid': metadata.st_uid, 'gid': metadata.st_gid,
                         'mode': metadata.st_mode & 0o777})
    (backup / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    for (path, data), entry in zip(planned, manifest):
        descriptor, temporary = tempfile.mkstemp(prefix='.apx-apps-hotfix-', dir=path.parent)
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
            raise RuntimeError(f'write verification failed: {path}')
    print(backup)


if __name__ == '__main__':
    main()
