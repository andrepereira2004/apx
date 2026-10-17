"""Owner-enrolled, independent workload face unlock configuration.

The root-owned identity is opt-in and never belongs to the public shell seed.
Only the lock-screen PAM consumer receives biometric authentication.
"""
from __future__ import annotations

import configparser
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile


def trusted_file(path: Path, owner: int = 0) -> bytes:
    metadata = path.lstat()
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_uid != owner or metadata.st_mode & 0o022:
        raise ValueError("Face identity file is not protected")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        current = os.fstat(descriptor)
        if (current.st_ino, current.st_dev) != (metadata.st_ino, metadata.st_dev):
            raise ValueError("Face identity file changed during validation")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            return stream.read()
    finally:
        os.close(descriptor)


def load_identity(directory: Path) -> dict[str, bytes] | None:
    if not directory.exists():
        return None
    info = directory.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o077:
        raise ValueError("Face identity directory is not private")
    manifest = json.loads(trusted_file(directory / "manifest.json"))
    if manifest.get("schema") != 1 or type(manifest.get("enabled")) is not bool:
        raise ValueError("Face identity is not explicitly enrolled")
    if manifest["enabled"] is False:
        return None
    if set(manifest.get("files", {})) != {"config.ini", "apx.dat", "hyprlock.pam"}:
        raise ValueError("Face identity manifest is incomplete")
    data = {}
    for name, expected in manifest["files"].items():
        value = trusted_file(directory / name)
        if not value or hashlib.sha256(value).hexdigest() != expected:
            raise ValueError("Face identity digest mismatch")
        data[name] = value
    config = configparser.ConfigParser()
    config.read_string(data["config.ini"].decode())
    if config.getboolean("core", "disabled", fallback=True) or not config.getboolean("core", "abort_if_ssh", fallback=False):
        raise ValueError("Face identity camera policy is invalid")
    if config.getboolean("snapshots", "save_failed", fallback=True) or config.getboolean("snapshots", "save_successful", fallback=True):
        raise ValueError("Face identity must not save camera images")
    pam = data["hyprlock.pam"].decode()
    if "pam_howdy.so" not in pam or "pam_unix.so" not in pam or "pam_faillock.so authsucc" not in pam:
        raise ValueError("Face identity password fallback is absent")
    return data


def install_identity(root: Path, data: dict[str, bytes]) -> None:
    """Write an independent copy with stopped or shifted active-root ownership."""
    info = root.lstat()
    if not stat.S_ISDIR(info.st_mode) or root.is_symlink():
        raise ValueError("Environment root is invalid")
    etc = root / "etc"
    if etc.is_symlink() or etc.stat().st_uid != info.st_uid:
        raise ValueError("Environment ownership is inconsistent")
    groups = trusted_file(etc / "group", info.st_uid).decode().splitlines()
    group = next((int(line.split(":")[2]) for line in groups if line.startswith("apx:")), None)
    if group != 1000:
        raise ValueError("Environment APX group is unsupported")
    for relative in ("etc/howdy", "etc/howdy/models"):
        path = root / relative
        if path.is_symlink():
            raise ValueError("Face identity directory is linked")
        path.mkdir(exist_ok=True)
        os.chown(path, info.st_uid, info.st_gid + group)
        path.chmod(0o750)
    for relative, value, mode, gid in (
        ("etc/howdy/config.ini", data["config.ini"], 0o640, info.st_gid + group),
        ("etc/howdy/models/apx.dat", data["apx.dat"], 0o640, info.st_gid + group),
        ("etc/pam.d/hyprlock", data["hyprlock.pam"], 0o644, info.st_gid),
    ):
        path = root / relative
        if path.is_symlink() or path.parent.is_symlink():
            raise ValueError("Face identity destination is linked")
        descriptor, temporary = tempfile.mkstemp(prefix=".apx-face-", dir=path.parent)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(value)
                stream.flush()
                os.fsync(stream.fileno())
            os.chown(temporary, info.st_uid, gid)
            os.chmod(temporary, mode)
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
