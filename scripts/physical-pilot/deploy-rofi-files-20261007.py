#!/usr/bin/env python3
"""Install separate Rofi app/file modes, preserving local QuickShell differences."""
from pathlib import Path
import datetime
import hashlib
import os
import re
import shutil

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / 'config/environment-shell-v1'
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')
OLD = '"apps:/home/apx/.local/bin/apx-window-apps-v1"'
NEW = '"apps:/home/apx/.local/bin/apx-window-apps-v1,filebrowser"'

def main():
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    planned = {}
    for base in [SEED] + [Path('/var/lib/apx/environments') / name / 'home/apx/.config' for name in ('hub', 'faculdade', 'hytale', 'minecraft', 'steam')]:
        config = base / 'rofi/config.rasi'
        qml = base / 'quickshell/apx/shell.qml'
        assert config.is_file() and not config.is_symlink()
        assert qml.is_file() and not qml.is_symlink()
        text = qml.read_text()
        assert text.count(OLD) == 1, qml
        planned[config] = (SOURCE / 'rofi/config.rasi').read_bytes()
        planned[qml] = text.replace(OLD, NEW).encode()
    for runtime, assets in [(REPO / 'scripts/virtual-lab/apx-lab-runtime.py', SOURCE), (Path('/usr/lib/apx/apx-lab-runtime.py'), SEED)]:
        original = runtime.read_text()
        start = original.index("ENVIRONMENT_SHELL_ASSETS = {")
        end = original.index("\n}", start) + 2
        text = original[start:end]
        for rel in ('rofi/config.rasi', 'quickshell/apx/shell.qml'):
            path = assets / rel
            data = planned.get(path, path.read_bytes())
            digest = hashlib.sha256(data).hexdigest()
            text, count = re.subn(r'("' + re.escape(rel) + r'": ")[a-f0-9]{64}("[,])', lambda m: m[1] + digest + m[2], text)
            assert count == 1
        planned[runtime] = (original[:start] + text + original[end:]).encode()
    recovery = REPO / 'scripts/physical-pilot/recover-development-quota-v1.sh'
    text, count = re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$', 'readonly RUNTIME_SHA256=' + hashlib.sha256(planned[REPO / 'scripts/virtual-lab/apx-lab-runtime.py']).hexdigest(), recovery.read_text())
    assert count == 1
    planned[recovery] = text.encode()
    backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-rofi-files')
    backup.mkdir(mode=0o700)
    for target, data in planned.items():
        assert target.is_file() and not target.is_symlink()
        saved = backup / str(target).lstrip('/')
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, saved)
        metadata = target.stat()
        temporary = target.with_name(target.name + '.rofi-files-tmp')
        temporary.write_bytes(data)
        os.chmod(temporary, metadata.st_mode & 0o777)
        os.chown(temporary, metadata.st_uid, metadata.st_gid)
        os.replace(temporary, target)
        assert target.read_bytes() == data
    print(backup)

if __name__ == '__main__':
    main()
