#!/usr/bin/env python3
"""Hide the Thunar tab bar when only one tab is open."""
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
    import xml.etree.ElementTree as ET
    planned = {}
    relatives = ('xfce4/xfconf/xfce-perchannel-xml/thunar.xml',)
    for environment in ('hub', 'faculdade', 'hytale', 'minecraft', 'steam'):
        target = Path('/var/lib/apx/environments') / environment / 'home/apx/.config' / relatives[0]
        root = ET.parse(target).getroot()
        prop = root.find("./property[@name='misc-always-show-tabs']")
        if prop is None:
            prop = ET.SubElement(root, 'property', name='misc-always-show-tabs', type='bool')
        prop.set('value', 'false')
        planned[target] = ET.tostring(root, encoding='utf-8', xml_declaration=True) + b'\n'
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
    backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-thunar-single-tab-bar')
    backup.mkdir(mode=0o700)
    for target in planned:
        assert not target.is_symlink()
        assert target.is_file() or target.name in ("thunar.xml")
    for target, data in planned.items():
        assert not target.is_symlink()
        assert target.is_file() or target.name in ("thunar.xml")
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
        temporary = target.with_name(target.name + '.single-tab-tmp')
        temporary.write_bytes(data)
        os.chmod(temporary, (metadata.st_mode & 0o777) if target.exists() else 0o644)
        os.chown(temporary, metadata.st_uid, metadata.st_gid)
        os.replace(temporary, target)
        assert target.read_bytes() == data
    print(backup)

if __name__ == '__main__':
    main()
