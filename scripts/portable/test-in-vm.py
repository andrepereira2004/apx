#!/usr/bin/env python3
"""Build and test in a NEW file-backed Arch VM; no physical disk passthrough."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='new directory for disposable VM and logs')
    parser.add_argument('--qemu-prefix', type=Path, help='optional unpacked QEMU usr/ tree')
    parser.add_argument('--github', action='store_true', help='install using the public GitHub one-command entry point')
    args = parser.parse_args()
    if os.geteuid() != 0 or not os.access('/dev/kvm', os.R_OK | os.W_OK):
        parser.error('Host root and /dev/kvm required for this laboratory harness')
    for tool in ('pacstrap', 'pacman-key', 'arch-chroot', 'mkfs.btrfs', 'systemctl'):
        if not shutil.which(tool):
            parser.error(f'missing Host laboratory tool: {tool}')
    qemu = args.qemu_prefix.resolve() / 'usr/bin/qemu-system-x86_64' if args.qemu_prefix else Path(shutil.which('qemu-system-x86_64') or '/missing-qemu')
    if not qemu.is_file():
        parser.error('QEMU is unavailable')
    output = args.output.absolute()
    if output.exists() or output.is_symlink():
        parser.error('output must be a new directory; no reuse or overwrite')
    if shutil.disk_usage(output.parent).free < 12 * 1024**3:
        parser.error('at least 12 GiB real Host free space required')
    os.umask(0o022)
    output.mkdir(mode=0o700)
    root = output / 'rootfs'; root.mkdir()
    def run(*command, log):
        with (output / log).open('w') as stream:
            subprocess.run(command, check=True, stdout=stream, stderr=subprocess.STDOUT)
    # GnuPG UNIX socket paths cannot fit arbitrarily long output directories.
    with tempfile.TemporaryDirectory(prefix='apx-vm-keys-') as keys:
        run('pacman-key', '--gpgdir', keys, '--init', log='keyring-init.log')
        run('pacman-key', '--gpgdir', keys, '--populate', 'archlinux', log='keyring-populate.log')
        run('gpgconf', '--homedir', keys, '--kill', 'gpg-agent', log='keyring-stop.log')
        keyring = root / 'etc/pacman.d/gnupg'
        keyring.parent.mkdir(parents=True)
        shutil.copytree(keys, keyring)
    run('pacstrap', '-K', '-c', str(root), 'base', 'linux', 'mkinitcpio', 'btrfs-progs', 'python', 'nftables', 'arch-install-scripts', log='pacstrap.log')
    spec = importlib.util.spec_from_file_location('portable', REPO / 'scripts/portable/install_apx_arch.py')
    installer = importlib.util.module_from_spec(spec); spec.loader.exec_module(installer)
    for relative in set(installer.SOURCES) | {'scripts/portable/install-apx-arch.sh', 'scripts/portable/install_apx_arch.py', 'scripts/portable/vm-smoke.py'}:
        target = root / 'root/apx' / relative; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / relative, target)
    def write(relative, text):
        path = root / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text); path.chmod(0o644)
    write('etc/hostname', 'teste-de-vm\n')
    if args.github:
        write('etc/apx-vm-github-source', 'apx-arch-base-v1\n')
    write('etc/fstab', '/dev/vda / btrfs defaults 0 0\n')
    write('etc/machine-id', '')
    write('etc/systemd/network/20-ethernet.network', '[Match]\nName=en* eth*\n\n[Network]\nDHCP=yes\n')
    resolver = root / 'etc/resolv.conf'; resolver.unlink(missing_ok=True); resolver.symlink_to('/run/systemd/resolve/stub-resolv.conf')
    write('etc/mkinitcpio-apx-vm.conf', 'MODULES=(virtio_pci virtio_blk virtio_net btrfs)\nBINARIES=()\nFILES=()\nHOOKS=(base systemd modconf block filesystems)\n')
    write('etc/systemd/system/apx-vm-smoke.service', '''[Unit]
Description=Disposable APX install and lifecycle smoke test
Wants=network-online.target
After=network-online.target apx-portable-hub.service

[Service]
Type=oneshot
ExecStart=/usr/bin/python /root/apx/scripts/portable/vm-smoke.py
StandardOutput=journal+console
StandardError=journal+console
TimeoutStartSec=1800
ExecStopPost=/usr/bin/journalctl -b -u apx-portable-hub -u apx-lab-executor --no-pager
ExecStopPost=/usr/bin/systemctl --no-block poweroff

[Install]
WantedBy=multi-user.target
''')
    # Do NOT order first-install smoke after a unit it will create/start: that
    # would create a job cycle while the installer enables the new Hub.
    service = root / 'etc/systemd/system/apx-vm-smoke.service'
    service.write_text(service.read_text().replace('After=network-online.target apx-portable-hub.service', 'After=network-online.target'))
    run('systemctl', '--root', str(root), 'enable', 'systemd-networkd', 'systemd-resolved', 'systemd-networkd-wait-online', 'apx-vm-smoke', log='enable.log')
    kernels = [p.name for p in (root / 'usr/lib/modules').iterdir() if (p / 'vmlinuz').is_file()]
    if len(kernels) != 1:
        raise RuntimeError('ambiguous guest kernel')
    run('arch-chroot', str(root), 'mkinitcpio', '-k', kernels[0], '-c', '/etc/mkinitcpio-apx-vm.conf', '-g', '/boot/initramfs-apx-vm.img', log='initramfs.log')
    disk = output / 'disk.raw'
    with disk.open('xb') as stream:
        stream.truncate(160 * 1024**3)
    run('mkfs.btrfs', '--rootdir', str(root), '--label', 'APX_TESTE_VM', str(disk), log='mkfs.log')
    command = [str(qemu), '-name', 'Teste de VM', '-machine', 'q35,accel=kvm', '-cpu', 'host', '-m', '4096', '-smp', '4',
        '-nodefaults', '-no-reboot', '-display', 'none', '-kernel', str(root / 'boot/vmlinuz-linux'),
        '-initrd', str(root / 'boot/initramfs-apx-vm.img'), '-append', 'root=/dev/vda rw console=ttyS0 loglevel=4',
        '-drive', 'if=none,id=disk,format=raw,file=' + str(disk), '-device', 'virtio-blk-pci,drive=disk',
        '-netdev', 'user,id=n0', '-device', 'virtio-net-pci,netdev=n0']
    env = os.environ.copy()
    if args.qemu_prefix:
        prefix = args.qemu_prefix.resolve()
        env['LD_LIBRARY_PATH'] = str(prefix / 'usr/lib')
        command += ['-L', str(prefix / 'usr/share/qemu')]
    (output / 'command.json').write_text(json.dumps(command, indent=2))
    for boot in (1, 2):
        serial = output / f'boot-{boot}.log'
        with (output / f'qemu-{boot}.log').open('w') as log:
            subprocess.run(command + ['-serial', 'file:' + str(serial)], env=env,
                           check=True, stdout=log, stderr=subprocess.STDOUT, timeout=2100)
        if 'APX_VM_SMOKE_PASS' not in serial.read_text(errors='replace'):
            raise RuntimeError(f'guest smoke failed; inspect {serial}')
        print(f'Boot {boot}: installation/lifecycle checks passed', flush=True)
    print(f'Teste de VM passed twice; disposable files retained in {output}')

if __name__ == '__main__':
    main()
