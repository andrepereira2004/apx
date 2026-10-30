#!/usr/bin/env python3
"""Bounded owner-requested Teste/QEMU lab; never exposes a physical disk to QEMU."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import secrets
import stat
import subprocess
import tempfile
import time

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "audit/2026-10-18-portable-rebuild/vm"
GENERATION = "6d3bf7be-dcf6-4040-a13e-9fda4c7c8100"
ENVIRONMENT = Path("/var/lib/apx/environments/teste")
MAINTENANCE_ROOT = ENVIRONMENT / "root"
HOME = ENVIRONMENT / "home/apx"
VM = HOME / "VMs/APX-Rebuild"
INNER = "/home/apx/VMs/APX-Rebuild"
LEASE = Path("/dev/apx-portable-rehearsal-teste")
MACHINE = "apx-lab-teste"
UNIT = "apx-portable-rehearsal-teste.service"
GUARD_ENTRYPOINT = Path(__file__).resolve()


def call(*args, check=True, **kwargs):
    result = subprocess.run(args, text=True, capture_output=True, check=False, **kwargs)
    if check and result.returncode:
        raise RuntimeError(f"{args[0]}: {(result.stderr or result.stdout)[-2000:]}")
    return result


def assert_test():
    if os.geteuid(): raise ValueError("Host root required")
    if Path("/proc/sys/kernel/hostname").read_text().strip() != "apx-host":
        raise ValueError("this lab harness is scoped to the current authorized pilot")
    path = ENVIRONMENT / "registration.json"
    record = json.loads(path.read_text())
    if path.is_symlink() or record.get("generation") != GENERATION \
            or (record.get("name"), record.get("role")) != ("teste", "graphical-base"):
        raise ValueError("Test Environment identity changed")
    return record


def inside(*args, check=True):
    return call("systemd-run", "-M", MACHINE, "--quiet", "--wait", "--pipe", "--collect", *args, check=check)


def prepare():
    assert_test()
    os.umask(0o022)
    if shutil.disk_usage("/").free < 100 * 1024**3:
        raise ValueError("insufficient starting budget above the unchanged Host reserve")
    if VM.exists() or LEASE.exists(): raise ValueError("refusing to overwrite an existing lab")
    OUT.mkdir(parents=True, exist_ok=True, mode=0o700)
    VM.mkdir(parents=True, mode=0o700)
    os.chown(VM.parent, 1000, 1000); os.chown(VM, 1000, 1000)
    def logged(log, *args):
        with (OUT / log).open("x") as stream:
            subprocess.run(args, stdout=stream, stderr=subprocess.STDOUT, check=True)
    # RAM staging avoids retaining a second guest disk/root on the physical SSD.
    with tempfile.TemporaryDirectory(prefix="apx-full-vm-", dir="/tmp") as stage:
        root = Path(stage) / "root"; root.mkdir()
        with tempfile.TemporaryDirectory(prefix="apx-vm-keys-", dir="/tmp") as keys:
            logged("keyring-init.log", "pacman-key", "--gpgdir", keys, "--init")
            logged("keyring-populate.log", "pacman-key", "--gpgdir", keys, "--populate", "archlinux")
            call("gpgconf", "--homedir", keys, "--kill", "gpg-agent")
            destination = root / "etc/pacman.d/gnupg"
            destination.parent.mkdir(parents=True)
            shutil.copytree(keys, destination)
        logged("pacstrap.log", "pacstrap", "-K", "-c", str(root), "base", "linux", "mkinitcpio", "btrfs-progs",
               "python", "nftables", "arch-install-scripts")
        spec = importlib.util.spec_from_file_location("portable_full", REPO / "scripts/portable/install_apx_full.py")
        installer = importlib.util.module_from_spec(spec); spec.loader.exec_module(installer)
        hashes = installer.verify_sources()
        for relative in installer.source_files():
            target = root / "root/apx" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / relative, target)
        (OUT / "source-manifest.json").write_text(json.dumps(hashes, indent=2) + "\n")
        def write(relative, value, mode=0o644):
            path = root / relative; path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value); path.chmod(mode)
        for filename in ("full-vm-agent.py", "full-vm-smoke.py"):
            shutil.copy2(REPO / "scripts/portable" / filename, root / "root" / filename)
        write("etc/apx-disposable-full-vm", "local-source-disposable-vm-fixture\n", 0o600)
        write("etc/hostname", "apx-portable-guest\n")
        write("etc/machine-id", "")
        write("etc/fstab", "/dev/vda / btrfs defaults,compress=zstd:3 0 0\n")
        write("etc/systemd/network/20-ethernet.network", "[Match]\nName=en* eth*\n[Network]\nDHCP=yes\n")
        resolver = root / "etc/resolv.conf"
        resolver.unlink(missing_ok=True); resolver.symlink_to("/run/systemd/resolve/stub-resolv.conf")
        write("etc/mkinitcpio-apx-vm.conf", "MODULES=(virtio_pci virtio_blk virtio_net virtio_gpu virtio_console virtio_input btrfs)\nBINARIES=()\nFILES=()\nHOOKS=(base systemd modconf block filesystems)\n")
        write("etc/systemd/system/apx-full-vm-agent.service", """[Unit]
Description=Disposable VM owner control fixture
After=systemd-udevd.service
ConditionVirtualization=vm
[Service]
ExecStart=/usr/bin/python /root/full-vm-agent.py
Restart=on-failure
[Install]
WantedBy=multi-user.target
""")
        write("etc/systemd/system/apx-full-vm-auth-fixture.service", """[Unit]
Description=Disposable VM root authentication fixture; never shipped by APX
Before=apx-portable-graphical.service
ConditionVirtualization=vm
[Service]
Type=oneshot
ExecStart=/usr/bin/bash -c 'install -d -m 0755 /run/apx; umask 077; echo disposable-vm-test > /run/apx/portable-vm-authenticated-fixture'
RemainAfterExit=yes
[Install]
WantedBy=multi-user.target
""")
        logged("enable.log", "systemctl", "--root", str(root), "enable", "systemd-networkd", "systemd-resolved",
               "apx-full-vm-agent", "apx-full-vm-auth-fixture")
        kernels = [p.name for p in (root / "usr/lib/modules").iterdir() if (p / "vmlinuz").is_file()]
        if len(kernels) != 1: raise ValueError("ambiguous guest kernel")
        logged("initramfs.log", "arch-chroot", str(root), "mkinitcpio", "-k", kernels[0],
               "-c", "/etc/mkinitcpio-apx-vm.conf", "-g", "/boot/initramfs-apx-vm.img")
        for source, target in ((root / "boot/vmlinuz-linux", VM / "vmlinuz"),
                               (root / "boot/initramfs-apx-vm.img", VM / "initramfs")):
            shutil.copy2(source, target); os.chown(target, 1000, 1000); target.chmod(0o400)
        disk = VM / "disk.raw"
        with disk.open("xb") as stream: stream.truncate(160 * 1024**3)
        # Runtime/outer Btrfs compression remains enabled. Do not use mkfs's
        # rootdir compressor: this Host tool produced guest-invalid zstd extents.
        logged("mkfs.log", "mkfs.btrfs", "--rootdir", str(root), "--label", "APX_FULL_REBUILD", str(disk))
        os.chown(disk, 1000, 1000); disk.chmod(0o600)
    attach()
    print("Fresh Arch disk prepared; QEMU remains inside Teste", flush=True)


def attach():
    assert_test()
    if not (VM / "disk.raw").is_file(): raise ValueError("prepared guest disk missing")
    LEASE.mkdir(mode=0o700)
    kvm = Path("/dev/kvm").stat()
    if not stat.S_ISCHR(kvm.st_mode): raise ValueError("KVM device missing")
    proxy = LEASE / "kvm"
    os.mknod(proxy, stat.S_IFCHR | 0o600, kvm.st_rdev)
    call("systemd-run", "--quiet", "--collect", "--unit=" + UNIT,
         "--property=Delegate=yes", "--property=KillMode=mixed", "--property=TimeoutStopSec=15s",
         "--property=MemoryMax=10G", "--property=TasksMax=4096", "--property=DevicePolicy=closed",
         "--property=DeviceAllow=/dev/kvm rw", "systemd-nspawn", "--quiet", "--keep-unit", "--boot",
         "--settings=no", "--register=yes", "--machine=" + MACHINE, "--directory=" + str(MAINTENANCE_ROOT),
         "--private-users=pick", "--private-users-ownership=chown", "--private-network", "--network-veth",
         "--link-journal=no", "--console=pipe", "--bind=" + str(ENVIRONMENT / "home") + ":/home:idmap",
         "--bind=" + str(proxy) + ":/dev/kvm")
    for _ in range(200):
        result = call("machinectl", "show", MACHINE, "--property=Leader", "--value", check=False)
        if result.returncode == 0 and result.stdout.strip().isdecimal():
            fields = Path("/proc/" + result.stdout.strip() + "/uid_map").read_text().split()
            if len(fields) != 3 or fields[0] != "0" or fields[2] != "65536":
                raise ValueError("unexpected Teste user namespace")
            uid = int(fields[1]) + 1000
            os.chown(proxy, uid, uid); os.chmod(proxy, 0o660)
            break
        time.sleep(.1)
    else: raise RuntimeError("Teste maintenance container did not register")
    for _ in range(200):
        if inside("/usr/bin/true", check=False).returncode == 0: break
        time.sleep(.1)
    (OUT / "lab.json").write_text(json.dumps({"generation": GENERATION, "machine": MACHINE, "unit": UNIT,
                                              "vm": str(VM), "free_bytes": shutil.disk_usage("/").free}, indent=2) + "\n")
    if call("systemctl", "is-active", "--quiet", "apx-portable-rehearsal-budget.service", check=False).returncode:
        call("systemd-run", "--quiet", "--collect", "--unit=apx-portable-rehearsal-budget.service",
             "--property=MemoryMax=128M", "/usr/bin/python", str(GUARD_ENTRYPOINT), "guard")
    print("Bounded Teste KVM proxy and maintenance container ready", flush=True)


def start(chipset):
    assert_test()
    for filename in ("qmp.sock", "agent.sock"):
        (VM / filename).unlink(missing_ok=True)
    boot = "q35" if chipset == "q35" else "pc"
    command = ["/usr/bin/qemu-system-x86_64", "-name", "APX Full Rebuild Teste", "-machine", boot + ",accel=kvm",
               "-cpu", "host", "-m", "6144", "-smp", "4", "-nodefaults", "-no-reboot", "-display", "none",
               "-kernel", INNER + "/vmlinuz", "-initrd", INNER + "/initramfs",
               "-append", "root=/dev/vda rw console=ttyS0 loglevel=4",
               "-drive", "if=none,id=disk,format=raw,discard=unmap,detect-zeroes=unmap,file=" + INNER + "/disk.raw",
               "-device", "virtio-blk-pci,drive=disk", "-device", "virtio-vga",
               "-netdev", "user,id=n0", "-device", "virtio-net-pci,netdev=n0",
               "-device", "virtio-serial-pci", "-chardev", "socket,id=lab,path=" + INNER + "/agent.sock,server=on,wait=off",
               "-device", "virtserialport,chardev=lab,name=apx.lab",
               "-qmp", "unix:" + INNER + "/qmp.sock,server=on,wait=off", "-serial", "file:" + INNER + "/serial-" + chipset + ".log"]
    (OUT / ("qemu-" + chipset + ".json")).write_text(json.dumps(command, indent=2) + "\n")
    result = call("systemd-run", "-M", MACHINE, "--quiet", "--unit=apx-full-rebuild-vm", "--collect",
                  "--property=User=apx", "--property=Group=apx",
                  "--property=MemoryMax=8G", "--property=KillMode=mixed", *command)
    print(result.stdout, result.stderr)


def guard():
    assert_test()
    while call("systemctl", "is-active", "--quiet", UNIT, check=False).returncode == 0:
        free = shutil.disk_usage("/").free
        if free < 97 * 1024**3:
            (OUT / "storage-guard.json").write_text(json.dumps({"stopped_test": True, "free_bytes": free}) + "\n")
            call("systemctl", "stop", UNIT, check=False)
            return
        time.sleep(2)


def guest(args, timeout=60):
    assert_test()
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(timeout + 10)
        connection.connect(str(VM / "agent.sock"))
        request_id = secrets.token_hex(8)
        connection.sendall((json.dumps({"args": args, "timeout": timeout, "request_id": request_id}) + "\n").encode())
        data = bytearray()
        while len(data) < 1000000:
            while b'\n' in data:
                line, _, rest = data.partition(b'\n'); data = bytearray(rest)
                response = json.loads(line)
                if response.get('request_id') == request_id:
                    return response
            block = connection.recv(16384)
            if not block: break
            data += block
    raise RuntimeError('guest fixture closed without a matching response')


def cleanup():
    record = assert_test()
    original = json.loads((REPO / 'audit/2026-10-18-storage-cleanup/after.json').read_text())
    def signatures():
        return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in original['registrations']}
    before = signatures()
    call("systemctl", "stop", "apx-portable-rehearsal-budget.service", check=False)
    call("systemctl", "stop", UNIT, check=False)
    for _ in range(100):
        if call("machinectl", "show", MACHINE, check=False).returncode: break
        time.sleep(.1)
    else: raise RuntimeError("Teste maintenance container still exists")
    if LEASE.exists():
        (LEASE / "kvm").unlink(missing_ok=True); LEASE.rmdir()
    # Preserve console evidence, never raw disks, account data or keyrings.
    for log in VM.glob("serial-*.log"):
        shutil.copy2(log, OUT / log.name)
    plan = json.loads(call("apx", "environment", "destroy-plan", "teste").stdout)
    if plan["generation"] != GENERATION: raise ValueError("destroy generation changed")
    (OUT / "destroy-plan.json").write_text(json.dumps(plan, indent=2) + "\n")
    result = call("apx", "environment", "destroy", "--plan", plan["digest"], "--approve", "DESTROY teste")
    (OUT / "destroy.log").write_text(result.stdout + result.stderr)
    call("btrfs", "subvolume", "sync", "/var/lib/apx")
    (OUT / "cleanup.json").write_text(json.dumps({"generation": GENERATION,
        "environment_absent": not ENVIRONMENT.exists(), "lease_absent": not LEASE.exists(),
        "maintenance_machine_absent": call("machinectl", "show", MACHINE, check=False).returncode != 0,
        "free_bytes": shutil.disk_usage("/").free,
        "other_registrations_before": before, "other_registrations_after": signatures(),
        "other_registrations_unchanged_during_cleanup": before == signatures(),
        "partition_table_unchanged": hashlib.sha256(call('sfdisk', '--json', '/dev/nvme0n1').stdout.strip().encode()).hexdigest() == original['partition_table_sha256'],
        "btrfs_device_stats": call('btrfs', 'device', 'stats', '/').stdout,
        "failed_units": call('systemctl', '--failed', '--no-legend', '--no-pager').stdout}, indent=2) + "\n")
    print("Teste, its VM and KVM proxy removed; evidence retained")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "attach", "start", "command", "cleanup", "guard"))
    parser.add_argument("--chipset", choices=("q35", "pc"), default="q35")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("command", nargs="*")
    args = parser.parse_args()
    if args.action == "prepare": prepare()
    elif args.action == "attach": attach()
    elif args.action == "start": start(args.chipset)
    elif args.action == "cleanup": cleanup()
    elif args.action == "guard": guard()
    else: print(json.dumps(guest(args.command, args.timeout), indent=2))
