#!/usr/bin/env python3
"""Install the Environment-local pretransaction gate and future-creation hook."""
from pathlib import Path
import datetime
import fcntl
import hashlib
import importlib.util
import json
import os
import shutil

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / 'audit/2026-10-22-zapzap-launch'
if __name__ == '__main__':
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        source = (REPO / 'scripts/virtual-lab/apx-lab-runtime.py').read_text()
        begin = '# Pacman runs this after desktop-entry changes'
        end = 'def copy_environment_shell_seed('
        block = source[source.index(begin):source.index(end)]
        runtime = Path('/usr/lib/apx/apx-lab-runtime.py')
        old = runtime.read_text()
        planned = {runtime: (old[:old.index(begin)] + block + old[old.index(end):]).encode()}
        for directory in sorted(Path('/var/lib/apx/environments').iterdir()):
            if not (directory / 'registration.json').is_file(): continue
            root = directory / 'root'
            if not (root / 'usr/bin/pacman').is_file(): continue
            for relative, filename in (
                ('usr/lib/apx/apx-package-coherence-v1.py', 'apx-package-coherence-v1.py'),
                ('etc/pacman.d/hooks/05-apx-package-coherence.hook', '05-apx-package-coherence.hook'),
            ):
                target = root / relative
                assert not target.is_symlink()
                assert not target.exists() or target.read_bytes() == (REPO / 'config/environment-package-install-v1' / filename).read_bytes()
                planned[target] = (REPO / 'config/environment-package-install-v1' / filename).read_bytes()
        planned = {p: d for p, d in planned.items() if not p.exists() or p.read_bytes() != d}
        if not planned:
            print('Already coherent: zero pending files')
            raise SystemExit(0)
        backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-package-coherence')
        backup.mkdir()
        inventory = []
        for p, d in planned.items():
            assert not p.parent.is_symlink()
            if not p.parent.exists():
                assert p.parent.name == 'apx' and p.parent.parent.name == 'lib'
                st = p.parent.parent.stat()
                p.parent.mkdir(mode=0o755); os.chown(p.parent, st.st_uid, st.st_gid)
            existed = p.exists(); st = p.stat() if existed else p.parent.stat()
            if existed:
                dest = backup / str(p).lstrip('/'); dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, dest)
            inventory.append(dict(path=str(p), existed=existed, uid=st.st_uid, gid=st.st_gid, mode=(st.st_mode & 0o777) if existed else 0o644, after=hashlib.sha256(d).hexdigest()))
        (backup / 'inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')
        for item in inventory:
            p = Path(item['path']); temp = p.with_name(p.name + '.apx-coherence-tmp')
            assert not temp.exists() and not temp.is_symlink()
            temp.write_bytes(planned[p]); os.chmod(temp, item['mode']); os.chown(temp, item['uid'], item['gid']); os.replace(temp, p)
            assert p.read_bytes() == planned[p]
        (OUT / 'coherence-backup.txt').write_text(str(backup) + '\n')
        print(backup); print('Verified', len(planned), 'files')
