#!/usr/bin/env python3
"""Restore the native v3 release pin after the reviewed switch service edit."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


REPO = Path(__file__).resolve().parents[2]
SERVICE = Path('/usr/lib/apx/apx-environment-switch-v1.py')
SOURCE = REPO / 'scripts/physical-pilot/apx-environment-switch-v1.py'
RELEASE = Path('/usr/share/apx/native-v3-enabled.json')
OLD_HASH = '87b0bbd27dc9cbea93c563c51b3c2ccba5a00d72c8a194942cab586e3fd84d34'
NEW_HASH = 'ac28edecd84de240abe4fd6f6cb2154441f86887c31e54b01eaabff0be9cdba2'
BACKUPS = Path('/var/lib/apx/backups')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    require(os.geteuid() == 0, 'requires the physical root Host')
    require(Path('/etc/hostname').read_text().strip() == 'apx-host', 'Host differs')
    require(Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU', 'hardware differs')
    require(Path('/sys/class/block/nvme0n1/device/serial').read_text().strip() == 'S4DYNX0R253702', 'SSD differs')
    require(not Path('/var/lib/apx/native-environments/pending-v3.json').exists(), 'native operation pending')
    require(not Path('/run/apx/environment-management-v1.lock').exists(), 'management operation pending')
    require(subprocess.run(['systemctl', 'is-active', '--quiet', 'apx-environment-switch-v1.service']).returncode == 0,
            'switch service inactive')
    require(digest(SOURCE) == NEW_HASH and digest(SERVICE) == NEW_HASH, 'installed service differs from reviewed source')

    sys.path.insert(0, str(REPO / 'src'))
    import apx_native_hub_v3 as native

    release = json.loads(RELEASE.read_text())
    require(release.get('profile') == 'apx-native-validated-release-v3', 'release profile differs')
    require(set(release.get('files', {})) == native.CRITICAL, 'release file set differs')
    require(release['files'][str(SERVICE)] == OLD_HASH, 'previous service pin differs')
    for name, expected in release['files'].items():
        if name == str(SERVICE):
            continue
        path = Path(name)
        info = path.lstat()
        require(stat.S_ISREG(info.st_mode) and info.st_uid == info.st_gid == 0
                and not info.st_mode & 0o022 and digest(path) == expected,
                'other release file differs: ' + name)
    require(not native.enabled(), 'release already enabled')
    require({(record['name'], record['state']) for record in native.records()}
            == {('windows', 'ready'), ('windows-testes', 'ready')}, 'Windows catalogue differs')

    backup = BACKUPS / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-native-v3-switch-pin')
    backup.mkdir(mode=0o700)
    shutil.copy2(RELEASE, backup / 'native-v3-enabled.json')
    release['files'][str(SERVICE)] = NEW_HASH
    descriptor, temporary = tempfile.mkstemp(prefix='.native-v3-enabled-', dir=RELEASE.parent)
    try:
        os.fchmod(descriptor, 0o400)
        with os.fdopen(descriptor, 'w') as output:
            json.dump(release, output, sort_keys=True, separators=(',', ':'))
            output.write('\n')
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, RELEASE)
        require(native.enabled(), 'release still disabled after pin update')
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        shutil.copy2(backup / 'native-v3-enabled.json', RELEASE)
        raise
    print('native v3 enabled; backup: ' + str(backup))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        print('Native v3 pin repair refused: ' + str(error), file=sys.stderr)
        raise SystemExit(2)
