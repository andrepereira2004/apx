#!/usr/bin/env python3
"""Exact owner-authorized cleanup of completed pilot labs, not a general cleaner."""
from __future__ import annotations
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
EVIDENCE = REPO / "audit/2026-10-18-storage-cleanup"
GENERATION = "2770478b-480f-4aea-8910-e3201d5334c5"
NATIVE = Path("/var/lib/apx/native-environments")
JOB = NATIVE / "migrations-v3" / GENERATION
FILES = [JOB / relative for relative in (
    "images/original.ntfs.raw", "images/prepared.ntfs.raw", "boot.wim", "previous-boot.wim",
    "maintenance-relocate/maintenance.efi", "maintenance-rollback/maintenance.efi")]
FILES += [Path("/root/apx-teste-de-vm/disk-v5.raw"), Path("/root/apx-teste-de-vm-github/disk.raw")]
DIRECTORIES = [Path("/root/apx-teste-de-vm/rootfs"), Path("/root/apx-teste-de-vm-github/rootfs")]
OLD_SNAPSHOTS = [Path("/.snapshots/local-recovery/system") / name
                 for name in ("20261007T065356Z", "20261012T112430Z")]


def call(*args):
    return subprocess.check_output(args, text=True).strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signatures():
    paths = list(Path("/var/lib/apx/environments").glob("*/registration.json"))
    paths += list((NATIVE / "instances-v3").glob("*.json")) + [NATIVE / "windows.json"]
    return {str(path): digest(path) for path in paths}


def write_new(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def assert_idle():
    for path in (NATIVE / "pending-v3.json", NATIVE / "windows-pending.json",
                 Path("/run/apx/environment-management-v1.lock")):
        if path.exists() or path.is_symlink():
            raise RuntimeError(f"operation pending: {path}")


def assert_unused(paths):
    prefixes = tuple(str(p) for p in paths)
    def selected(value):
        return any(value == p or value.startswith(p + "/") for p in prefixes)
    for line in Path("/proc/self/mountinfo").read_text().splitlines():
        if selected(line.split()[4]):
            raise RuntimeError("cleanup target contains an active mount")
    for proc in Path("/proc").iterdir():
        if not proc.name.isdecimal():
            continue
        try:
            entries = list((proc / "fd").iterdir()) + [proc / "cwd", proc / "root", proc / "exe"]
        except (FileNotFoundError, PermissionError):
            continue
        for entry in entries:
            try:
                if selected(os.readlink(entry)):
                    raise RuntimeError(f"cleanup target is in use by PID {proc.name}")
            except (FileNotFoundError, PermissionError, OSError) as error:
                if isinstance(error, RuntimeError):
                    raise
    for backing in Path("/sys/block").glob("loop*/loop/backing_file"):
        if selected("/" + backing.read_text().strip().lstrip("/")):
            raise RuntimeError("cleanup target is attached to a loop device")


def main():
    if sys.argv[1:] != ["--apply"]:
        raise RuntimeError("Read the exact target list; run with --apply for the owner-authorized cleanup")
    if os.geteuid() != 0 or Path("/proc/sys/kernel/hostname").read_text().strip() != "apx-host" \
            or Path("/sys/class/dmi/id/product_name").read_text().strip() != "82JU":
        raise RuntimeError("this cleanup is for the current pilot only; it is not a portable installer")
    if json.loads((JOB / "job.json").read_text()).get("stage") != "ready" \
            or json.loads((JOB / "authorization.json").read_text()).get("state") != "retired":
        raise RuntimeError("migration is not complete and retired")
    instances = [json.loads(p.read_text()) for p in (NATIVE / "instances-v3").glob("*.json")]
    if len(instances) != 2 or any(x.get("state") != "ready" for x in instances) \
            or {x["name"] for x in instances} != {"windows", "windows-testes"}:
        raise RuntimeError("current Windows registrations differ")
    assert_idle()
    for path in FILES + DIRECTORIES + OLD_SNAPSHOTS:
        if path.is_symlink() or not path.exists() or path.resolve() != path:
            raise RuntimeError(f"missing or linked target: {path}")
    for path in FILES:
        if not stat.S_ISREG(path.stat().st_mode):
            raise RuntimeError("file target is not regular")
    for path in DIRECTORIES:
        if not path.is_dir():
            raise RuntimeError("directory target differs")
        # A nested Btrfs subvolume cannot be safely erased with rmtree.
        for parent, dirs, files in os.walk(path, followlinks=False):
            if Path(parent).stat().st_ino == 256:
                raise RuntimeError(f"unexpected subvolume in ordinary lab tree: {parent}")
    assert_unused(FILES + DIRECTORIES + OLD_SNAPSHOTS)
    EVIDENCE.mkdir(mode=0o700, parents=True, exist_ok=True)
    before = {"schema": 1, "authorization": "owner explicitly requested old/irrelevant data cleanup on 2026-10-18",
              "free_bytes": shutil.disk_usage("/").free, "registrations": signatures(),
              "partition_table_sha256": hashlib.sha256(call("sfdisk", "--json", "/dev/nvme0n1").encode()).hexdigest(),
              "files": [{"path": str(p), "size": p.stat().st_size, "allocated_bytes": p.stat().st_blocks * 512,
                         "inode": p.stat().st_ino} for p in FILES],
              "directories": [str(p) for p in DIRECTORIES], "replaced_system_snapshots": [str(p) for p in OLD_SNAPSHOTS],
              "preserved": ["Windows partitions/registrations/boot files", "active Environments and homes",
                            "installation ISO templates and package artifacts", "all lab logs", "all Environment recovery snapshots"]}
    write_new(EVIDENCE / "before.json", before)
    with Path("/run/lock/apx-local-recovery.lock").open("a") as lock, \
            (EVIDENCE / "actions.jsonl").open("x") as actions:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        def event(action, path):
            actions.write(json.dumps({"action": action, "path": str(path)}) + "\n")
            actions.flush()
            os.fsync(actions.fileno())
        for path in FILES:
            assert_idle()
            event("unlink-start", path)
            path.unlink()
            event("unlink-complete", path)
        for path in DIRECTORIES:
            assert_idle()
            event("remove-lab-root-start", path)
            shutil.rmtree(path)
            event("remove-lab-root-complete", path)
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        snapshot = Path("/.snapshots/local-recovery/system") / stamp
        event("create-current-system-snapshot-start", snapshot)
        call("btrfs", "subvolume", "snapshot", "-r", "/", str(snapshot))
        event("create-current-system-snapshot-complete", snapshot)
        for path in OLD_SNAPSHOTS:
            assert_idle()
            event("delete-old-system-snapshot-start", path)
            call("btrfs", "subvolume", "delete", str(path))
            event("delete-old-system-snapshot-complete", path)
        call("btrfs", "subvolume", "sync", "/")
    after = {"schema": 1, "free_bytes": shutil.disk_usage("/").free,
             "registrations": signatures(), "new_system_snapshot": str(snapshot),
             "partition_table_sha256": hashlib.sha256(call("sfdisk", "--json", "/dev/nvme0n1").encode()).hexdigest(),
             "deleted_targets_absent": all(not p.exists() for p in FILES + DIRECTORIES + OLD_SNAPSHOTS)}
    after["registrations_unchanged"] = after["registrations"] == before["registrations"]
    after["partition_table_unchanged"] = after["partition_table_sha256"] == before["partition_table_sha256"]
    after["freed_bytes"] = after["free_bytes"] - before["free_bytes"]
    write_new(EVIDENCE / "after.json", after)
    if not all(after[k] for k in ("registrations_unchanged", "partition_table_unchanged", "deleted_targets_absent")):
        raise RuntimeError("post-cleanup verification requires inspection")
    print(json.dumps(after, indent=2))


if __name__ == "__main__":
    main()
