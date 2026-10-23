#!/usr/bin/env python3
"""Keep the transparent Rofi dismissal regions symmetric after adding a header."""

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


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    if (Path('/etc/hostname').read_text().strip(),
            Path('/sys/class/dmi/id/product_name').read_text().strip()) != ('apx-host', '82JU'):
        raise RuntimeError('physical Host identity differs')
    if 'profile=apx-physical-headless-pilot-v1' not in Path('/etc/apx-physical-pilot').read_text().splitlines():
        raise RuntimeError('physical pilot marker differs')
    lock = open('/run/apx/machine-transition-v1.lock', 'a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    rel = 'rofi/config.rasi'
    source = DEPLOY.SOURCE / rel
    after = source.read_bytes()
    old_line = b'button-dismiss-top, button-dismiss-bottom { height: calc((100% - 436px) / 2); }'
    new_line = b'button-dismiss-top, button-dismiss-bottom { height: calc((100% - 490px) / 2); }'
    before = after.replace(new_line, old_line)
    if after.count(new_line) != 1 or digest(before) != 'a7ae13ec8562ae99cba495fcd4489d1fa43ec6537319e280fbf9ca08da703dad':
        raise RuntimeError('Rofi source differs')
    paths = [DEPLOY.SEED / rel] + [DEPLOY.home_target(name, rel) for name in DEPLOY.NAMES]
    for path in paths:
        if DEPLOY.checked(path) != before:
            raise RuntimeError(f'installed Rofi differs: {path}')
    source_runtime = REPO / 'scripts/virtual-lab/apx-lab-runtime.py'
    installed_runtime = Path('/usr/lib/apx/apx-lab-runtime.py')
    next_source_runtime = DEPLOY.update_runtime(source_runtime, {rel: after})
    next_installed_runtime = DEPLOY.update_runtime(installed_runtime, {rel: after})
    recovery = REPO / 'scripts/physical-pilot/recover-development-quota-v1.sh'
    updated_recovery, count = re.subn(r'(?m)^readonly RUNTIME_SHA256=[0-9a-f]{64}$',
        'readonly RUNTIME_SHA256=' + digest(next_source_runtime), recovery.read_text())
    if count != 1:
        raise RuntimeError('recovery runtime pin differs')
    planned = ([(path, after) for path in paths]
               + [(source_runtime, next_source_runtime),
                  (installed_runtime, next_installed_runtime),
                  (recovery, updated_recovery.encode())])
    backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-rofi-title-height')
    backup.mkdir(mode=0o700)
    manifest = []
    for index, (path, data) in enumerate(planned):
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(f'unsafe target: {path}')
        metadata = path.stat()
        saved = backup / str(index)
        shutil.copy2(path, saved)
        manifest.append({'target': str(path), 'backup': str(saved), 'before': digest(path.read_bytes()),
                         'after': digest(data), 'uid': metadata.st_uid, 'gid': metadata.st_gid,
                         'mode': metadata.st_mode & 0o777})
    (backup / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    for (path, data), entry in zip(planned, manifest):
        descriptor, temporary = tempfile.mkstemp(prefix='.apx-rofi-height-', dir=path.parent)
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
