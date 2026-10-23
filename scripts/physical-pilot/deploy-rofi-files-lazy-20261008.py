#!/usr/bin/env python3
"""Deploy async per-folder Files mode, preserving each workload's shell settings."""
import datetime
import fcntl
import hashlib
import os
from pathlib import Path
import re
import shutil

REPO = Path(__file__).resolve().parents[2]
ASSETS = ('local/bin/apx-rofi-files-v1', 'local/lib/rofi/apx-rofi-files-v1.so', 'quickshell/apx/shell.qml')
OLD = '"/usr/bin/rofi", "-modi", "apps:/home/apx/.local/bin/apx-window-apps-v1,files:/home/apx/.local/bin/apx-rofi-files-v1"'
NEW = '"ROFI_PLUGIN_PATH=/home/apx/.local/lib/rofi", "/usr/bin/rofi", "-modi", "apps:/home/apx/.local/bin/apx-window-apps-v1,files"'


def main():
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        seed = Path('/usr/share/apx/config-seeds/environment-shell-v1')
        planned = {}
        new_owners = {}
        for base in [seed] + [Path('/var/lib/apx/environments') / name / 'home/apx' for name in ('hytale', 'faculdade', 'minecraft', 'steam')]:
            for rel in ASSETS:
                target = base / rel if base == seed else base / ('.local' if rel.startswith('local/') else '.config') / (rel[6:] if rel.startswith('local/') else rel)
                data = (REPO / 'config/environment-shell-v1' / rel).read_bytes()
                if rel.endswith('shell.qml'):
                    original = target.read_text()
                    assert original.count(OLD) + original.count(NEW) == 1
                    data = original.replace(OLD, NEW).encode()
                planned[target] = data
                if not target.exists():
                    metadata = (base if base != seed else seed / 'local').stat()
                    new_owners[target] = (metadata.st_uid, metadata.st_gid)
        for runtime, origin in ((REPO / 'scripts/virtual-lab/apx-lab-runtime.py', REPO / 'config/environment-shell-v1'), (Path('/usr/lib/apx/apx-lab-runtime.py'), seed)):
            original = runtime.read_text()
            start = original.index('ENVIRONMENT_SHELL_ASSETS = {'); end = original.index('\n}', start) + 2
            block = original[start:end]
            for rel in ASSETS:
                data = planned.get(origin / rel, (origin / rel).read_bytes() if (origin / rel).exists() else b'')
                assert data
                digest = hashlib.sha256(data).hexdigest()
                pattern = r'("' + re.escape(rel) + r'": ")[a-f0-9]{64}("[,])'
                block, count = re.subn(pattern, lambda m: m[1] + digest + m[2], block)
                if not count:
                    assert rel == 'local/lib/rofi/apx-rofi-files-v1.so'
                    block = block[:-2] + f'\n    "{rel}": "{digest}",\n}}'
                else:
                    assert count == 1
            planned[runtime] = (original[:start] + block + original[end:]).encode()
        recovery = REPO / 'scripts/physical-pilot/recover-development-quota-v1.sh'
        text, count = re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$', 'readonly RUNTIME_SHA256=' + hashlib.sha256(planned[REPO / 'scripts/virtual-lab/apx-lab-runtime.py']).hexdigest(), recovery.read_text())
        assert count == 1; planned[recovery] = text.encode()
        backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-rofi-files-lazy')
        backup.mkdir(mode=0o700)
        for target in planned:
            assert not target.is_symlink()
            if target.exists():
                assert target.is_file()
                saved = backup / str(target).lstrip('/'); saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, saved)
        (backup / 'new-targets.txt').write_text('\n'.join(map(str, new_owners)) + '\n')
        for target, data in planned.items():
            if target in new_owners:
                uid, gid = new_owners[target]
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                os.chown(target.parent, uid, gid)
                permissions = 0o600
            else:
                metadata = target.stat(); uid, gid = metadata.st_uid, metadata.st_gid; permissions = metadata.st_mode & 0o777
            temporary = target.with_name(target.name + '.rofi-lazy-tmp')
            temporary.write_bytes(data); os.chown(temporary, uid, gid); os.chmod(temporary, permissions)
            os.replace(temporary, target); assert target.read_bytes() == data
        print(backup)


if __name__ == '__main__':
    main()
