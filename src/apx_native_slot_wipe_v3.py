"""Exact p5/p6 logical wipe for a future owner-confirmed native deletion.

The block-device wrapper is pilot-bound. Tests exercise the byte operation on
regular files; no caller may substitute a regular file for a physical target.
"""
import array
import fcntl
import os
from pathlib import Path
import platform
import stat
import subprocess
from uuid import UUID

CHUNK = 8 * 1024**2
BLKGETSIZE64_X86_64 = 0x80081272


def zero_exact_fd(fd, length):
    if type(length) is not int or length <= 0 or length % 4096:
        raise ValueError('invalid native slot wipe length')
    block = b'\0' * CHUNK
    offset = 0
    while offset < length:
        data = block[:min(CHUNK, length - offset)]
        written = os.pwrite(fd, data, offset)
        if written != len(data):
            raise OSError('short native slot wipe')
        offset += written
    os.fsync(fd)
    offset = 0
    while offset < length:
        data = os.pread(fd, min(CHUNK, length - offset), offset)
        if not data or data != block[:len(data)]:
            raise ValueError('native slot wipe verification failed')
        offset += len(data)
    os.fsync(fd)


def wipe_block_partition(path, expected_bytes, expected_partuuid, number):
    """Refuse any path except the exact unmounted pilot p5 or p6 device."""
    if platform.machine() != 'x86_64' or number not in {5, 6}:
        raise ValueError('unsupported native slot wipe target')
    expected = Path('/dev/nvme0n1p' + str(number))
    if Path(path) != expected or type(expected_bytes) is not int or expected_bytes <= 0:
        raise ValueError('native slot wipe target differs')
    if type(expected_partuuid) is not str or len(expected_partuuid) != 36:
        raise ValueError('native slot partition identity differs')
    try:
        if str(UUID(expected_partuuid)) != expected_partuuid:
            raise ValueError('native slot partition identity differs')
    except (TypeError, ValueError) as error:
        raise ValueError('native slot partition identity differs') from error
    info = expected.lstat()
    if not stat.S_ISBLK(info.st_mode) or expected.is_symlink():
        raise ValueError('native slot wipe requires a block partition')
    sysfs = Path('/sys/class/block') / expected.name
    if sysfs.resolve().parent.name != 'nvme0n1' or \
            sysfs.joinpath('partition').read_text().strip() != str(number) or \
            sysfs.joinpath('dev').read_text().strip() != f'{os.major(info.st_rdev)}:{os.minor(info.st_rdev)}':
        raise ValueError('native slot block identity differs')
    result = subprocess.run(['/usr/bin/blkid', '-p', '-s', 'PARTUUID', '-o', 'value', str(expected)],
                            check=True, text=True, capture_output=True, timeout=15)
    if result.stdout.strip().lower() != expected_partuuid:
        raise ValueError('native slot PARTUUID differs')
    fd = os.open(expected, os.O_RDWR | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        observed = os.fstat(fd)
        if not stat.S_ISBLK(observed.st_mode) or observed.st_rdev != info.st_rdev:
            raise ValueError('native slot device changed while opening')
        length = array.array('Q', [0])
        fcntl.ioctl(fd, BLKGETSIZE64_X86_64, length, True)
        if length[0] != expected_bytes:
            raise ValueError('native slot extent changed')
        zero_exact_fd(fd, expected_bytes)
    finally:
        os.close(fd)
