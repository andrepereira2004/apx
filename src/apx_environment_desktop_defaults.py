"""Pinned Environment-only system defaults for nested Flatpak execution."""
from pathlib import Path
import hashlib
import os
import stat

SEED = Path('/usr/share/apx/config-seeds/environment-flatpak-v1')
ASSETS = {'apx-flatpak-nesting-v1': '97305e81f99d29f6fd55c675d40c069368ce93bc67b7d2be762eb605edd3e5a5', 'apx-flatpak-nesting-v1.service': '6ac1facb4c407dce57212a23ba273165e2b21ce85ffa0583e779c13f6fe5b2c0'}


def install_flatpak_defaults(root: Path, seed: Path = SEED) -> None:
    if not root.is_dir() or root.is_symlink() or not seed.is_dir() or seed.is_symlink():
        raise ValueError('desktop defaults root/seed is unsafe')
    if {p.name for p in seed.iterdir()} != set(ASSETS):
        raise ValueError('desktop defaults seed entries differ')
    content = {}
    for name, digest in ASSETS.items():
        p = seed / name
        if p.is_symlink() or not p.is_file() or p.stat().st_size > 16384:
            raise ValueError('desktop defaults asset is unsafe')
        data = p.read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError('desktop defaults asset digest differs')
        content[name] = data
    paths = {
        'apx-flatpak-nesting-v1': 'usr/local/libexec/apx-flatpak-nesting-v1',
        'apx-flatpak-nesting-v1.service': 'etc/systemd/system/apx-flatpak-nesting-v1.service',
    }
    uid, gid = root.stat().st_uid, root.stat().st_gid
    def directory(relative):
        current = root
        for part in Path(relative).parts:
            current /= part
            if current.is_symlink() or (current.exists() and not current.is_dir()):
                raise ValueError('desktop defaults parent is unsafe')
            if not current.exists():
                current.mkdir(mode=0o755); os.chown(current, uid, gid)
    # Validate destinations before writes, preserving safe idempotence.
    targets = [root / rel for rel in paths.values()]
    link = root / 'etc/systemd/system/multi-user.target.wants/apx-flatpak-nesting-v1.service'
    for target in targets:
        directory(target.relative_to(root).parent)
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise ValueError('desktop defaults destination is unsafe')
    directory(link.relative_to(root).parent)
    if link.is_symlink():
        if os.readlink(link) != '../apx-flatpak-nesting-v1.service':
            raise ValueError('desktop defaults activation link differs')
    elif link.exists():
        raise ValueError('desktop defaults activation path differs')
    for name, rel in paths.items():
        p = root / rel
        p.write_bytes(content[name]); os.chown(p,uid,gid)
        os.chmod(p,0o644 if name.endswith('.service') else 0o755)
    if not link.is_symlink():
        link.symlink_to('../apx-flatpak-nesting-v1.service');os.lchown(link,uid,gid)
