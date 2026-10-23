#!/usr/bin/env python3
"""Host-owned, identity-pinned mount for the owner's removable Ventoy volume."""

from __future__ import annotations

import argparse
import fcntl
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


def trusted_device() -> Path | None:
    try:
        path = DEVICE.resolve(strict=True)
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
            properties.get("ID_FS_TYPE")) != ("usb", UUID, FILESYSTEM):
        raise RuntimeError("PEN filesystem or USB identity differs")
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
    VOLUME.mkdir(mode=0o755, exist_ok=True)
    if VOLUME.is_symlink() or VOLUME.stat().st_uid != 0:
        raise RuntimeError("removable media volume path is untrusted")
    if mounted_source(VOLUME) is None:
        VOLUME.chmod(0o755)


def refresh() -> None:
    LOCK.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    with LOCK.open("a") as descriptor:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        prepare_root()
        device = trusted_device()
        source = mounted_source(VOLUME)
        if source is not None:
            if device is not None and Path(source).exists() \
                    and Path(source).stat().st_rdev == device.stat().st_rdev:
                return
            # Never force a detach: an active copy must finish first.
            result = run("/usr/bin/umount", str(VOLUME), check=False)
            if result.returncode:
                raise RuntimeError("PEN is still in use; close open files before removing it")
        if device is None:
            return
        run("/usr/bin/mount", "--types", FILESYSTEM,
            "--options", "rw,nosuid,nodev,noexec,uid=0,gid=0,umask=000",
            str(device), str(VOLUME))


def watch() -> None:
    refresh()
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
