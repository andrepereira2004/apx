"""Prepare/verify NTFS image files for a future offline native migration.

Only output image files are resized. No physical partition is resized, moved,
formatted or written. Entry-point authorization and disk identity belong to
the future Host lifecycle executor, not this image preparation primitive.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess


def run(*args):
    return subprocess.run(args, check=True, text=True, capture_output=True,
                          env={"PATH": "/usr/bin", "LC_ALL": "C"})


def image_hash(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def source_fingerprint(path):
    """Hash the full original extent, including blocks omitted by ntfsclone."""
    info = path.lstat()
    if stat.S_ISREG(info.st_mode):
        length = info.st_size
    elif stat.S_ISBLK(info.st_mode):
        length = int(run("/usr/bin/blockdev", "--getsize64", str(path)).stdout.strip())
    else:
        raise ValueError("source must be a regular image or block device")
    if length <= 0:
        raise ValueError("empty backup source")
    digest = hashlib.sha256()
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        observed = os.fstat(fd)
        if (observed.st_dev, observed.st_ino, observed.st_rdev) != (info.st_dev, info.st_ino, info.st_rdev):
            raise ValueError("backup source changed")
        remaining = length
        while remaining:
            data = os.read(fd, min(8 * 1024**2, remaining))
            if not data:
                raise ValueError("short backup source read")
            digest.update(data)
            remaining -= len(data)
    finally:
        os.close(fd)
    return {"bytes": length, "sha256": digest.hexdigest()}


def prepare_images(source: Path, directory: Path, target_bytes: int, *, prepared_metadata=None, plan_sha256=None):
    """Create an original raw backup and a smaller reflinked preparation copy.

    Refuses to reuse a directory or existing image, and validates the source
    and both NTFS images with ntfsresize's read-only consistency check.
    """
    if type(target_bytes) is not int or target_bytes <= 0 or target_bytes % 4096:
        raise ValueError("invalid target byte size")
    if plan_sha256 is not None and (type(plan_sha256) is not str or not re.fullmatch(r"[0-9a-f]{64}", plan_sha256)):
        raise ValueError("invalid migration plan hash")
    if prepared_metadata is not None:
        name, content = prepared_metadata
        if not re.fullmatch(r"APX-[0-9a-f-]{36}\.ini", name) or type(content) is not bytes or len(content) > 4096:
            raise ValueError("invalid prepared image metadata")
    source_info = source.lstat()
    if not (stat.S_ISREG(source_info.st_mode) or stat.S_ISBLK(source_info.st_mode)):
        raise ValueError("source must be a regular image or block device")
    if directory.exists() or directory.is_symlink():
        raise ValueError("backup output directory already exists")
    source_before = source_fingerprint(source)
    initial = run("/usr/bin/ntfsresize", "--info", "--no-action", str(source)).stdout
    minimum = re.search(r"You might resize at (\d+) bytes", initial)
    if not minimum or target_bytes < int(minimum.group(1)):
        raise ValueError("NTFS data does not fit the requested image")
    directory.mkdir(mode=0o700)
    original = directory / "original.ntfs.raw"
    prepared = directory / "prepared.ntfs.raw"
    old_mask = os.umask(0o077)
    stage = "clone-original"
    try:
        # Without --save-image, ntfsclone creates a sparse raw NTFS filesystem.
        # Keep the original intact; shrinking happens on a COW copy only.
        run("/usr/bin/ntfsclone", "--output", str(original), str(source))
        if source_fingerprint(source) != source_before:
            raise ValueError("Windows source changed during backup")
        run("/usr/bin/ntfsresize", "--info", "--no-action", str(original))
        original_digest = image_hash(original)
        stage = "prepare-copy"
        run("/usr/bin/cp", "--reflink=always", str(original), str(prepared))
        run("/usr/bin/ntfsresize", "--force", "--size", str(target_bytes), str(prepared))
        # The NTFS resize tool leaves the containing file at its old length.
        # Truncate only our private image after its filesystem was resized.
        with prepared.open("r+b") as stream:
            stream.truncate(target_bytes)
            stream.flush()
            os.fsync(stream.fileno())
        if prepared_metadata is not None:
            name, content = prepared_metadata
            metadata_file = directory / "source-contract.ini"
            metadata_file.write_bytes(content)
            run("/usr/bin/ntfscp", "--force", str(prepared), str(metadata_file), "/" + name)
        stage = "verify-prepared"
        # A just-resized NTFS volume is marked for a Windows check. --force
        # bypasses that flag only for this read-only check of our image copy.
        run("/usr/bin/ntfsresize", "--force", "--info", "--no-action", str(prepared))
        if image_hash(original) != original_digest:
            raise ValueError("original backup changed during preparation")
        manifest = {"schema": 3, "profile": "apx-native-image-backup-v3", "state": "verified-images",
                    "original": {"file": original.name, "bytes": original.stat().st_size, "sha256": original_digest},
                    "prepared": {"file": prepared.name, "bytes": prepared.stat().st_size, "sha256": image_hash(prepared)},
                    "source_identity": {"device": source_info.st_dev, "inode": source_info.st_ino, "rdev": source_info.st_rdev},
                    "source_fingerprint": source_before, "plan_sha256": plan_sha256}
        manifest_path = directory / "manifest.json"
        with manifest_path.open("x") as stream:
            json.dump(manifest, stream, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        for image in (original, prepared):
            with image.open("rb") as stream:
                os.fsync(stream.fileno())
        descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        return manifest
    except Exception:
        (directory / "failed.json").write_text(json.dumps({"stage": stage, "state": "failed"}))
        raise
    finally:
        os.umask(old_mask)
