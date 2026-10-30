#!/usr/bin/env python3
"""Install Arch + stage APX on an explicitly selected EMPTY disk from Arch live USB."""
from __future__ import annotations
import argparse
import getpass
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.request
import tarfile

REPO = Path(__file__).resolve().parents[2]
MIN_BYTES = 160 * 1024**3
CODEX_URL = ('https://github.com/openai/codex/releases/download/rust-v0.166.0/'
             'codex-x86_64-unknown-linux-musl.tar.gz')
CODEX_SHA256 = 'a0bf572d2f93f056c6712a6da348e96078dc84f3885fd7be67807ef389cb3978'
RECOVERY_PACKAGES = ('base', 'linux', 'mkinitcpio', 'networkmanager', 'cryptsetup',
                     'btrfs-progs', 'ntfs-3g', 'systemd-ukify')


def run(*args, capture=False, input=None):
    result = subprocess.run(args, check=True, text=True, input=input,
                            stdout=subprocess.PIPE if capture else None,
                            env={**os.environ, 'LC_ALL': 'C'})
    return (result.stdout or '').strip()


def installer():
    spec = importlib.util.spec_from_file_location('apx_full', Path(__file__).with_name('install_apx_full.py'))
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


def validate_disk(record, signatures, swap_devices):
    if record.get('type') != 'disk' or record.get('ro') or int(record.get('size', 0)) < MIN_BYTES:
        raise ValueError('select a writable whole disk of at least 160 GiB')
    if record.get('children') or record.get('fstype') or record.get('pttype') or signatures:
        raise ValueError('disk is not empty: partitions or filesystem/partition signatures found')
    if any(record.get('mountpoints') or []) or record.get('path') in swap_devices:
        raise ValueError('disk is mounted or used as swap')


def disk_identity(disk):
    path = Path(disk)
    if not re.fullmatch(r'/dev/(?:sd[a-z]+|vd[a-z]+|nvme[0-9]+n[0-9]+|mmcblk[0-9]+)', disk):
        raise ValueError('use a direct whole-disk device path; aliases/loop/mapper devices refused')
    info = path.lstat()
    if not stat.S_ISBLK(info.st_mode): raise ValueError('target is not a block device')
    data = json.loads(run('lsblk', '--json', '--tree', '--bytes', '--paths', '--output',
                          'PATH,TYPE,SIZE,RO,FSTYPE,PTTYPE,MOUNTPOINTS,MODEL,SERIAL,WWN,MAJ:MIN', disk, capture=True))
    records = data['blockdevices']
    if len(records) != 1: raise ValueError('ambiguous disk identity')
    record = records[0]
    signatures = json.loads(run('wipefs', '--json', '--no-act', disk, capture=True))['signatures']
    swap = run('swapon', '--noheadings', '--raw', '--show=NAME', capture=True).splitlines()
    validate_disk(record, signatures, swap)
    sysdev = Path('/sys/dev/block') / f'{os.major(info.st_rdev)}:{os.minor(info.st_rdev)}'
    if list((sysdev / 'holders').iterdir()): raise ValueError('disk has active holders')
    if record.get('maj:min') != f'{os.major(info.st_rdev)}:{os.minor(info.st_rdev)}':
        raise ValueError('device identity changed')
    return record


def pci_graphics(sys_pci=Path('/sys/bus/pci/devices')):
    devices = []
    for path in sorted(sys_pci.iterdir()):
        if (path / 'class').read_text().strip().startswith('0x03'):
            devices.append({'address': path.name, 'vendor': (path/'vendor').read_text().strip(),
                            'device': (path/'device').read_text().strip()})
    if not devices: raise ValueError('no PCI graphics device found; ARM/headless installation is unsupported')
    return devices


def graphics_packages(devices, nvidia_supported=()):
    packages = {'mesa', 'vulkan-swrast'}
    for gpu in devices:
        vendor = gpu['vendor']
        if vendor == '0x8086': packages.add('vulkan-intel')
        elif vendor == '0x1002': packages.add('vulkan-radeon')
        elif vendor == '0x10de':
            if gpu['device'][2:].upper() not in nvidia_supported:
                raise ValueError('NVIDIA PCI ID absent from the current official driver support list; no disk changes')
            packages.update(('nvidia-open', 'nvidia-utils', 'egl-wayland'))
        elif vendor not in {'0x1af4', '0x1234', '0x15ad', '0x80ee'}:
            raise ValueError('unsupported GPU vendor: ' + vendor)
    return sorted(packages)


def hardware_plan():
    devices = pci_graphics()
    supported = set()
    version = None
    if any(g['vendor'] == '0x10de' for g in devices):
        resolved = run('pacman', '-Sp', '--print-format', '%n %v', 'nvidia-utils', capture=True)
        version = next(line.split()[1] for line in resolved.splitlines() if line.startswith('nvidia-utils '))
        upstream = version.split(':')[-1].rsplit('-', 1)[0]
        if not re.fullmatch(r'[0-9.]+', upstream): raise ValueError('unexpected NVIDIA package version')
        url = f'https://download.nvidia.com/XFree86/Linux-x86_64/{upstream}/README/supportedchips.html'
        with urllib.request.urlopen(url, timeout=30) as response: text = response.read(4_000_000).decode()
        supported = set(re.findall(r'<tr\s+id="devid([0-9A-Fa-f]{4})(?:_[0-9A-Fa-f_]+)?"', text))
        supported = {v.upper() for v in supported}
        if not supported: raise ValueError('cannot validate NVIDIA supported-products list')
    cpu = Path('/proc/cpuinfo').read_text()
    microcode = ['intel-ucode'] if 'GenuineIntel' in cpu else ['amd-ucode'] if 'AuthenticAMD' in cpu else []
    return {'graphics': devices, 'graphics_packages': graphics_packages(devices, supported),
            'nvidia_version': version, 'microcode_packages': microcode}


def live_session():
    if os.geteuid() or os.uname().machine != 'x86_64': raise ValueError('Arch x86_64 live root required')
    if not Path('/run/archiso').is_dir(): raise ValueError('boot the Arch installation USB first')
    if subprocess.run(['systemd-detect-virt', '--container', '--quiet']).returncode == 0:
        raise ValueError('containers/chroots are not installation targets')


def preflight(disk):
    live_session()
    for tool in ('pacstrap', 'arch-chroot', 'sfdisk', 'wipefs', 'mkfs.btrfs', 'mkfs.fat', 'mkfs.ext4', 'mount',
                 'umount', 'udevadm', 'lsblk', 'swapon', 'genfstab', 'blkid', 'chpasswd', 'loadkeys', 'efibootmgr', 'gpgconf'):
        if not shutil.which(tool): raise ValueError('missing Arch live tool: ' + tool)
    record = disk_identity(disk)
    hashes = installer().verify_sources()
    hardware = hardware_plan()
    uefi = Path('/sys/firmware/efi').is_dir()
    if not uefi: raise ValueError('APX Recovery requires UEFI firmware boot options')
    if uefi:
        for variable in Path('/sys/firmware/efi/efivars').glob('SecureBoot-*'):
            if variable.read_bytes()[4:5] == b'\x01': raise ValueError('disable Secure Boot for this unsigned experimental installer')
    packages = ['base', 'linux', 'linux-firmware', 'mkinitcpio', 'btrfs-progs', 'python',
                'arch-install-scripts', 'nftables', 'grub', 'efibootmgr', 'dosfstools',
                'networkmanager', 'iwd', 'curl', *hardware['microcode_packages'], *hardware['graphics_packages']]
    # Check resolvability against the live medium's package databases before formatting.
    run('pacman', '-Sp', '--print-format', '%n %v', *packages, *RECOVERY_PACKAGES, capture=True)
    plan = {'schema': 1, 'disk': record, 'boot_mode': 'uefi' if uefi else 'bios',
            'hardware': hardware, 'packages': packages, 'source_sha256': hashes,
            'layout': 'GPT + 1GiB ESP + 2GiB APX Recovery + Btrfs @'}
    digest = hashlib.sha256(json.dumps(plan, sort_keys=True).encode()).hexdigest()
    plan['confirmation'] = f'INSTALL APX ON {disk} {digest[:12]}'
    return plan


def partition_script(uefi):
    return ('label: gpt\nunit: sectors\n\n' +
            ('size=1GiB, type=U\n' if uefi else 'size=2MiB, type=21686148-6449-6E6F-744E-656564454649\n') +
            'size=2GiB, type=L, name="APX_RECOVERY"\n'
            'type=L\n')


def download_codex(directory):
    archive = directory / 'codex.tar.gz'
    digest = hashlib.sha256()
    with urllib.request.urlopen(CODEX_URL, timeout=60) as response, archive.open('wb') as output:
        while chunk := response.read(1024 * 1024):
            digest.update(chunk); output.write(chunk)
    if digest.hexdigest() != CODEX_SHA256:
        raise ValueError('Codex release checksum mismatch; disk untouched')
    with tarfile.open(archive, 'r:gz') as package:
        members = [m for m in package.getmembers() if m.isfile() and
                   Path(m.name).name == 'codex-x86_64-unknown-linux-musl']
        if len(members) != 1: raise ValueError('Codex release layout changed; disk untouched')
        binary = directory / 'codex'
        with package.extractfile(members[0]) as source, binary.open('wb') as target:
            shutil.copyfileobj(source, target)
        binary.chmod(0o755)
    version = subprocess.run([str(binary), '--version'], capture_output=True, text=True, check=True)
    if version.stdout.strip() != 'codex-cli 0.166.0':
        raise ValueError('Codex release version mismatch; disk untouched')
    return binary


def partition_path(disk, number):
    return disk + ('p' if disk[-1].isdigit() else '') + str(number)


def write(root, name, text, mode=0o644):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text); path.chmod(mode)


def install_recovery(esp, partition, codex_binary):
    run('mkfs.ext4', '-F', '-L', 'APX_RECOVERY', partition)
    recovery = Path(tempfile.mkdtemp(prefix='apx-recovery-', dir='/mnt'))
    try:
        run('mount', partition, str(recovery))
        try:
            run('pacstrap', '-K', str(recovery), *RECOVERY_PACKAGES)
            destination = recovery / 'usr/local/bin/codex'
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(codex_binary, destination); destination.chmod(0o755)
            uuid = run('blkid', '-s', 'UUID', '-o', 'value', partition, capture=True)
            write(recovery, 'etc/fstab', f'UUID={uuid} / ext4 rw,relatime 0 1\n')
            write(recovery, 'etc/hostname', 'apx-recovery\n')
            write(recovery, 'etc/systemd/system/getty@tty1.service.d/autologin.conf',
                  '[Service]\nExecStart=\nExecStart=-/usr/bin/agetty --autologin root --noclear %I $TERM\n')
            write(recovery, 'root/RECOVERY.txt',
                  'APX Recovery: connect with nmcli, then run codex login --device-auth '
                  'on first use. Run codex to start. Unlock the APX disk with cryptsetup.\n', 0o600)
            run('systemctl', '--root', str(recovery), 'enable', 'NetworkManager', 'getty@tty1.service')
            run('arch-chroot', str(recovery), 'mkinitcpio', '-P')
            run('arch-chroot', str(recovery), 'ukify', 'build', '--linux=/boot/vmlinuz-linux',
                '--initrd=/boot/initramfs-linux.img', '--os-release=@/etc/os-release',
                f'--cmdline=root=UUID={uuid} rw systemd.unit=multi-user.target',
                '--output=/boot/APX-Recovery.efi')
            efi = esp / 'EFI/Recovery/APX-Recovery.efi'
            efi.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(recovery / 'boot/APX-Recovery.efi', efi)
            # Keep the 2 GiB root useful for repairs instead of retaining install archives.
            for path in (recovery / 'var/cache/pacman/pkg').glob('*.pkg.tar.zst*'):
                if path.is_file(): path.unlink()
            if shutil.disk_usage(recovery).free < 400 * 1024**2:
                raise ValueError('APX Recovery has insufficient free space after installation')
        finally:
            subprocess.run(['gpgconf', '--homedir', str(recovery/'etc/pacman.d/gnupg'),
                            '--kill', 'gpg-agent'], check=False)
            run('umount', str(recovery))
    finally:
        recovery.rmdir()


def register_firmware_entries(disk):
    def create(label, path):
        before = set(re.findall(r'^Boot([0-9A-Fa-f]{4})\*', run('efibootmgr', capture=True), re.M))
        run('efibootmgr', '-c', '-d', disk, '-p', '1', '-L', label, '-l', path)
        after = set(re.findall(r'^Boot([0-9A-Fa-f]{4})\*', run('efibootmgr', capture=True), re.M))
        created = after - before
        if len(created) != 1: raise ValueError('firmware did not expose the new ' + label + ' entry')
        return created.pop()
    apx = create('APX', r'\EFI\BOOT\BOOTX64.EFI')
    recovery = create('APX Recovery', r'\EFI\Recovery\APX-Recovery.efi')
    order = re.search(r'^BootOrder: (.+)$', run('efibootmgr', capture=True), re.M)
    if not order: raise ValueError('firmware boot order unavailable')
    entries = [item for item in order.group(1).split(',') if item not in (apx, recovery)]
    run('efibootmgr', '-o', ','.join([apx, *entries, recovery]))


def apply(plan):
    disk = plan['disk']['path']
    if disk_identity(disk) != plan['disk']: raise ValueError('disk identity changed since planning')
    phrase = input('Type exactly: ' + plan['confirmation'] + '\n> ')
    if phrase != plan['confirmation']: raise ValueError('confirmation does not match; disk untouched')
    print('Switching console keyboard to Portuguese (pt-latin1), matching the APX graphical default.', flush=True)
    run('loadkeys', 'pt-latin1')
    password = getpass.getpass('New recovery root password (12+ characters): ')
    if len(password) < 12 or len(password) > 255 or any(c in password for c in '\r\n'):
        raise ValueError('invalid recovery password; disk untouched')
    if password != getpass.getpass('Repeat recovery root password: '): raise ValueError('password mismatch; disk untouched')
    # Download and verify the recovery CLI before touching the disk.
    download_dir = Path(tempfile.mkdtemp(prefix='apx-codex-'))
    try:
        codex_binary = download_codex(download_dir)
        _apply_verified(plan, password, codex_binary)
    finally:
        for path in download_dir.iterdir(): path.unlink()
        download_dir.rmdir()


def _apply_verified(plan, password, codex_binary):
    disk = plan['disk']['path']
    # Recheck immediately before the first destructive operation.
    if disk_identity(disk) != plan['disk']: raise ValueError('disk changed; disk untouched')
    # Root may have a private umask; the installed system root must be traversable.
    os.umask(0o022)
    uefi = plan['boot_mode'] == 'uefi'
    first, recovery_partition, system = (partition_path(disk, n) for n in (1, 2, 3))
    run('sfdisk', '--lock', disk, input=partition_script(uefi))
    run('udevadm', 'settle')
    run('mkfs.btrfs', '--label', 'APX', system)
    if uefi: run('mkfs.fat', '-F', '32', '-n', 'APX_BOOT', first)
    # Do not use TemporaryDirectory: recursive cleanup must NEVER traverse a
    # target filesystem if an unmount fails.
    root = Path(tempfile.mkdtemp(prefix='apx-install-', dir='/mnt'))
    try:
        try:
            run('mount', system, str(root))
            run('btrfs', 'subvolume', 'create', str(root/'@'))
            run('umount', str(root))
            run('mount', '-o', 'subvol=@,compress=zstd:3', system, str(root))
            if uefi:
                (root/'boot').mkdir(); run('mount', first, str(root/'boot'))
            run('pacstrap', '-K', str(root), *plan['packages'])
            write(root, 'etc/fstab', run('genfstab', '-U', str(root), capture=True) + '\n')
            write(root, 'etc/hostname', 'apx\n')
            write(root, 'etc/locale.conf', 'LANG=C.UTF-8\n')
            write(root, 'etc/vconsole.conf', 'KEYMAP=pt-latin1\n')
            write(root, 'etc/NetworkManager/conf.d/apx-wifi.conf', '[device]\nwifi.backend=iwd\n')
            if 'nvidia-open' in plan['hardware']['graphics_packages']:
                write(root, 'etc/modprobe.d/apx-nvidia.conf', 'options nvidia_drm modeset=1\n')
            run('arch-chroot', str(root), 'chpasswd', input='root:' + password + '\n')
            password = None
            run('arch-chroot', str(root), 'mkinitcpio', '-P')
            if uefi:
                run('arch-chroot', str(root), 'grub-install', '--target=x86_64-efi', '--efi-directory=/boot',
                    '--bootloader-id=APX', '--removable', '--no-nvram')
            else: run('arch-chroot', str(root), 'grub-install', '--target=i386-pc', disk)
            run('arch-chroot', str(root), 'grub-mkconfig', '-o', '/boot/grub/grub.cfg')
            install_recovery(root/'boot', recovery_partition, codex_binary)
            full = installer()
            for relative in full.source_files():
                dest = root/'opt/apx-installer'/relative
                dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(REPO/relative, dest)
            write(root, 'etc/apx-empty-disk-install.json', json.dumps(plan, indent=2)+'\n', 0o600)
            write(root, 'etc/systemd/system/apx-first-boot.service', '''[Unit]
Description=Finish experimental APX installation on first boot
Wants=NetworkManager-wait-online.service
After=NetworkManager-wait-online.service systemd-user-sessions.service
Conflicts=getty@tty1.service
ConditionPathExists=!/var/lib/apx-first-boot-complete

[Service]
Type=oneshot
ExecStart=/usr/bin/bash /opt/apx-installer/scripts/portable/finish-apx-first-boot.sh
StandardInput=tty-force
StandardOutput=tty
StandardError=tty
TTYPath=/dev/tty1
TTYReset=yes
TTYVHangup=yes
TimeoutStartSec=infinity

[Install]
WantedBy=multi-user.target
''')
            run('systemctl', '--root', str(root), 'mask', 'getty@tty1.service')
            run('systemctl', '--root', str(root), 'enable', 'NetworkManager.service', 'apx-first-boot.service')
        finally:
            # Never unmount anything outside our fresh, private target mount tree.
            if subprocess.run(['mountpoint', '--quiet', str(root)]).returncode == 0:
                run('umount', '--recursive', str(root))
    finally:
        root.rmdir()
    register_firmware_entries(disk)
    print('Arch installed. Shut down, remove the USB, and boot this disk.\n'
          'APX installation continues on VT1 and asks for your new APX password.\n'
          'Recovery login: root on VT3, using the recovery password chosen above.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list-disks', action='store_true')
    parser.add_argument('--disk')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        if args.list_disks:
            run('lsblk', '--paths', '--output', 'PATH,TYPE,SIZE,FSTYPE,MOUNTPOINTS,MODEL'); return 0
        if not args.disk: parser.error('--disk is required')
        if args.apply:
            live_session()
            disk_identity(args.disk)
            # This is the disposable live medium, never a partial installed-system upgrade.
            run('pacman', '-Sy', '--noconfirm')
        plan = preflight(args.disk)
        print(json.dumps(plan, indent=2), flush=True)
        if args.apply: apply(plan)
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print('APX disk installation refused/failed: ' + str(error), file=sys.stderr); return 2


if __name__ == '__main__': raise SystemExit(main())
