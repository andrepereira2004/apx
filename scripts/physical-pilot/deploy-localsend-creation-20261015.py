#!/usr/bin/env python3
"""Publish the explicitly optional LocalSend creation module, preserving live UI."""
from pathlib import Path
import datetime
import hashlib
import os
import re
import shutil

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / 'config/environment-shell-v1'
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')


def transform(text: str, source: str) -> str:
    if 'key: "iphone-integration"' in text:
        raise RuntimeError('LocalSend creation toggle already exists; inspect before redeploy')
    new_line = next(line for line in source.splitlines() if 'key: "iphone-integration"' in line)
    anchor = '        { key: "printing-scanning",'
    assert text.count(anchor) == 1
    text = text.replace(anchor, new_line + '\n' + anchor, 1)
    for old, new in [
        ('modules: ["office", "communication", "printing-scanning", "development"]',
         'modules: ["office", "communication", "iphone-integration", "printing-scanning", "development"]'),
        ('ArtCraft, câmara, impressão, programação e containers', 'ArtCraft, iPhone, câmara, impressão e programação'),
        ('if (preset === "complete") return environmentModuleCatalog.map(function(item) { return item.key })',
         'if (preset === "complete") return environmentModuleCatalog.filter(function(item) { return item.key !== "iphone-integration" }).map(function(item) { return item.key })'),
        ('item.key !== "office" && item.key !== "development" }).map',
         'item.key !== "office" && item.key !== "development" && item.key !== "iphone-integration" }).map'),
    ]:
        assert text.count(old) == 1, old
        text = text.replace(old, new, 1)
    return text


def main():
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower() == 'e83e08ac-a723-11eb-80ef-38f3aba440bc'
    source = (SOURCE / 'quickshell/apx/shell.qml').read_text()
    planned = {}
    for environment in ('hub', 'faculdade', 'hytale', 'minecraft', 'steam'):
        target = Path('/var/lib/apx/environments') / environment / 'home/apx/.config/quickshell/apx/shell.qml'
        planned[target] = transform(target.read_text(), source).encode()
    planned[SEED / 'quickshell/apx/shell.qml'] = source.encode()
    planned[Path('/usr/lib/apx/apx_environment_features.py')] = (REPO / 'src/apx_environment_features.py').read_bytes()
    for runtime, seed in [(REPO / 'scripts/virtual-lab/apx-lab-runtime.py', SOURCE), (Path('/usr/lib/apx/apx-lab-runtime.py'), SEED)]:
        text = runtime.read_text()
        if '"localsend-bin": "localsend-bin-v1.json"' not in text:
            assert text.count('LOCAL_PACKAGE_MANIFESTS = {') == 1
            text = text.replace('LOCAL_PACKAGE_MANIFESTS = {', 'LOCAL_PACKAGE_MANIFESTS = {\n    "localsend-bin": "localsend-bin-v1.json",', 1)
        digest = hashlib.sha256(planned.get(seed / 'quickshell/apx/shell.qml', source.encode())).hexdigest()
        text, count = re.subn(r'("quickshell/apx/shell.qml": ")[a-f0-9]{64}("[,])', lambda m: m[1] + digest + m[2], text)
        assert count == 1
        planned[runtime] = text.encode()
    recovery = REPO / 'scripts/physical-pilot/recover-development-quota-v1.sh'
    digest = hashlib.sha256(planned[REPO / 'scripts/virtual-lab/apx-lab-runtime.py']).hexdigest()
    text, count = re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$', 'readonly RUNTIME_SHA256=' + digest, recovery.read_text())
    assert count == 1
    planned[recovery] = text.encode()
    for target in planned:
        assert target.is_file() and not target.is_symlink(), target
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = Path('/var/lib/apx/backups') / (stamp + '-localsend-creation')
    backup.mkdir(mode=0o700)
    for target, data in planned.items():
        saved = backup / str(target).lstrip('/')
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, saved)
        metadata = target.stat()
        temporary = target.with_name(target.name + '.localsend-tmp')
        assert not temporary.exists()
        temporary.write_bytes(data)
        os.chmod(temporary, metadata.st_mode & 0o777)
        os.chown(temporary, metadata.st_uid, metadata.st_gid)
        os.replace(temporary, target)
    print(backup)


if __name__ == '__main__':
    main()
