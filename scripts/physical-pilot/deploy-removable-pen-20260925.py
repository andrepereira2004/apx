#!/usr/bin/env python3
"""Install or roll back the bounded Ventoy file bridge on the physical pilot."""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import time


REPO = Path(__file__).resolve().parents[2]
BASE = Path("/var/lib/apx/environments")
BACKUPS = Path("/var/lib/apx/backups")
NAMES = ("faculdade", "hytale", "minecraft", "steam")
BOOKMARK = "file:///media/apx-usb PEN USB\n"
OLD_LAUNCHER = "8ab255f04424b648d600aaa96a65eb88450e295bddf9b33a6e85f78c40f3cdf5"
OLD_BOOKMARK = "04319388475f0674511ab87d2ea11e52c6407414bd975daa9cf4254ff9c207a2"
OLD_DIGEST = f'"gtk-3.0/bookmarks": "{OLD_BOOKMARK}"'
NEW_DIGEST = '"gtk-3.0/bookmarks": "3937f6621d3b55203dfe464ade24fe9a14df3cab1f4ae2cfa631d6cbbd26b3b3"'
SERVICE = "apx-removable-media-v1.service"


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=check, text=True, capture_output=True)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def host_volume_mounted() -> bool:
    result = run("/usr/bin/nsenter", "--target", "1", "--mount", "--",
                 "/usr/bin/python3", "-c",
                 "import os; print(int(os.path.ismount('/run/apx/removable-media-v1/Ventoy')))")
    return result.stdout.strip() == "1"


def identity() -> None:
    if (Path("/etc/hostname").read_text().strip(),
            Path("/sys/class/dmi/id/product_name").read_text().strip(),
            Path("/sys/class/dmi/id/board_name").read_text().strip()) != (
            "apx-host", "82JU", "LNVNB161216"):
        raise RuntimeError("physical Host identity differs")
    if "profile=apx-physical-headless-pilot-v1" not in Path("/etc/apx-physical-pilot").read_text().splitlines():
        raise RuntimeError("physical pilot marker differs")


def source(path: str) -> bytes:
    return (REPO / path).read_bytes()


def save_and_write(target: Path, data: bytes, backup: Path, entries: list[dict[str, object]],
                   *, mode: int = 0o644, owner: tuple[int, int] = (0, 0)) -> None:
    if target.is_symlink():
        raise RuntimeError(f"refusing symlink: {target}")
    existed = target.exists()
    metadata = target.stat() if existed else None
    entry: dict[str, object] = {
        "target": str(target), "existed": existed,
        "uid": metadata.st_uid if metadata else owner[0],
        "gid": metadata.st_gid if metadata else owner[1],
        "mode": stat.S_IMODE(metadata.st_mode) if metadata else mode,
        "before": digest(target.read_bytes()) if existed else None,
        "after": digest(data),
    }
    if existed:
        saved = backup / f"file-{len(entries)}"
        shutil.copy2(target, saved)
        entry["backup"] = str(saved)
    entries.append(entry)
    (backup / "manifest.json").write_text(json.dumps(entries, indent=2) + "\n")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".apx-pen-new")
    if temporary.exists() or temporary.is_symlink():
        raise RuntimeError(f"temporary path already exists: {temporary}")
    try:
        with temporary.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chown(temporary, int(entry["uid"]), int(entry["gid"]))
        os.chmod(temporary, int(entry["mode"]))
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def preflight() -> None:
    identity()
    for name in NAMES:
        record = json.loads((BASE / name / "registration.json").read_text())
        if (record.get("name"), record.get("role"), record.get("state")) != (
                name, "graphical-base", "stopped") or "files" not in record.get("desktop_modules", []):
            raise RuntimeError(f"{name} is not a stopped file-enabled Environment")
    launcher = Path("/usr/lib/apx/apx-graphical-environment-v1.py")
    if digest(launcher.read_bytes()) != OLD_LAUNCHER:
        raise RuntimeError("installed graphical launcher differs from reviewed baseline")
    seed = Path("/usr/share/apx/config-seeds/environment-shell-v1/gtk-3.0/bookmarks")
    if digest(seed.read_bytes()) != OLD_BOOKMARK:
        raise RuntimeError("installed bookmark seed differs from reviewed baseline")
    runtime = Path("/usr/lib/apx/apx-lab-runtime.py").read_text()
    if runtime.count(OLD_DIGEST) != 1:
        raise RuntimeError("installed runtime bookmark digest differs")
    if Path("/usr/lib/apx/apx-removable-media-v1.py").exists() \
            or Path("/etc/systemd/system/apx-removable-media-v1.service").exists():
        raise RuntimeError("removable PEN bridge is already installed")
    units = run("/usr/bin/systemctl", "--failed", "--no-legend").stdout.strip()
    if units:
        raise RuntimeError("Host has failed units")


def deploy() -> Path:
    preflight()
    backup = BACKUPS / (dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-removable-pen")
    backup.mkdir(mode=0o700)
    entries: list[dict[str, object]] = []
    save_and_write(Path("/usr/lib/apx/apx-removable-media-v1.py"),
                   source("scripts/physical-pilot/apx-removable-media-v1.py"), backup, entries, mode=0o755)
    save_and_write(Path("/etc/systemd/system/apx-removable-media-v1.service"),
                   source("scripts/physical-pilot/apx-removable-media-v1.service"), backup, entries)
    save_and_write(Path("/usr/lib/apx/apx-graphical-environment-v1.py"),
                   source("scripts/physical-pilot/apx-graphical-environment-v1.py"), backup, entries, mode=0o755)
    save_and_write(Path("/usr/share/apx/config-seeds/environment-shell-v1/gtk-3.0/bookmarks"),
                   source("config/environment-shell-v1/gtk-3.0/bookmarks"), backup, entries)
    runtime = Path("/usr/lib/apx/apx-lab-runtime.py")
    save_and_write(runtime, runtime.read_text().replace(OLD_DIGEST, NEW_DIGEST).encode(),
                   backup, entries, mode=0o755)
    for name in NAMES:
        path = BASE / name / "home/apx/.config/gtk-3.0/bookmarks"
        old = path.read_text() if path.exists() else ""
        if BOOKMARK.strip() in old.splitlines():
            continue
        home = BASE / name / "home/apx"
        metadata = home.stat()
        data = (old.rstrip("\n") + "\n" if old else "") + BOOKMARK
        save_and_write(path, data.encode(), backup, entries,
                       owner=(metadata.st_uid, metadata.st_gid), mode=0o644)
    run("/usr/bin/systemctl", "daemon-reload")
    run("/usr/bin/systemctl", "enable", "--now", SERVICE)
    run("/usr/bin/systemctl", "is-active", "--quiet", SERVICE)
    for _ in range(50):
        if host_volume_mounted():
            break
        time.sleep(0.1)
    else:
        raise RuntimeError("Ventoy did not mount on the Host")
    mounted = set(run("/usr/bin/findmnt", "--task", "1", "--mountpoint",
                      "/run/apx/removable-media-v1/Ventoy", "--noheadings",
                      "--output", "SOURCE").stdout.splitlines())
    if mounted != {"/dev/sda1"} or not host_volume_mounted():
        raise RuntimeError(f"Ventoy mount differs: {mounted}")
    print(backup)
    return backup


def rollback(backup: Path) -> None:
    identity()
    for name in NAMES:
        record = json.loads((BASE / name / "registration.json").read_text())
        if record.get("state") != "stopped":
            raise RuntimeError(f"{name} must be stopped before rollback")
    entries = json.loads((backup / "manifest.json").read_text())
    if type(entries) is not list:
        raise RuntimeError("backup manifest is invalid")
    for entry in entries:
        target = Path(entry["target"])
        if not target.is_file() or digest(target.read_bytes()) != entry["after"]:
            raise RuntimeError(f"installed file changed after deployment: {target}")
    run("/usr/bin/systemctl", "disable", "--now", SERVICE)
    if host_volume_mounted():
        run("/usr/bin/nsenter", "--target", "1", "--mount", "--", "/usr/bin/umount",
            "/run/apx/removable-media-v1/Ventoy")
    if host_volume_mounted():
        raise RuntimeError("PEN remains mounted on Host; rollback stopped")
    for entry in reversed(entries):
        target = Path(entry["target"])
        if entry["existed"]:
            shutil.copy2(Path(entry["backup"]), target)
            os.chown(target, int(entry["uid"]), int(entry["gid"]))
            os.chmod(target, int(entry["mode"]))
        else:
            target.unlink()
    run("/usr/bin/systemctl", "daemon-reload")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rollback", type=Path)
    args = parser.parse_args()
    lock = Path("/run/apx/machine-transition-v1.lock")
    with lock.open("a") as descriptor:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.rollback:
            rollback(args.rollback)
        else:
            deploy()


if __name__ == "__main__":
    main()
