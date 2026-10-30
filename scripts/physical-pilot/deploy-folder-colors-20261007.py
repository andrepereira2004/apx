#!/usr/bin/env python3
"""Install Environment-local folder color actions and thumbnailer."""
from pathlib import Path
import datetime
import hashlib
import os
import re
import shutil

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / 'config/environment-shell-v1'
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')

def main():
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    import xml.etree.ElementTree as ET
    planned = {}
    relatives = ('local/share/icons/APX-Graphite/scalable/places/apx-folder-tagged.svg',
                 'local/bin/apx-folder-color-v1',
                 'local/share/thumbnailers/apx-folder-color.thumbnailer', 'Thunar/uca.xml',
                 'local/bin/apx-rofi-files-v1', 'local/bin/apx-desktop-activation-v1',
                 'local/bin/apx-desktop-preferences-v1', 'hypr/hyprland.lua',
                 'apx/locale.env', 'environment.d/80-apx-locale.conf')
    new_actions = ET.parse(SOURCE / 'Thunar/uca.xml').getroot()
    source_hypr = (SOURCE / 'hypr/hyprland.lua').read_text()
    locale_block = source_hypr[source_hypr.index('-- Apply Environment-local language'):source_hypr.index('hl.env("XDG_DATA_DIRS",')]
    for environment in ('hub', 'faculdade', 'hytale', 'minecraft', 'steam'):
        base = Path('/var/lib/apx/environments') / environment
        home = base / 'home/apx'
        # Confirm translations and locale exist before changing language.
        if (base / 'root/usr/bin/thunar').exists():
            assert (base / 'root/usr/share/locale/pt/LC_MESSAGES/thunar.mo').is_file()
        import subprocess
        available = subprocess.check_output(['chroot', str(base / 'root'), '/usr/bin/locale', '-a'], text=True)
        assert 'pt_PT.utf8' in available.splitlines()
        for rel in relatives:
            if rel in ('Thunar/uca.xml', 'hypr/hyprland.lua'):
                continue
            target = home / ('.' + rel if rel.startswith('local/') else '.config/' + rel)
            planned[target] = (SOURCE / rel).read_bytes()
        target = home / '.config/Thunar/uca.xml'
        root = ET.parse(target).getroot() if target.exists() else ET.Element('actions')
        for action in list(root):
            if action.findtext('command', '').startswith('/home/apx/.local/bin/apx-folder-color-v1 '):
                root.remove(action)
        for action in new_actions:
            if action.findtext('command', '').startswith('/home/apx/.local/bin/apx-folder-color-v1 '):
                root.append(action)
        planned[target] = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        target = home / '.config/hypr/hyprland.lua'
        text = target.read_text()
        if '-- Apply Environment-local language' not in text:
            text += '\n' + locale_block
        if 'name = "apx-folder-controls"' not in text:
            text += '\n' + source_hypr[source_hypr.index('-- Small folder customization controls'):]
        planned[target] = text.encode()
        planned[base / 'root/etc/locale.conf'] = b'LANG=pt_PT.UTF-8\n'
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
    backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-folder-colors')
    backup.mkdir(mode=0o700)
    for target in planned:
        assert not target.is_symlink()
        assert target.is_file() or target.name in {Path(rel).name for rel in relatives}
    for target, data in planned.items():
        assert not target.is_symlink()
        assert target.is_file() or target.name in {Path(rel).name for rel in relatives}
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
        temporary = target.with_name(target.name + '.folder-colors-tmp')
        temporary.write_bytes(data)
        os.chmod(temporary, (metadata.st_mode & 0o777) if target.exists() else (0o755 if target.parent.name == "bin" else 0o644))
        os.chown(temporary, metadata.st_uid, metadata.st_gid)
        os.replace(temporary, target)
        assert target.read_bytes() == data
    print(backup)

if __name__ == '__main__':
    main()
