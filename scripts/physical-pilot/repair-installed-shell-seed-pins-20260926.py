#!/usr/bin/env python3
"""Reconcile two reviewed installed seed variants with the Host digest map."""

import ast
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

RUNTIME = Path('/usr/lib/apx/apx-lab-runtime.py')
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')
EXPECTED = {
    'gtk-3.0/bookmarks': ('3937f6621d3b55203dfe464ade24fe9a14df3cab1f4ae2cfa631d6cbbd26b3b3',
                          '6ed88362969d3a010bab7f9045761a25400e42247c819616d43e3ced9cf9c2a8'),
    'local/bin/apx-laptop-action-v1': ('6ec1dbb32c79ebc816387aa1300560bd3f912d9561e7fb18b6d7d89109a7e4a8',
                                       '5e16b80ab71119567dd42be0debf3b2293dee0823fda32163d799db98da26455'),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    if (Path('/etc/hostname').read_text().strip(),
            Path('/sys/class/dmi/id/product_name').read_text().strip()) != ('apx-host', '82JU'):
        raise RuntimeError('physical Host differs')
    if 'profile=apx-physical-headless-pilot-v1' not in Path('/etc/apx-physical-pilot').read_text().splitlines():
        raise RuntimeError('physical pilot marker differs')
    lock = open('/run/apx/machine-transition-v1.lock', 'a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    old = RUNTIME.read_bytes()
    text = old.decode()
    start = text.index('ENVIRONMENT_SHELL_ASSETS = {')
    end = text.index('\n}', start) + 2
    assets = ast.literal_eval(text[start:end].split(' = ', 1)[1])
    for rel, (before, actual) in EXPECTED.items():
        if assets.get(rel) != before or digest((SEED / rel).read_bytes()) != actual:
            raise RuntimeError(f'installed seed variant differs: {rel}')
        assets[rel] = actual
    updated = (text[:start] + 'ENVIRONMENT_SHELL_ASSETS = '
               + json.dumps(assets, indent=4, sort_keys=True) + text[end:]).encode()
    backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-shell-seed-pin-repair')
    backup.mkdir(mode=0o700)
    saved = backup / 'apx-lab-runtime.py'
    shutil.copy2(RUNTIME, saved)
    metadata = RUNTIME.stat()
    (backup / 'manifest.json').write_text(json.dumps({
        'target': str(RUNTIME), 'backup': str(saved), 'before': digest(old),
        'after': digest(updated), 'uid': metadata.st_uid, 'gid': metadata.st_gid,
        'mode': metadata.st_mode & 0o777,
    }, indent=2) + '\n')
    descriptor, temporary = tempfile.mkstemp(prefix='.apx-seed-pin-', dir=RUNTIME.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(updated)
            stream.flush()
            os.fsync(stream.fileno())
        os.chown(temporary, metadata.st_uid, metadata.st_gid)
        os.chmod(temporary, metadata.st_mode & 0o777)
        os.replace(temporary, RUNTIME)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    if digest(RUNTIME.read_bytes()) != digest(updated):
        raise RuntimeError('runtime write verification failed')
    print(backup)


if __name__ == '__main__':
    main()
