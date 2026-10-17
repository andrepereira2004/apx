#!/usr/bin/env python3
"""Owner-requested Environment-local Flatpak authorization repair on Lenovo pilot."""
from pathlib import Path
import datetime, fcntl, hashlib, json, os, shutil

REPO = Path(__file__).resolve().parents[2]
NAME = '49-apx-flatpak-environment.rules'

def main():
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    lock = open('/run/apx/machine-transition-v1.lock', 'a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    assert not Path('/run/apx/system-power-v1.reserved').exists()
    source = REPO / 'config/environment-flatpak-v1' / NAME
    planned = {}
    fallback = (REPO / 'config/environment-flatpak-v1/apx-flatpak-no-revokefs.conf').read_bytes()
    for name in ('hub', 'faculdade', 'hytale', 'minecraft', 'steam'):
        base = Path('/var/lib/apx/environments') / name
        registration = json.loads((base / 'registration.json').read_text())
        assert registration['name'] == name
        assert registration['state'] in ('running', 'stopped')
        assert registration['role'] in ('hub', 'graphical-base')
        root = base / 'root'
        assert root.is_dir() and not root.is_symlink()
        assert any(line.startswith('wheel:') and 'apx' in line.split(':')[3].split(',')
                   for line in (root / 'etc/group').read_text().splitlines())
        metadata = root.stat()
        planned[root / 'etc/systemd/system/flatpak-system-helper.service.d/50-apx-no-revokefs.conf'] = (fallback, metadata.st_uid, metadata.st_gid)
        planned[root / 'etc/polkit-1/rules.d' / NAME] = (source.read_bytes(), metadata.st_uid, metadata.st_gid)
    planned[Path('/usr/share/apx/config-seeds/environment-flatpak-v1') / NAME] = (source.read_bytes(), 0, 0)
    planned[Path('/usr/share/apx/config-seeds/environment-flatpak-v1/apx-flatpak-no-revokefs.conf')] = (fallback, 0, 0)
    planned[Path('/usr/lib/apx/apx_environment_desktop_defaults.py')] = ((REPO / 'src/apx_environment_desktop_defaults.py').read_bytes(), 0, 0)
    for path in planned:
        assert not path.is_symlink() and (not path.exists() or path.is_file())
        parent = path.parent
        while parent != Path('/'):
            assert not parent.is_symlink()
            assert not parent.exists() or parent.is_dir()
            parent = parent.parent
    backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-flatpak-authorization')
    backup.mkdir(mode=0o700)
    manifest = []
    for path, (data, uid, gid) in planned.items():
        item = {'target': str(path), 'existed': path.exists(), 'sha256': hashlib.sha256(data).hexdigest()}
        if path.exists():
            saved = backup / str(path).lstrip('/')
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, saved)
            item['backup'] = str(saved)
            metadata = path.stat()
            item.update(uid=metadata.st_uid, gid=metadata.st_gid, mode=metadata.st_mode & 0o777)
        manifest.append(item)
        (backup / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        missing = []
        parent = path.parent
        while not parent.exists():
            missing.append(parent); parent = parent.parent
        for parent in reversed(missing):
            parent.mkdir(mode=0o755); os.chown(parent, uid, gid)
        temporary = path.with_name(path.name + '.apx-tmp')
        assert not temporary.exists() and not temporary.is_symlink()
        temporary.write_bytes(data)
        os.chown(temporary, uid, gid); os.chmod(temporary, 0o644)
        os.replace(temporary, path)
        assert path.read_bytes() == data
    print(backup)

if __name__ == '__main__':
    main()
