#!/usr/bin/env python3
"""Show USB bookmark only while the existing media bridge is mounted."""
from pathlib import Path
import datetime
import hashlib
import os
import re
import shutil

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / 'config/environment-shell-v1'
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')
OLD = '"apps:/home/apx/.local/bin/apx-rofi-files-v1"'
NEW = '"apps:/home/apx/.local/bin/apx-rofi-files-v1,filebrowser"'

def main():
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    planned = {}
    relatives = ('gtk-3.0/bookmarks', 'local/bin/apx-removable-bookmark-v1', 'local/bin/apx-shell-v1')
    for environment in ('hub', 'faculdade', 'hytale', 'minecraft', 'steam'):
        home = Path('/var/lib/apx/environments') / environment / 'home/apx'
        target = home / '.config/gtk-3.0/bookmarks'
        text = target.read_text()
        planned[target] = ''.join(l for l in text.splitlines(keepends=True) if l.split(' ', 1)[0] not in ('file:///media/apx-usb', 'file:///media/apx-usb/Ventoy')).encode()
        planned[home / '.local/bin/apx-removable-bookmark-v1'] = (SOURCE / relatives[1]).read_bytes()
        target = home / '.local/bin/apx-shell-v1'
        original = target.read_text()
        needle = "start_desktop_service '^/usr/bin/udiskie([[:space:]]|$)' /usr/bin/udiskie --automount --no-tray"
        addition = "\nstart_desktop_service '[/]apx-removable-bookmark-v1([[:space:]]|$)' \\\n    /home/apx/.local/bin/apx-removable-bookmark-v1 --watch"
        if '/home/apx/.local/bin/apx-removable-bookmark-v1 --watch' not in original:
            assert needle in original
            original = original.replace(needle, needle + addition)
        planned[target] = original.encode()
    for rel in relatives:
        planned[SEED / rel] = (SOURCE / rel).read_bytes()
    for runtime, assets in [(REPO / 'scripts/virtual-lab/apx-lab-runtime.py', SOURCE), (Path('/usr/lib/apx/apx-lab-runtime.py'), SEED)]:
        original = runtime.read_text()
        start = original.index("ENVIRONMENT_SHELL_ASSETS = {")
        end = original.index("\n}", start) + 2
        text = original[start:end]
        for rel in relatives:
            path = assets / rel
            data = planned[path] if path in planned else path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            text, count = re.subn(r'("' + re.escape(rel) + r'": ")[a-f0-9]{64}("[,])', lambda m: m[1] + digest + m[2], text)
            if count == 0:
                text = text.replace("ENVIRONMENT_SHELL_ASSETS = {", "ENVIRONMENT_SHELL_ASSETS = {\n    \"" + rel + "\": \"" + digest + "\",", 1)
            else:
                assert count == 1
        planned[runtime] = (original[:start] + text + original[end:]).encode()
    recovery = REPO / 'scripts/physical-pilot/recover-development-quota-v1.sh'
    text, count = re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$', 'readonly RUNTIME_SHA256=' + hashlib.sha256(planned[REPO / 'scripts/virtual-lab/apx-lab-runtime.py']).hexdigest(), recovery.read_text())
    assert count == 1
    planned[recovery] = text.encode()
    backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-dynamic-usb-bookmark')
    backup.mkdir(mode=0o700)
    for target in planned:
        assert not target.is_symlink()
        assert target.is_file() or target.name in ("apx-removable-bookmark-v1")
    for target, data in planned.items():
        assert not target.is_symlink()
        assert target.is_file() or target.name in ("apx-removable-bookmark-v1")
        saved = backup / str(target).lstrip('/')
        saved.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            shutil.copy2(target, saved)
        else:
            saved.with_suffix(".absent").touch()
        if target.exists():
            metadata = target.stat()
        else:
            ancestor = target.parent
            missing = []
            while not ancestor.exists():
                missing.append(ancestor)
                ancestor = ancestor.parent
            metadata = ancestor.stat()
            for directory in reversed(missing):
                directory.mkdir(mode=0o755)
                os.chown(directory, metadata.st_uid, metadata.st_gid)
        temporary = target.with_name(target.name + '.usb-bookmark-tmp')
        temporary.write_bytes(data)
        os.chmod(temporary, (metadata.st_mode & 0o777) if target.exists() else (0o755 if target.parent.name == "bin" else 0o644))
        os.chown(temporary, metadata.st_uid, metadata.st_gid)
        os.replace(temporary, target)
        assert target.read_bytes() == data
    print(backup)

if __name__ == '__main__':
    main()
