#!/usr/bin/env python3
"""Deploy faster live file enumeration to independent workloads and creation seed."""
import datetime
import fcntl
import hashlib
import os
from pathlib import Path
import re
import shutil

REPO = Path(__file__).resolve().parents[2]
REL = 'local/bin/apx-rofi-files-v1'
SOURCE = REPO / 'config/environment-shell-v1' / REL
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1') / REL


def main():
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        data = SOURCE.read_bytes()
        planned = {SEED: data}
        for name in ('hytale', 'faculdade', 'minecraft', 'steam'):
            planned[Path('/var/lib/apx/environments') / name / 'home/apx/.local/bin/apx-rofi-files-v1'] = data
        digest = hashlib.sha256(data).hexdigest()
        for runtime in (REPO / 'scripts/virtual-lab/apx-lab-runtime.py', Path('/usr/lib/apx/apx-lab-runtime.py')):
            original = runtime.read_text()
            start = original.index('ENVIRONMENT_SHELL_ASSETS = {')
            end = original.index('\n}', start) + 2
            block, count = re.subn(r'("' + re.escape(REL) + r'": ")[a-f0-9]{64}("[,])',
                                  lambda m: m[1] + digest + m[2], original[start:end])
            assert count == 1
            planned[runtime] = (original[:start] + block + original[end:]).encode()
        recovery = REPO / 'scripts/physical-pilot/recover-development-quota-v1.sh'
        text, count = re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$',
                             'readonly RUNTIME_SHA256=' + hashlib.sha256(planned[REPO / 'scripts/virtual-lab/apx-lab-runtime.py']).hexdigest(), recovery.read_text())
        assert count == 1
        planned[recovery] = text.encode()
        backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-rofi-files-speed')
        backup.mkdir(mode=0o700)
        for target in planned:
            assert target.is_file() and not target.is_symlink()
            saved = backup / str(target).lstrip('/')
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, saved)
        for target, data in planned.items():
            metadata = target.stat()
            temporary = target.with_name(target.name + '.rofi-speed-tmp')
            temporary.write_bytes(data)
            os.chown(temporary, metadata.st_uid, metadata.st_gid)
            os.chmod(temporary, metadata.st_mode & 0o777)
            os.replace(temporary, target)
            assert target.read_bytes() == data
        print(backup)


if __name__ == '__main__':
    main()
