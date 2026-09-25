#!/usr/bin/env python3
"""Publish a read-only, bounded APX Environment storage summary."""

from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile


ENVIRONMENTS = Path("/var/lib/apx/environments")
CACHE = Path("/var/lib/apx/environment-storage-v1/cache.json")
NATIVE_WINDOWS = Path("/var/lib/apx/native-environments/windows.json")
NAME = re.compile(r"[a-z](?:[a-z0-9]|-(?=[a-z0-9])){0,26}")
QGROUP_PATH = re.compile(r"@apx/environments/([a-z](?:[a-z0-9]|-(?=[a-z0-9])){0,26})/(root|home)")


def checked(arguments: tuple[str, ...]) -> str:
    result = subprocess.run(arguments, text=True, capture_output=True, check=False,
                            env={"PATH": "/usr/bin", "LC_ALL": "C"})
    if result.returncode:
        raise RuntimeError("a contabilidade Btrfs não pôde ser lida")
    return result.stdout


def trusted_json(path: Path, maximum: int, mode: int) -> dict[str, object]:
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        info = os.fstat(descriptor); raw = os.read(descriptor, maximum + 1)
    finally:
        os.close(descriptor)
    if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_gid != 0 \
            or stat.S_IMODE(info.st_mode) != mode or not raw or len(raw) > maximum:
        raise RuntimeError("os metadados de armazenamento não são confiáveis")
    value = json.loads(raw)
    if type(value) is not dict:
        raise RuntimeError("os metadados de armazenamento diferem")
    return value


def parse_qgroups(output: str) -> dict[str, int]:
    parts: dict[str, dict[str, int]] = {}
    for line in output.splitlines():
        fields = line.split()
        if len(fields) < 6 or not fields[0].startswith("0/") or not fields[1].isdigit():
            continue
        match = QGROUP_PATH.fullmatch(fields[-1])
        if match is None:
            continue
        parts.setdefault(match.group(1), {})[match.group(2)] = int(fields[1])
    return {name: values["root"] + values["home"] for name, values in parts.items()
            if set(values) == {"root", "home"}}


def registered_names() -> set[str]:
    names: set[str] = set()
    for directory in ENVIRONMENTS.iterdir():
        if not directory.is_dir() or NAME.fullmatch(directory.name) is None:
            continue
        try:
            value = trusted_json(directory / "registration.json", 8192, 0o600)
            if value.get("schema") == 1 and value.get("name") == directory.name \
                    and value.get("state") in {"stopped", "running"} \
                    and (value.get("role"), value.get("release")) in {
                        ("graphical-base", "hyprland-base-v2"), ("hub", "hub-headless-v4")}:
                names.add(directory.name)
        except (OSError, ValueError, KeyError, json.JSONDecodeError, RuntimeError):
            continue
    return names


def subvolume_versions(output: str) -> dict[str, dict[str, str]]:
    versions: dict[str, dict[str, str]] = {}
    for line in output.splitlines():
        match = re.fullmatch(r"ID (\d+) gen (\d+) top level \d+ uuid ([0-9a-f-]+) path (.+)", line)
        if not match:
            continue
        path = QGROUP_PATH.fullmatch(match[4])
        if path:
            versions.setdefault(path[1], {})[path[2]] = ":".join(match.groups()[:3])
    return {name: parts for name, parts in versions.items() if set(parts) == {"root", "home"}}


def cached_measurements() -> dict[str, object]:
    try:
        value = trusted_json(CACHE, 65536, 0o600)
        if value.get("schema") == 1 and type(value.get("entries")) is dict:
            return value["entries"]
    except (OSError, ValueError, RuntimeError):
        pass
    return {}


def refresh_cache() -> None:
    # The UI only reads this file. This protected worker checks Btrfs change
    # generations; unchanged Environments keep their stored measurement.
    with (CACHE.parent / "refresh.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        previous = cached_measurements()
        versions = subvolume_versions(checked(("/usr/bin/btrfs", "subvolume", "list", "-u", "-g", "/")))
        names = registered_names()
        entries = {name: previous[name] for name in names if name in previous
                   and type(previous[name]) is dict and previous[name].get("version") == versions.get(name)
                   and name in versions and type(previous[name].get("bytes")) is int}
        changed = names - entries.keys()
        if changed:
            quota = checked(("/usr/bin/btrfs", "quota", "status", str(ENVIRONMENTS)))
            required = ("Enabled:                 yes", "Mode:                    qgroup (full accounting)",
                        "Inconsistent:            no", "Override limits:         no")
            if any(field not in quota for field in required):
                raise RuntimeError("a contabilidade Btrfs não está estável")
            sizes = parse_qgroups(checked(("/usr/bin/btrfs", "qgroup", "show", "--raw", "-re", "/")))
            # Do not tag a measurement with a generation changed during the read.
            after = subvolume_versions(checked(("/usr/bin/btrfs", "subvolume", "list", "-u", "-g", "/")))
            for name in changed:
                if name in sizes and name in versions and versions[name] == after.get(name):
                    entries[name] = {"version": versions[name], "bytes": sizes[name]}
                elif name in previous and name in versions and type(previous[name]) is dict \
                        and all(previous[name].get("version", {}).get(part, "").split(":")[-1]
                                == versions[name][part].split(":")[-1] for part in ("root", "home")):
                    entries[name] = previous[name]
        if entries == previous:
            return
        descriptor, temporary = tempfile.mkstemp(dir=CACHE.parent, prefix=".cache-")
        try:
            with os.fdopen(descriptor, "w") as stream:
                json.dump({"schema": 1, "entries": entries}, stream, sort_keys=True)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, CACHE)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


def storage_status() -> dict[str, object]:
    if os.geteuid() != 0:
        raise RuntimeError("a medição requer o executor protegido")
    entries = cached_measurements()
    names = registered_names()
    sizes = {name: item["bytes"] for name, item in entries.items()
             if name in names and type(item) is dict
             and type(item.get("bytes")) is int and 0 <= item["bytes"] <= 256 * 1024**3}
    try:
        windows = trusted_json(NATIVE_WINDOWS, 4096, 0o400)
        size = windows.get("requested_size_gib")
        expected_reserved = (1000215183 - ((1000215183 - size * 2097152) // 2048 * 2048)) * 512 \
            if size in {80, 120, 160} else -1
        if (windows.get("schema"), windows.get("profile"), windows.get("name"),
                windows.get("state")) == (2, "apx-native-environment-v2", "windows", "ready") \
                and windows.get("reserved_bytes") == expected_reserved:
            sizes["windows"] = int(windows["reserved_bytes"])
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError):
        pass
    filesystem = os.statvfs(ENVIRONMENTS)
    total = filesystem.f_blocks * filesystem.f_frsize
    available = filesystem.f_bavail * filesystem.f_frsize
    if not 128 * 1024**3 <= total <= 1024**4 or not 0 <= available <= total or len(sizes) > 64:
        raise RuntimeError("a capacidade do APX difere")
    return {"schema": 1, "profile": "apx-environment-storage-v1",
            "available_bytes": available, "total_bytes": total, "sizes": sizes}


def main() -> int:
    if sys.argv[1:] == ["--refresh"]:
        refresh_cache()
        return 0
    if sys.argv[1:]:
        raise RuntimeError("argumentos inválidos")
    print(json.dumps(storage_status(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"APX recusou a medição: {error}", file=sys.stderr)
        raise SystemExit(2)
