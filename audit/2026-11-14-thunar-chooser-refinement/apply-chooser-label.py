#!/usr/bin/env python3
from pathlib import Path
import datetime, fcntl, hashlib, json, os, re, shutil

repo = Path(__file__).resolve().parents[2]
source = repo / 'config/environment-shell-v1/local/lib/apx'
base = Path('/var/lib/apx/environments')
assert Path('/etc/hostname').read_text().strip() == 'apx-host'
assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text()
with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    homes = [p / 'home/apx' for p in sorted(base.iterdir()) if (p / 'registration.json').is_file()]
    assert len(homes) == 5
    planned = {}
    assets = {f'local/lib/apx/{name}': source / name for name in ('chooser-places.c', 'libchooser-places.so')}
    assets['local/bin/apx-appearance-v1'] = repo / 'config/environment-shell-v1/local/bin/apx-appearance-v1'
    for relative, origin in assets.items():
        payload = origin.read_bytes()
        planned[Path('/usr/share/apx/config-seeds/environment-shell-v1') / relative] = payload
        for home in homes:
            target = (home / '.local' / relative.removeprefix('local/')) if relative.startswith('local/') else (home / '.config' / relative)
            if relative == 'gtk-3.0/gtk.css':
                marker = b'\n/* APX appearance override BEGIN */'
                existing = target.read_bytes()
                if marker in existing:
                    payload_for_home = payload.rstrip(b'\n') + b'\n' + existing[existing.index(marker):]
                else:
                    payload_for_home = payload
            else:
                payload_for_home = payload
            planned[target] = payload_for_home
    digest = lambda data: hashlib.sha256(data).hexdigest()
    for runtime in (repo / 'scripts/virtual-lab/apx-lab-runtime.py', Path('/usr/lib/apx/apx-lab-runtime.py')):
        content = runtime.read_text()
        for relative, origin in assets.items():
            pattern = r'("' + re.escape(relative) + r'": ")[a-f0-9]{64}("[,])'
            content, count = re.subn(pattern, lambda m: m[1] + digest(origin.read_bytes()) + m[2], content)
            assert count == 1
        planned[runtime] = content.encode()
    recovery = repo / 'scripts/physical-pilot/recover-development-quota-v1.sh'
    content, count = re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$',
                             'readonly RUNTIME_SHA256=' + digest(planned[repo / 'scripts/virtual-lab/apx-lab-runtime.py']),
                             recovery.read_text())
    assert count == 1
    planned[recovery] = content.encode()
    planned = {path: data for path, data in planned.items() if path.read_bytes() != data}
    backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-chooser-label')
    backup.mkdir()
    inventory = []
    for path, data in planned.items():
        assert path.is_file() and not path.is_symlink()
        stat = path.stat()
        saved = backup / path.relative_to('/')
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, saved)
        inventory.append({'path': str(path), 'before': digest(path.read_bytes()), 'after': digest(data), 'mode': stat.st_mode & 0o777, 'uid': stat.st_uid, 'gid': stat.st_gid})
    (backup / 'inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')
    for path, data in planned.items():
        stat = path.stat()
        temp = path.with_name(path.name + '.apx-stroke-fix-tmp')
        temp.write_bytes(data)
        os.chmod(temp, stat.st_mode & 0o777)
        os.chown(temp, stat.st_uid, stat.st_gid)
        os.replace(temp, path)
        assert digest(path.read_bytes()) == digest(data)
    print(backup)
    print('Verified', len(planned), 'files')
