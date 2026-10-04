#!/usr/bin/env python3
"""Fresh-host, hardware-independent APX headless installer (not a disk installer)."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
STATE = Path('/var/lib/apx')
RESERVE = 110 * 1024**3
SOURCES = {
    'scripts/virtual-lab/apx-lab-runtime.py': 'apx-lab-runtime-core.py',
    'scripts/portable/apx-portable-runtime.py': 'apx-lab-runtime.py',
    'scripts/virtual-lab/apx-lab-client.py': 'apx-lab-client.py',
    'scripts/virtual-lab/apx-lab-executor.py': 'apx-lab-executor.py',
    'scripts/physical-pilot/apx-environment-network-v1.py': 'apx-environment-network-v1.py',
    'src/apx_environment_features.py': 'apx_environment_features.py',
    'src/apx_environment_desktop_defaults.py': 'apx_environment_desktop_defaults.py',
    'config/environment-flatpak-v1/apx-flatpak-nesting-v1': '/usr/share/apx/config-seeds/environment-flatpak-v1/apx-flatpak-nesting-v1',
    'config/environment-flatpak-v1/apx-flatpak-nesting-v1.service': '/usr/share/apx/config-seeds/environment-flatpak-v1/apx-flatpak-nesting-v1.service',
}
PACKAGES = ['python', 'btrfs-progs', 'systemd', 'nftables', 'arch-install-scripts']
RELEASES = {'minimal': 'minimal-headless-v1', 'development': 'development-headless-v1', 'hub': 'hub-headless-v4'}


def run(*args: str, capture: bool = False, input: str | None = None) -> str:
    result = subprocess.run(args, check=True, text=True, input=input,
                            stdout=subprocess.PIPE if capture else None,
                            env={**os.environ, 'LC_ALL': 'C'})
    return (result.stdout or '').strip()


def quota_state(text: str) -> str:
    fields = {}
    for line in text.splitlines():
        if ':' not in line:
            continue
        key, value = (x.strip().lower() for x in line.split(':', 1))
        if key in {'enabled', 'status', 'mode', 'inconsistent', 'override limits', 'rescan status'}:
            if key in fields:
                raise ValueError('duplicate quota field')
            fields[key] = value
    enabled = [fields[key] for key in ('enabled', 'status') if key in fields]
    if len(enabled) != 1:
        raise ValueError('quota enablement is ambiguous')
    if enabled[0] in {'no', 'disabled'}:
        return 'disabled'
    if (enabled[0] in {'yes', 'enabled'} and fields.get('mode') in {'qgroup', 'qgroup (full accounting)'}
            and fields.get('inconsistent') == 'no' and fields.get('override limits') != 'yes'
            and fields.get('rescan status') != 'running'):
        return 'healthy'
    raise ValueError('Btrfs quota accounting is unsupported or unhealthy')


def preflight() -> dict:
    if os.geteuid() != 0:
        raise ValueError('run as Host root')
    os_release = dict(line.split('=', 1) for line in Path('/etc/os-release').read_text().splitlines() if '=' in line)
    if os_release.get('ID', '').strip('"') != 'arch' or os.uname().machine != 'x86_64':
        raise ValueError('requires Arch Linux x86_64')
    if not Path('/run/systemd/system').is_dir():
        raise ValueError('boot into the installed Arch system first')
    container = subprocess.run(['systemd-detect-virt', '--container', '--quiet']).returncode
    if container == 0:
        raise ValueError('requires a physical Host or a full VM, not a container/chroot')
    for path in (STATE, Path('/usr/lib/apx'), Path('/usr/share/apx'), Path('/usr/bin/apx'), Path('/etc/apx-physical-pilot'),
                 Path('/etc/systemd/system/apx-portable-hub.service'),
                 Path('/etc/systemd/system/apx-lab-executor.service'),
                 Path('/etc/systemd/system/apx-portable-network.service'),
                 Path('/etc/systemd/network/70-apx-portable.network')):
        if path.is_symlink() or (path.exists() and (not path.is_dir() or any(path.iterdir()))):
            raise ValueError(f'existing APX state or destination: {path}; installation refused')
    parent = STATE if STATE.exists() else STATE.parent
    if run('findmnt', '-n', '-T', str(parent), '-o', 'FSTYPE', capture=True) != 'btrfs':
        raise ValueError('/var/lib/apx must reside on Btrfs')
    if shutil.disk_usage(parent).free < RESERVE:
        raise ValueError('at least 110 GiB available required; preserves current 96 GiB APX reserve')
    for relative in SOURCES:
        path = REPO / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f'missing/unsafe source: {relative}')
    quotas = quota_state(run('btrfs', 'quota', 'status', str(parent), capture=True))
    return {'schema': 1, 'profile': 'portable-headless-v1', 'phase': 'checked',
            'packages': PACKAGES, 'quota_state': quotas,
            'source_sha256': {name: hashlib.sha256((REPO / name).read_bytes()).hexdigest() for name in SOURCES},
            'limitations': ['no graphical Hub', 'no native Windows', 'no hardware-specific controls']}


def write(path: Path, content: str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    path.chmod(mode)


def checkpoint(record: dict, phase: str) -> None:
    record['phase'] = phase
    path = STATE / 'portable-install.json'
    temporary = path.with_suffix('.tmp')
    write(temporary, json.dumps(record, indent=2) + '\n', 0o600)
    temporary.replace(path)


def release(role: str) -> None:
    directory = STATE / 'releases' / RELEASES[role]
    directory.mkdir()
    root = directory / 'root'
    run('btrfs', 'subvolume', 'create', str(root))
    packages = ['base', 'python', 'sudo']
    if role == 'development':
        packages += ['git', 'base-devel']
    # Seed public Arch trust into a NEW local keyring; never copy Host secret keys.
    keyring = root / 'etc/pacman.d/gnupg'
    keyring.mkdir(parents=True, mode=0o700)
    run('pacman-key', '--gpgdir', str(keyring), '--init')
    run('pacman-key', '--gpgdir', str(keyring), '--populate', 'archlinux')
    run('pacstrap', '-K', '-c', str(root), *packages)
    write(root / 'etc/hostname', 'apx-release\n')
    write(root / 'etc/machine-id', '')
    write(root / 'etc/locale.conf', 'LANG=C.UTF-8\n')
    write(root / 'etc/systemd/network/20-host0.network', '[Match]\nName=host0\n\n[Network]\nDHCP=ipv4\n')
    resolver = root / 'etc/resolv.conf'
    resolver.unlink(missing_ok=True)
    resolver.symlink_to('/run/systemd/resolve/stub-resolv.conf')
    run('systemctl', '--root', str(root), 'enable', 'systemd-networkd.service', 'systemd-resolved.service')
    run('systemctl', '--root', str(root), 'set-default', 'multi-user.target')
    run('systemd-nspawn', '-q', '-D', str(root), '--register=no', '--private-network',
        'useradd', '--create-home', '--uid', '1000', '--user-group', '--shell', '/bin/bash', 'apx')
    run('passwd', '-R', str(root), '-l', 'root')
    # No installation machine entropy, identity, credentials or writable package cache.
    (root / 'var/lib/systemd/random-seed').unlink(missing_ok=True)
    write(root / 'etc/machine-id', '')
    if role == 'hub':
        shutil.copy2('/usr/lib/apx/apx-lab-client.py', root / 'usr/bin/apx')
    write(directory / 'manifest.json', json.dumps({'schema': 1, 'role': role,
          'backend': 'portable-headless-v1', 'source': 'fresh-pacstrap-not-live-hub'}) + '\n', 0o400)
    run('btrfs', 'property', 'set', '-ts', str(root), 'ro', 'true')


def install(record: dict) -> None:
    # pacstrap creates /etc before package extraction; a root 0077 umask
    # would leave it unreadable to the guest's service users.
    os.umask(0o022)
    STATE.mkdir(mode=0o700, exist_ok=True)
    checkpoint(record, 'started')
    # A full upgrade is intentional: Arch does not support partial upgrades.
    run('pacman', '-Syu', '--needed', '--noconfirm', *PACKAGES)
    if record['quota_state'] == 'disabled':
        run('btrfs', 'quota', 'enable', str(STATE))
        run('btrfs', 'quota', 'rescan', '-w', str(STATE))
    if quota_state(run('btrfs', 'quota', 'status', str(STATE), capture=True)) != 'healthy':
        raise ValueError('quota accounting is not healthy after enablement')
    for directory in ('releases', 'environments', 'plans', 'journal', 'snapshots', 'archives', 'backups', 'catalogue'):
        (STATE / directory).mkdir(mode=0o700)
    library = Path('/usr/lib/apx')
    library.mkdir(mode=0o755, exist_ok=True)
    for source, destination in SOURCES.items():
        (library / destination).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / source, library / destination)
        (library / destination).chmod(0o755)
    Path('/usr/bin/apx').symlink_to('/usr/lib/apx/apx-lab-runtime.py')
    checkpoint(record, 'runtime-installed')
    for role in RELEASES:
        release(role)
        checkpoint(record, f'release-{role}-complete')
    write(Path('/etc/systemd/network/70-apx-portable.network'), '''[Match]
Name=ve-apx-*
Driver=veth

[Network]
Address=0.0.0.0/28
DHCPServer=yes
IPMasquerade=ipv4
LinkLocalAddressing=no

[DHCPServer]
DNS=1.1.1.1 9.9.9.9
''')
    # Closed input and private-network egress boundary for ALL APX headless roles.
    write(library / 'portable-network.nft', '''table inet apx_portable {
 chain input {
  type filter hook input priority -10; policy accept;
  iifname "ve-apx-*" udp dport 67 accept
  iifname "ve-apx-*" drop
 }
 chain forward {
  type filter hook forward priority -10; policy accept;
  iifname "ve-apx-*" meta nfproto ipv6 drop
  iifname "ve-apx-*" ip daddr { 10.0.0.0/8, 100.64.0.0/10, 127.0.0.0/8, 169.254.0.0/16, 172.16.0.0/12, 192.168.0.0/16 } drop
  iifname "ve-apx-*" oifname "ve-*" drop
 }
}
''')
    run('nft', '-c', '-f', str(library / 'portable-network.nft'))
    write(Path('/etc/systemd/system/apx-portable-network.service'), '''[Unit]
Description=APX portable container network boundary
Before=apx-lab-executor.service apx-portable-hub.service

[Service]
Type=oneshot
ExecStart=/usr/bin/nft -f /usr/lib/apx/portable-network.nft
ExecStop=/usr/bin/nft delete table inet apx_portable
RemainAfterExit=yes
''')
    write(Path('/etc/systemd/system/apx-lab-executor.service'), '''[Unit]
Description=APX authenticated headless Hub executor
Requires=apx-portable-network.service
After=apx-portable-network.service systemd-machined.service
RequiresMountsFor=/var/lib/apx

[Service]
ExecStart=/usr/lib/apx/apx-lab-executor.py
Restart=on-failure
RestartSec=2
UMask=0077

[Install]
WantedBy=multi-user.target
''')
    write(Path('/etc/systemd/system/apx-portable-hub.service'), '''[Unit]
Description=APX portable headless Hub
Requires=apx-lab-executor.service systemd-networkd.service
After=apx-lab-executor.service systemd-networkd.service

[Service]
Type=oneshot
ExecStartPre=/usr/bin/timeout 15 /usr/bin/bash -c 'until test -S /run/apx/executor.sock; do sleep 0.1; done'
ExecStart=/usr/bin/apx environment start hub
ExecStop=/usr/bin/apx environment stop hub
RemainAfterExit=yes
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
''')
    plan = json.loads(run('apx', 'environment', 'create-plan', 'hub', '--role', 'hub', capture=True))
    run('apx', 'environment', 'create', '--plan', plan['digest'], '--approve', 'CREATE hub AS hub')
    checkpoint(record, 'hub-created')
    run('systemctl', 'daemon-reload')
    run('systemctl', 'enable', '--now', 'systemd-networkd.service')
    # An already-running networkd keeps the old configuration until reloaded.
    # Load our bounded APX DHCP/DNS policy BEFORE the first veth is created.
    run('networkctl', 'reload')
    run('systemctl', 'enable', '--now', 'apx-lab-executor.service', 'apx-portable-hub.service')
    run('systemctl', 'is-active', 'apx-lab-executor.service', 'apx-portable-hub.service')
    run('apx', 'status')
    checkpoint(record, 'complete')
    print('APX portable HEADLESS base installed. Enter: apx environment shell hub')
    print('Graphical Hub/native Windows are not installed by this experimental adapter.')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument('--check', action='store_true', help='read-only preflight (default)')
    choice.add_argument('--apply', action='store_true', help='install experimental HEADLESS base on a fresh Host')
    args = parser.parse_args()
    try:
        record = preflight()
        print(json.dumps(record, indent=2), flush=True)
        if args.apply:
            install(record)
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'APX portable installer refused/failed: {error}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
