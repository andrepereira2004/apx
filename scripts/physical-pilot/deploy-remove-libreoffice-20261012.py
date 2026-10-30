#!/usr/bin/env python3
"""Remove the Office creation option on the owner-authorized physical pilot.

Legacy office module remains admitted for old registrations, with no packages.
Preserve independent live shells and other pending repository changes.
"""
import datetime
import fcntl
import hashlib
import os
from pathlib import Path
import re
import shutil

REPO = Path(__file__).resolve().parents[2]
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')
REL = 'quickshell/apx/shell.qml'


def patch(text):
    text = '\n'.join(line for line in text.split('\n') if '{ key: "office", label:' not in line)
    return text.replace('Office, câmara, impressão, programação e containers', 'Câmara, impressão, programação e containers').replace('modules: ["office", "communication",', 'modules: ["communication",').replace('Tudo do Intermédio, Office e programação.', 'Tudo do Intermédio e programação.').replace('+ LibreOffice · programação', '+ programação')


def main():
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_uuid').read_text().strip() == 'e83e08ac-a723-11eb-80ef-38f3aba440bc'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        planned = {}
        for target in [SEED / REL] + [Path('/var/lib/apx/environments') / name / 'home/apx/.config' / REL for name in ('hub', 'faculdade', 'hytale', 'minecraft', 'steam')]:
            planned[target] = patch(target.read_text()).encode()
        features = Path('/usr/lib/apx/apx_environment_features.py')
        old = features.read_text()
        new = old.replace('"complete": MODULES,', '"complete": tuple(module for module in MODULES if module != "office"),').replace('"office": ("hunspell-en_gb", "libreoffice-fresh"),', '# Legacy registrations may retain office; it no longer installs a suite.\n    "office": (),')
        assert new == (REPO / 'src/apx_environment_features.py').read_text()
        planned[features] = new.encode()
        for runtime in (REPO / 'scripts/virtual-lab/apx-lab-runtime.py', Path('/usr/lib/apx/apx-lab-runtime.py')):
            original = runtime.read_text()
            start = original.index('ENVIRONMENT_SHELL_ASSETS = {')
            end = original.index('\n}', start) + 2
            value = (REPO / 'config/environment-shell-v1' / REL).read_bytes() if runtime.parent.name == 'virtual-lab' else planned[SEED / REL]
            block, count = re.subn(r'("' + re.escape(REL) + r'": ")[a-f0-9]{64}("[,])', lambda m: m[1] + hashlib.sha256(value).hexdigest() + m[2], original[start:end])
            assert count == 1
            planned[runtime] = (original[:start] + block + original[end:]).encode()
        recovery = REPO / 'scripts/physical-pilot/recover-development-quota-v1.sh'
        text, count = re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$', 'readonly RUNTIME_SHA256=' + hashlib.sha256(planned[REPO / 'scripts/virtual-lab/apx-lab-runtime.py']).hexdigest(), recovery.read_text())
        assert count == 1
        planned[recovery] = text.encode()
        backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-remove-libreoffice-menu')
        backup.mkdir(mode=0o700)
        for target in planned:
            assert target.is_file() and not target.is_symlink()
            saved = backup / str(target).lstrip('/')
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, saved)
        for target, data in planned.items():
            metadata = target.stat()
            temporary = target.with_name(target.name + '.office-menu-tmp')
            temporary.write_bytes(data)
            os.chown(temporary, metadata.st_uid, metadata.st_gid)
            os.chmod(temporary, metadata.st_mode & 0o777)
            os.replace(temporary, target)
            assert target.read_bytes() == data
        print(backup)


if __name__ == '__main__':
    main()
