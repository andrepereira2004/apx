#!/usr/bin/env python3
"""Install deferred GPU firmware readback for the exact physical pilot."""

import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / 'scripts/physical-pilot/apx-system-power-v1.py'
TARGET = Path('/usr/lib/apx/apx-system-power-v1.py')
OLD = '565f73e137ecef54e5810f96a35cb4d0187145f2e5d666b45b6493fbeae38f1a'


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
        if not TARGET.is_file() or TARGET.is_symlink() or digest(TARGET.read_bytes()) != OLD:
            raise RuntimeError('installed power service differs')
        data = SOURCE.read_bytes()
        if b'A same-boot read may still report' not in data or b'"event": "gpu-request-rejected"' not in data:
            raise RuntimeError('source does not contain expected GPU fix and logging')
        backup = Path('/var/lib/apx/backups') / (
            datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-gpu-deferred-readback')
        backup.mkdir(mode=0o700)
        saved = backup / '0'
        shutil.copy2(TARGET, saved)
        metadata = TARGET.stat()
        entry = {'target': str(TARGET), 'backup': str(saved), 'before': OLD,
                 'after': digest(data), 'uid': metadata.st_uid, 'gid': metadata.st_gid,
                 'mode': metadata.st_mode & 0o777}
        (backup / 'manifest.json').write_text(json.dumps([entry], indent=2) + '\n')
        descriptor, temporary = tempfile.mkstemp(prefix='.apx-gpu-readback-', dir=TARGET.parent)
        try:
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.chown(temporary, entry['uid'], entry['gid'])
            os.chmod(temporary, entry['mode'])
            os.replace(temporary, TARGET)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        if digest(TARGET.read_bytes()) != entry['after']:
            raise RuntimeError('installed service digest differs')
    subprocess.run(['/usr/bin/systemctl', 'restart', 'apx-system-power-v1.service'], check=True)
    print(backup)


if __name__ == '__main__':
    main()
