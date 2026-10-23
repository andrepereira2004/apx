"""Pinned Environment-only system defaults for nested Flatpak execution and Environment-local authorization."""
from pathlib import Path
import hashlib
import os
import stat

SEED = Path('/usr/share/apx/config-seeds/environment-flatpak-v1')
ASSETS = {'apx-flatpak-no-revokefs.conf': '55c91eb9e1e69c1d8318ca96fd6a72e038bbfc802b3c6fea94e589a5531ae507', '49-apx-flatpak-environment.rules': 'f21e2026e16b71789fa529ee65711af445774000adc56b6ea578e81cf82b9375', 'apx-flatpak-nesting-v1': '97305e81f99d29f6fd55c675d40c069368ce93bc67b7d2be762eb605edd3e5a5', 'apx-flatpak-nesting-v1.service': '6ac1facb4c407dce57212a23ba273165e2b21ce85ffa0583e779c13f6fe5b2c0'}


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
        'apx-flatpak-no-revokefs.conf': 'etc/systemd/system/flatpak-system-helper.service.d/50-apx-no-revokefs.conf',
        '49-apx-flatpak-environment.rules': 'etc/polkit-1/rules.d/49-apx-flatpak-environment.rules',
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
        os.chmod(p,0o644 if name.endswith(('.service', '.rules', '.conf')) else 0o755)
    if not link.is_symlink():
        link.symlink_to('../apx-flatpak-nesting-v1.service');os.lchown(link,uid,gid)
    install_browser_passkey_defaults(root)


PASSKEY_LAUNCHER_HELPER = r'''#!/usr/bin/python
"""Keep APX passkey support after Environment-local Brave installations/upgrades."""
from pathlib import Path
import sys


def preserve(root=Path('/')):
    if root.is_symlink() or not root.is_dir():
        raise ValueError('unsafe Environment root')
    current = root
    for part in ('usr', 'bin', 'brave'):
        current /= part
        if current.is_symlink():
            raise ValueError('linked Brave launcher path')
    if not current.exists():
        return
    if not current.is_file() or current.stat().st_size > 65536:
        raise ValueError('unsafe Brave launcher')
    source = current.read_text()
    marker = '# APX passkeys: filtered host Bluetooth for the active desktop.'
    if marker in source:
        return
    target = 'exec /opt/brave-bin/brave '
    if target not in source:
        raise ValueError('Brave launcher format changed; APX passkeys requires review')
    block = marker + '\nif [[ -S /run/apx/passkeys-browser-bus ]]; then\n    export DBUS_SYSTEM_BUS_ADDRESS=unix:path=/run/apx/passkeys-browser-bus\nfi\n\n'
    current.write_text(source.replace(target, block + target, 1))


if __name__ == '__main__':
    preserve(Path(sys.argv[1]) if len(sys.argv) == 2 else Path('/'))
'''

PASSKEY_PACKAGE_HOOK = '''[Trigger]
Operation = Install
Operation = Upgrade
Type = Package
Target = brave-bin

[Action]
Description = Preserve APX Bluetooth support for browser passkeys
When = PostTransaction
Exec = /usr/bin/python /usr/local/lib/apx-passkeys/preserve-launcher.py
'''


def install_browser_passkey_defaults(root: Path) -> None:
    """Independent defaults, including when Brave is installed after creation.

    The Host bridge authorizes only the active Environment's user. This installs
    no Host socket, package manager access, credentials, or shared browser data.
    """
    if root.is_symlink() or not root.is_dir():
        raise ValueError('passkey defaults root is unsafe')
    uid, gid = root.stat().st_uid, root.stat().st_gid
    assets = {
        'usr/local/lib/apx-passkeys/preserve-launcher.py': (PASSKEY_LAUNCHER_HELPER, 0o755),
        'etc/pacman.d/hooks/95-apx-passkeys-bluetooth.hook': (PASSKEY_PACKAGE_HOOK, 0o644),
    }
    for relative in assets:
        current = root
        for part in Path(relative).parent.parts:
            current /= part
            if current.is_symlink() or (current.exists() and not current.is_dir()):
                raise ValueError('passkey defaults parent is unsafe')
        target = root / relative
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise ValueError('passkey defaults destination is unsafe')
    # Validate the launcher before writing hooks; skip absent Brave, which its
    # future package-install hook will configure after pacman installs it.
    namespace = {'__name__': 'apx_passkey_launcher'}
    exec(compile(PASSKEY_LAUNCHER_HELPER, '<apx-passkey-launcher>', 'exec'), namespace)
    namespace['preserve'](root)
    for relative, (content, mode) in assets.items():
        current = root
        for part in Path(relative).parent.parts:
            current /= part
            if not current.exists():
                current.mkdir(mode=0o755)
                current.chmod(0o755)
                os.chown(current, uid, gid)
        target = root / relative
        target.write_text(content)
        os.chown(target, uid, gid)
        target.chmod(mode)
