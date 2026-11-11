#!/usr/bin/env python3
"""Reconcile the fixed pilot's Windows test record after APX Recovery was added."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

sys.path.insert(0, "/usr/lib/apx")
from apx_native_instances_v3 import validate_instances

RECORD = Path("/var/lib/apx/native-environments/instances-v3/windows-testes.json")
EXPECTED_PARTUUID = "eddf4dba-7748-5ad6-a640-c9af195f5e1e"
EXPECTED_START = 813568000
OLD_SIZE = 167772160
NEW_SIZE = 161480704


def main():
    if os.geteuid() or Path("/etc/hostname").read_text().strip() != "apx-host" \
            or Path("/sys/class/dmi/id/product_name").read_text().strip() != "82JU":
        raise RuntimeError("pilot identity differs")
    table = json.loads(subprocess.check_output(("sfdisk", "--json", "/dev/nvme0n1")))["partitiontable"]
    parts = {part["uuid"].lower(): part for part in table["partitions"]}
    part = parts.get(EXPECTED_PARTUUID)
    if not part or part["node"] != "/dev/nvme0n1p5" or part["start"] != EXPECTED_START \
            or part["size"] != NEW_SIZE or part["type"].lower() != "ebd0a0a2-b9e5-4433-87c0-68b6b72699c7":
        raise RuntimeError("Windows test partition differs")
    with open(part["node"], "rb") as device:
        sector = device.read(512)
    if sector[3:11] != b"NTFS    " or struct.unpack_from("<H", sector, 11)[0] != 512 \
            or struct.unpack_from("<Q", sector, 40)[0] > NEW_SIZE:
        raise RuntimeError("NTFS does not fit the current partition")
    original = RECORD.read_bytes()
    record = json.loads(original)
    if record.get("windows_partuuid", "").lower() != EXPECTED_PARTUUID \
            or record.get("start_sector") != EXPECTED_START or record.get("size_sectors") != OLD_SIZE \
            or record.get("name") != "windows-testes" or record.get("state") != "ready":
        raise RuntimeError("native record differs")
    record["size_sectors"] = NEW_SIZE
    other = json.loads((RECORD.parent / "windows.json").read_bytes())
    serial = Path("/sys/class/block/nvme0n1/device/serial").read_text().strip()
    validate_instances([other, record], table, serial)
    backup_dir = Path("/var/lib/apx/backups/20261030-native-catalog-recovery-fix")
    backup_dir.mkdir(mode=0o700, exist_ok=True)
    backup = backup_dir / "windows-testes.json"
    if backup.exists():
        raise RuntimeError("backup already exists")
    shutil.copy2(RECORD, backup)
    content = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
    fd, temp = tempfile.mkstemp(prefix=".windows-testes-", dir=RECORD.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp, 0o400)
        os.replace(temp, RECORD)
        dirfd = os.open(RECORD.parent, os.O_DIRECTORY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    print(f"Updated Windows test extent to {NEW_SIZE} sectors; backup={backup}; sha256={hashlib.sha256(content).hexdigest()}")


if __name__ == "__main__":
    main()
