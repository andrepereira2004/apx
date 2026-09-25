"""Crash-resumable relocation of a prepared NTFS image in a DISPOSABLE disk file.

This laboratory executor deliberately rejects block devices. The physical
adapter must additionally prove offline Btrfs shrink/unlock and authenticate
owner approval. Do not point legacy v1 partition executors at a v3 plan.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile

CHUNK = 8 * 1024**2


def atomic_json(path, value):
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, prefix=path.name + '.', delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(value, stream, sort_keys=True)
        stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)


def range_digest(fd, offset, length):
    h = hashlib.sha256()
    while length:
        data = os.pread(fd, min(CHUNK, length), offset)
        if not data:raise ValueError('short disk/image read')
        h.update(data);offset += len(data);length -= len(data)
    return h.hexdigest()


def copy_range(source_fd, disk_fd, offset, length):
    position = 0
    while position < length:
        data = os.pread(source_fd, min(CHUNK, length-position), position)
        if not data:raise ValueError('short backup read')
        written = 0
        while written < len(data):
            count = os.pwrite(disk_fd, data[written:], offset+position+written)
            if count <= 0:raise OSError('short disk write')
            written += count
        position += len(data)
    os.fsync(disk_fd)


def open_regular(path, flags):
    fd = os.open(path, flags | os.O_NOFOLLOW)
    if not stat.S_ISREG(os.fstat(fd).st_mode):
        os.close(fd);raise ValueError('laboratory executor accepts regular files only')
    return fd


def relocate_image(disk, image, *, start_bytes, image_bytes, image_sha256, journal, plan_sha256):
    """Idempotent exact-extent copy, journaled before any write and verified after.

    Extents are explicit so the same operation can be fault-tested at small
    sizes. A physical caller must independently authorize these arguments.
    """
    if type(start_bytes) is not int or type(image_bytes) is not int or start_bytes < 0 or image_bytes <= 0:
        raise ValueError('invalid relocation extent')
    if start_bytes % 4096 or image_bytes % 4096:
        raise ValueError('unaligned relocation extent')
    target_fd = open_regular(disk, os.O_RDWR)
    source_fd = None
    try:
        source_fd = open_regular(image, os.O_RDONLY)
        target, source = os.fstat(target_fd), os.fstat(source_fd)
        if (target.st_dev,target.st_ino)==(source.st_dev,source.st_ino):raise ValueError('source aliases disk')
        if source.st_size != image_bytes or start_bytes + image_bytes > target.st_size:
            raise ValueError('relocation exceeds source or disk')
        if range_digest(source_fd, 0, image_bytes) != image_sha256:
            raise ValueError('backup image hash differs before relocation')
        identity = dict(plan_sha256=plan_sha256, disk_device=target.st_dev, disk_inode=target.st_ino,
                        disk_bytes=target.st_size, start_bytes=start_bytes, image_bytes=image_bytes,
                        image_sha256=image_sha256)
        if journal.exists():
            previous = json.loads(journal.read_bytes())
            if previous.get('identity') != identity or previous.get('state') not in {'copying','verified'}:
                raise ValueError('relocation journal belongs to a different operation')
        else:
            atomic_json(journal, dict(schema=3, state='copying', identity=identity))
        if range_digest(target_fd,start_bytes,image_bytes) != image_sha256:
            copy_range(source_fd,target_fd,start_bytes,image_bytes)
        if range_digest(target_fd,start_bytes,image_bytes) != image_sha256:
            raise ValueError('restored Windows image verification failed')
        if range_digest(source_fd,0,image_bytes) != image_sha256:
            raise ValueError('backup image changed during relocation')
        atomic_json(journal, dict(schema=3, state='verified', identity=identity))
        return identity
    finally:
        if source_fd is not None:os.close(source_fd)
        os.close(target_fd)
