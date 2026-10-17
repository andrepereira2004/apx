#!/usr/bin/env python3
"""Install APX GTK dialog styling and non-destructive document template defaults."""
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
    import ast
    template_tree = ast.parse((SOURCE / "local/bin/apx-document-templates-v1").read_text())
    templates = ast.literal_eval(next(n.value for n in template_tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "TEMPLATES" for t in n.targets)))
    planned = {}
    relatives = ('gtk-3.0/gtk.css', 'local/bin/apx-document-templates-v1',
                 'local/bin/apx-desktop-activation-v1')
    marker = '/* APX GTK dialogs and menus, including file-operation confirmations. */'
    addition = marker + (SOURCE / relatives[0]).read_text().split(marker, 1)[1]
    for environment in ('hub', 'faculdade', 'hytale', 'minecraft', 'steam'):
        home = Path('/var/lib/apx/environments') / environment / 'home/apx'
        dirs = home / '.config/user-dirs.dirs'
        match = re.search(r'^XDG_TEMPLATES_DIR="\$HOME(?:/([^"\n]*))?"$', dirs.read_text(), re.M) if dirs.exists() else None
        relative = match.group(1) if match else 'Templates'
        if relative and not Path(relative).is_absolute() and '..' not in Path(relative).parts:
            folder = home / relative
            assert not any(p.is_symlink() for p in (folder, *folder.parents) if p.is_relative_to(home))
            for name, content in templates.items():
                target = folder / name
                if not target.exists() and not target.is_symlink():
                    planned[target] = content.encode()
        target = home / '.config/gtk-3.0/gtk.css'
        planned[target] = (target.read_text().split(marker, 1)[0].rstrip() + '\n\n' + addition).encode()
        target = home / '.local/bin/apx-document-templates-v1'
        planned[target] = (SOURCE / relatives[1]).read_bytes()
        target = home / '.local/bin/apx-desktop-activation-v1'
        text = target.read_text()
        line = '"$HOME/.local/bin/apx-document-templates-v1"'
        if line not in text:
            text = text.replace('set -eu\n', 'set -eu\n' + line + '\n', 1)
        planned[target] = text.encode()
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
    backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-document-dialogs')
    backup.mkdir(mode=0o700)
    for target in planned:
        assert not target.is_symlink()
        assert target.is_file() or target.name in ("apx-document-templates-v1", *templates)
    for target, data in planned.items():
        assert not target.is_symlink()
        assert target.is_file() or target.name in ("apx-document-templates-v1", *templates)
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
        temporary = target.with_name(target.name + '.ui-polish-tmp')
        temporary.write_bytes(data)
        os.chmod(temporary, (metadata.st_mode & 0o777) if target.exists() else (0o755 if target.parent.name == "bin" else 0o644))
        os.chown(temporary, metadata.st_uid, metadata.st_gid)
        os.replace(temporary, target)
        assert target.read_bytes() == data
    print(backup)

if __name__ == '__main__':
    main()
