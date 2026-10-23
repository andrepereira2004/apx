#!/usr/bin/env python3
"""Install the hybrid NVIDIA application action and session policy marker."""

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
APP_REL = 'local/bin/apx-window-apps-v1'
OLD_APP = 'd27075be6981b9a99edadbdaa0b541667e25f5462116e8756a1073e5eec1325d'
OLD_SESSION = '555fdcfda62f601ee000bfa4546826ce153be4ba3c17ce11efdb110aecbbb86e'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def checked(path, expected):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f'Missing or unsafe file: {path}')
    data = path.read_bytes()
    if expected and digest(data) != expected:
        raise RuntimeError(f'Unexpected installed baseline: {path}')
    return data


def main():
    if (Path('/etc/hostname').read_text().strip(),
            Path('/sys/class/dmi/id/product_name').read_text().strip()) != ('apx-host', '82JU'):
        raise RuntimeError('Physical Host differs')
    if 'profile=apx-physical-headless-pilot-v1' not in Path('/etc/apx-physical-pilot').read_text().splitlines():
        raise RuntimeError('Physical pilot marker differs')
    lock = open('/run/apx/machine-transition-v1.lock', 'a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    source_app = checked(DEPLOY.SOURCE / APP_REL, None)
    source_session = checked(REPO / 'scripts/physical-pilot/apx-official-hub-session-v1.sh', None)
    if b'APX_GPU_POLICY="$GPU_POLICY"' not in source_session:
        raise RuntimeError('Source session lacks GPU policy export')
    planned = []
    for path in [DEPLOY.SEED / APP_REL, *(DEPLOY.home_target(name, APP_REL) for name in DEPLOY.NAMES)]:
        checked(path, OLD_APP)
        planned.append((path, source_app))
    session = Path('/var/lib/apx/official-hub-v1/apx-official-hub-session-v1.sh')
    checked(session, OLD_SESSION)
    planned.append((session, source_session))
    source_runtime = REPO / 'scripts/virtual-lab/apx-lab-runtime.py'
    installed_runtime = Path('/usr/lib/apx/apx-lab-runtime.py')
    next_source = DEPLOY.update_runtime(source_runtime, {APP_REL: source_app})
    next_installed = DEPLOY.update_runtime(installed_runtime, {APP_REL: source_app})
    planned.extend(((source_runtime, next_source), (installed_runtime, next_installed)))
    recovery = REPO / 'scripts/physical-pilot/recover-development-quota-v1.sh'
    updated, count = re.subn(r'(?m)^readonly RUNTIME_SHA256=[0-9a-f]{64}$',
                             'readonly RUNTIME_SHA256=' + digest(next_source), recovery.read_text())
    if count != 1:
        raise RuntimeError('Recovery runtime pin differs')
    planned.append((recovery, updated.encode()))
    print(f'Validated {len(planned)} files; app={digest(source_app)}')
    if '--apply' not in os.sys.argv[1:]:
        return
    if os.sys.argv[1:] != ['--apply']:
        raise RuntimeError('Unsupported arguments')
    backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-hybrid-nvidia-launch')
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
        descriptor, temporary = tempfile.mkstemp(prefix='.apx-nvidia-', dir=path.parent)
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
            raise RuntimeError(f'Installed digest differs: {path}')
    print(backup)


if __name__ == '__main__':
    main()
