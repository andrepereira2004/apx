#!/usr/bin/env python3
"""Copy-only ingress for the APX shared folder."""

import json
import os
from pathlib import Path
import socket
import stat
import struct
import tempfile
import threading

ROOT = Path('/var/lib/apx/transfer-v1')
SOCKET = Path('/run/apx/transfer-v1.sock')
MAX_FILE = 2 * 1024 * 1024 * 1024
MAX_HEADER = 8192


def exact(conn, count):
    result = bytearray()
    while len(result) < count:
        part = conn.recv(min(65536, count - len(result)))
        if not part:
            raise ValueError('incomplete transfer')
        result.extend(part)
    return bytes(result)


def read_header(conn):
    length = struct.unpack('!I', exact(conn, 4))[0]
    if length > MAX_HEADER:
        raise ValueError('header too large')
    value = json.loads(exact(conn, length))
    if not isinstance(value, dict):
        raise ValueError('invalid header')
    return value


def send(conn, value):
    data = json.dumps(value).encode()
    conn.sendall(struct.pack('!I', len(data)) + data)


def components(value):
    if not isinstance(value, str) or not value or len(value) > 1024 or '\x00' in value:
        raise ValueError('invalid path')
    parts = value.split('/')
    if any(p in ('', '.', '..') or len(p.encode()) > 255 for p in parts):
        raise ValueError('invalid path')
    return parts


def directory(root_fd, parts):
    fd = os.dup(root_fd)
    try:
        for part in parts:
            try:
                os.mkdir(part, 0o755, dir_fd=fd)
            except FileExistsError:
                pass
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        return fd
    except BaseException:
        os.close(fd)
        raise


def receive_file(conn, root_fd, parts, size, executable):
    if type(size) is not int or size < 0 or size > MAX_FILE:
        raise ValueError('invalid file size')
    if type(executable) is not bool:
        raise ValueError('invalid executable flag')
    parent_fd = directory(root_fd, parts[:-1])
    temp_name = '.apx-copy-' + next(tempfile._get_candidate_names())
    temp_fd = None
    try:
        temp_fd = os.open(temp_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent_fd)
        left = size
        while left:
            chunk = exact(conn, min(left, 65536))
            os.write(temp_fd, chunk)
            left -= len(chunk)
        os.fchmod(temp_fd, 0o755 if executable else 0o644)
        os.fsync(temp_fd)
        os.close(temp_fd)
        temp_fd = None
        target = parts[-1]
        # Never overwrite an existing file or follow its links.
        suffix = 1
        while True:
            try:
                os.link(temp_name, target, src_dir_fd=parent_fd, dst_dir_fd=parent_fd, follow_symlinks=False)
                break
            except FileExistsError:
                target = f'{parts[-1]} (cópia {suffix})'
                suffix += 1
        os.unlink(temp_name, dir_fd=parent_fd)
        return target
    finally:
        if temp_fd is not None:
            os.close(temp_fd)
        try:
            os.unlink(temp_name, dir_fd=parent_fd)
        except FileNotFoundError:
            pass
        os.close(parent_fd)


def handle(conn):
    with conn:
        root_fd = os.open(ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            request = read_header(conn)
            parts = components(request.get('path'))
            if request.get('type') == 'dir':
                fd = directory(root_fd, parts)
                os.close(fd)
                send(conn, {'ok': True})
            elif request.get('type') == 'file':
                name = receive_file(conn, root_fd, parts, request.get('size'), request.get('executable'))
                send(conn, {'ok': True, 'name': name})
            else:
                raise ValueError('invalid operation')
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            try:
                send(conn, {'ok': False, 'error': str(exc)})
            except OSError:
                pass
        finally:
            os.close(root_fd)


def main():
    ROOT.mkdir(mode=0o755, parents=True, exist_ok=True)
    SOCKET.parent.mkdir(parents=True, exist_ok=True)
    try:
        SOCKET.unlink()
    except FileNotFoundError:
        pass
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
        listener.bind(str(SOCKET))
        os.chmod(SOCKET, 0o666)
        listener.listen(16)
        while True:
            conn, _ = listener.accept()
            threading.Thread(target=handle, args=(conn,), daemon=True).start()


if __name__ == '__main__':
    main()
