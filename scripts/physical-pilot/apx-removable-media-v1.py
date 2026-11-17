#!/usr/bin/env python3
"""Host-owned, identity-pinned file bridge for the owner-approved removable volumes."""

from __future__ import annotations

import argparse
import fcntl
import json
import socket
import struct
import threading
import os
from pathlib import Path
import select
import stat
import subprocess
import time


UUID = "4E21-0000"
DEVICE = Path("/dev/disk/by-uuid") / UUID
ROOT = Path("/run/apx/removable-media-v1")
VOLUME = ROOT / "Ventoy"
LOCK = Path("/run/apx/removable-media-v1.lock")
FILESYSTEM = "exfat"
# Fixed admission list for this disposable physical pilot. No raw block device
# is passed to an Environment. New media require an explicit admission here.
APPROVED_VOLUMES = (
    (UUID, FILESYSTEM, "Ventoy", None),
    ("4079-3F8D", "vfat", "USB-4079-3F8D", "77EA21C2"),
)


def run(*arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(arguments, check=check, text=True, capture_output=True)


def mounted_source(target: Path) -> str | None:
    # findmnt can also list covered mounts left at the same textual path by
    # propagation. Only a mount reachable through this namespace is current.
    if not os.path.ismount(target):
        return None
    result = run("/usr/bin/findmnt", "--kernel", "--mountpoint", str(target),
                 "--noheadings", "--output", "SOURCE", check=False)
    if result.returncode:
        return None
    sources = set(result.stdout.splitlines())
    if len(sources) != 1:
        raise RuntimeError("removable media mount source is ambiguous")
    return sources.pop()


def trusted_device(uuid: str = UUID, filesystem: str = FILESYSTEM,
                   serial: str | None = None) -> Path | None:
    try:
        path = (Path("/dev/disk/by-uuid") / uuid).resolve(strict=True)
        metadata = path.stat()
    except FileNotFoundError:
        return None
    if not str(path).startswith("/dev/") or not stat.S_ISBLK(metadata.st_mode):
        raise RuntimeError("PEN device identity is not a block device")
    properties = {}
    for line in run("/usr/bin/udevadm", "info", "--query=property", "--name", str(path)).stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            properties[key] = value
    if (properties.get("ID_BUS"), properties.get("ID_FS_UUID"),
            properties.get("ID_FS_TYPE")) != ("usb", uuid, filesystem):
        raise RuntimeError("PEN filesystem or USB identity differs")
    if serial is not None and properties.get("ID_SERIAL_SHORT") != serial:
        raise RuntimeError("PEN USB serial identity differs")
    partition = Path("/sys/class/block") / path.name
    if not (partition / "partition").is_file():
        raise RuntimeError("PEN is not a partition")
    parent = partition.resolve().parent
    if (parent / "removable").read_text().strip() != "1":
        raise RuntimeError("PEN parent disk is not removable")
    return path


def prepare_root() -> None:
    ROOT.mkdir(mode=0o755, parents=True, exist_ok=True)
    if ROOT.is_symlink() or ROOT.stat().st_uid != 0:
        raise RuntimeError("removable media root is untrusted")
    ROOT.chmod(0o755)
    # /run/apx is already a Host-shared mount. Binding this directory in
    # nspawn makes a downstream shared/slave peer without self-binding ROOT.
    parent = run("/usr/bin/findmnt", "--target", str(ROOT.parent),
                 "--noheadings", "--output", "PROPAGATION").stdout.strip()
    if "shared" not in parent:
        raise RuntimeError("APX runtime mount does not propagate to Environments")
    for _, _, name, _ in APPROVED_VOLUMES:
        volume = ROOT / name
        volume.mkdir(mode=0o755, exist_ok=True)
        if volume.is_symlink() or volume.stat().st_uid != 0:
            raise RuntimeError("removable media volume path is untrusted")
        if mounted_source(volume) is None:
            volume.chmod(0o755)


def refresh() -> None:
    LOCK.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    with LOCK.open("a") as descriptor:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        prepare_root()
        for uuid, filesystem, name, serial in APPROVED_VOLUMES:
            refresh_volume(uuid, filesystem, ROOT / name, serial)


def suppression_path(uuid: str) -> Path:
    return ROOT / (".ejected-" + uuid)


def device_generation(device: Path) -> str:
    return ((Path("/sys/class/block") / device.name).resolve().parent / "diskseq").read_text().strip()


def unmount_volume(uuid: str) -> None:
    admitted = next((v for v in APPROVED_VOLUMES if v[0] == uuid), None)
    if admitted is None:
        raise ValueError("Dispositivo não autorizado")
    with LOCK.open("a") as descriptor:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        _, filesystem, name, serial = admitted
        device = trusted_device(uuid, filesystem, serial)
        if device is None:
            raise RuntimeError("O dispositivo já não está ligado")
        volume = ROOT / name
        source = mounted_source(volume)
        generation = device_generation(device)
        if source is not None:
            if Path(source).stat().st_rdev != device.stat().st_rdev:
                raise RuntimeError("A identidade do dispositivo mudou")
            result = run("/usr/bin/umount", str(volume), check=False)
            if result.returncode:
                raise RuntimeError("O dispositivo está em utilização. Feche os ficheiros e tente novamente.")
        # Suppress automatic re-mount until this physical connection ends.
        # The marker is also read-only notification metadata for Environments.
        marker = suppression_path(uuid)
        marker.write_text(generation + "\n")
        marker.chmod(0o644)


def serve_control() -> None:
    endpoint = ROOT / "control.sock"
    if endpoint.exists():
        metadata = endpoint.lstat()
        if not stat.S_ISSOCK(metadata.st_mode) or metadata.st_uid != 0:
            raise RuntimeError("untrusted removable control endpoint")
        endpoint.unlink()
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
        server.bind(str(endpoint));endpoint.chmod(0o600);server.listen(4)
        while True:
            connection, _ = server.accept()
            with connection:
                connection.settimeout(3)
                try:
                    _, uid, _ = struct.unpack("3i", connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
                    if uid != 0: raise ValueError("Host authentication required")
                    data = bytearray()
                    while b"\n" not in data and len(data) <= 1024:
                        chunk = connection.recv(1025 - len(data))
                        if not chunk: break
                        data.extend(chunk)
                    request = json.loads(data)
                    if type(request) is not dict or set(request) != {"operation", "uuid"} or request["operation"] != "unmount":
                        raise ValueError("unsupported removable request")
                    unmount_volume(request["uuid"])
                    response = {"ok": True}
                except Exception as error:
                    response = {"ok": False, "error": str(error)[:256]}
                try: connection.sendall((json.dumps(response) + "\n").encode())
                except OSError: pass


def refresh_volume(uuid: str, filesystem: str, volume: Path,
                   serial: str | None = None) -> None:
    device = trusted_device(uuid, filesystem, serial)
    source = mounted_source(volume)
    if source is not None:
        if device is not None and Path(source).exists() \
                and Path(source).stat().st_rdev == device.stat().st_rdev:
            return
        # Never force a detach: an active copy must finish first.
        result = run("/usr/bin/umount", str(volume), check=False)
        if result.returncode:
            raise RuntimeError("PEN is still in use; close open files before removing it")
    marker = suppression_path(uuid)
    if device is None:
        marker.unlink(missing_ok=True)
        return
    if marker.exists():
        if marker.read_text().strip() == device_generation(device):
            return
        marker.unlink()
    run("/usr/bin/mount", "--types", filesystem,
        "--options", "rw,nosuid,nodev,noexec,uid=0,gid=0,umask=000",
        str(device), str(volume))


def watch() -> None:
    refresh()
    threading.Thread(target=serve_control, daemon=True).start()
    while True:
        with subprocess.Popen(("/usr/bin/udevadm", "monitor", "--udev",
                               "--subsystem-match=block", "--property"),
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                              text=True, bufsize=1) as process:
            assert process.stdout is not None
            while process.poll() is None:
                ready, _, _ = select.select((process.stdout,), (), (), 10)
                line = process.stdout.readline() if ready else ""
                if ready and not line:
                    break
                if ready and not line.startswith("UDEV"):
                    continue
                try:
                    refresh()
                except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
                    print(f"APX removable media: {error}", flush=True)
            process.wait()
        time.sleep(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("prepare", "watch"))
    arguments = parser.parse_args()
    if os.geteuid() != 0 or Path("/etc/hostname").read_text().strip() != "apx-host":
        raise RuntimeError("only the APX physical Host may manage removable media")
    if arguments.operation == "prepare":
        refresh()
    else:
        watch()


if __name__ == "__main__":
    main()
