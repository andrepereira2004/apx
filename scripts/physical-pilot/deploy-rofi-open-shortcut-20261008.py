#!/usr/bin/env python3
"""Make workload openApplications IPC idempotent; preserve APPS button toggle."""
import datetime
import hashlib
import os
from pathlib import Path
import re
import shutil
import fcntl

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / 'config/environment-shell-v1'
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')
REL = 'quickshell/apx/shell.qml'
OLD = '''            root.toggleApplicationLauncher()
        }

        function toggleApplications(): void { openApplications() }'''
NEW = '''            // Repeated shortcut requests must not cancel a pending launch.
            if (popup.open) root.closePopup()
            if (!environmentAppsProcess.running) environmentAppsProcess.running = true
        }

        function toggleApplications(): void { root.toggleApplicationLauncher() }'''


def main():
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        targets = [SOURCE / REL, SEED / REL] + [
            Path('/var/lib/apx/environments') / name / 'home/apx/.config' / REL
            for name in ('hytale', 'minecraft', 'steam', 'faculdade')]
        planned = {}
        for path in targets:
            assert path.is_file() and not path.is_symlink()
            text = path.read_text()
            assert 'APX_ROFI_' not in text, 'restore temporary diagnostic instrumentation first'
            if text.count(OLD) == 1:
                text = text.replace(OLD, NEW)
            else:
                assert text.count(NEW) == 1, path
            planned[path] = text.encode()
        for runtime, asset in [(REPO / 'scripts/virtual-lab/apx-lab-runtime.py', SOURCE / REL),
                               (Path('/usr/lib/apx/apx-lab-runtime.py'), SEED / REL)]:
            original = runtime.read_text()
            start = original.index('ENVIRONMENT_SHELL_ASSETS = {')
            end = original.index('\n}', start) + 2
            block, count = re.subn(r'("' + re.escape(REL) + r'": ")[a-f0-9]{64}("[,])',
                                  lambda m: m[1] + hashlib.sha256(planned[asset]).hexdigest() + m[2],
                                  original[start:end])
            assert count == 1
            planned[runtime] = (original[:start] + block + original[end:]).encode()
        recovery = REPO / 'scripts/physical-pilot/recover-development-quota-v1.sh'
        text, count = re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$',
                             'readonly RUNTIME_SHA256=' + hashlib.sha256(planned[REPO / 'scripts/virtual-lab/apx-lab-runtime.py']).hexdigest(), recovery.read_text())
        assert count == 1
        planned[recovery] = text.encode()
        backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-rofi-open-shortcut')
        backup.mkdir(mode=0o700)
        for path in planned:
            assert path.is_file() and not path.is_symlink()
            saved = backup / str(path).lstrip('/')
            saved.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                shutil.copy2(path, saved)
            else:
                saved.with_suffix('.absent').touch()
        for path, data in planned.items():
            existed = path.exists()
            metadata = path.stat() if existed else path.parent.stat()
            temporary = path.with_name(path.name + '.rofi-open-tmp')
            temporary.write_bytes(data)
            os.chown(temporary, metadata.st_uid, metadata.st_gid)
            os.chmod(temporary, (metadata.st_mode & 0o777) if existed else 0o755)
            os.replace(temporary, path)
            assert path.read_bytes() == data
        print(backup)


if __name__ == '__main__':
    main()
