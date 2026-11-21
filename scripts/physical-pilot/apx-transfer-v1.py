#!/usr/bin/env python3
"""Bounded copy and rename operations for the APX shared folder."""

import ctypes
import errno
import hashlib
import re
import time
import configparser
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


def rename_entry(root_fd, parts, name):
    if len(components(name)) != 1 or name.startswith('.apx-') or any(p.startswith('.apx-') for p in parts):
        raise ValueError('Nome inválido')
    fd = os.dup(root_fd)
    try:
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd); fd = child
        info = os.stat(parts[-1], dir_fd=fd, follow_symlinks=False)
        if not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
            raise ValueError('Apenas ficheiros e pastas podem mudar de nome')
        rename = ctypes.CDLL(None, use_errno=True).renameat2
        rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        rename.restype = ctypes.c_int
        if rename(fd, os.fsencode(parts[-1]), fd, os.fsencode(name), 1):
            code = ctypes.get_errno()
            if code == errno.EEXIST: raise ValueError('Já existe um ficheiro ou pasta com esse nome')
            raise OSError(code, os.strerror(code))
        os.fsync(fd)
    finally:
        os.close(fd)


def wallpaper_usage(environments=Path('/var/lib/apx/environments')):
    used = {}
    for env in environments.iterdir():
        if not (env / 'registration.json').is_file(): continue
        try:
            home = env / 'home/apx'
            values = json.loads((home / '.config/apx/appearance.json').read_text())
            image = Path(values.get('wallpaper', ''))
            if image.parent != Path('/home/apx/.local/share/apx/appearance/wallpapers'): continue
            if not re.fullmatch(r'[a-f0-9]{64}\.(png|jpg|jpeg|bmp|webp)', image.name): continue
            if not (home / '.local/share/apx/appearance/wallpapers' / image.name).is_file(): continue
            used.setdefault(image.stem, []).append(env.name)
        except (OSError, ValueError, TypeError): continue
    return used


def publish_usage():
    cache = {}
    while True:
        try:
            used = wallpaper_usage()
            parser = configparser.ConfigParser(interpolation=None)
            parser.optionxform = str
            parser['used'] = {}
            folder = ROOT / 'wallpaper'
            current = {}
            for image in folder.iterdir():
                info = image.lstat()
                if not stat.S_ISREG(info.st_mode) or info.st_size > 40 * 1024 * 1024: continue
                key = (image.name, info.st_ino, info.st_size, info.st_mtime_ns)
                digest = cache.get(key)
                if digest is None: digest = hashlib.sha256(image.read_bytes()).hexdigest()
                current[key] = digest
                if digest in used:
                    from urllib.parse import quote
                    parser['used'][quote(image.name, safe='')] = ', '.join(sorted(used[digest]))
            cache = current
            import io
            output = io.StringIO(); parser.write(output, space_around_delimiters=False)
            target = ROOT / '.apx-wallpaper-used'
            content = output.getvalue()
            if not target.exists() or target.read_text() != content:
                temporary = ROOT / '.apx-wallpaper-used-new'
                temporary.write_text(content); temporary.chmod(0o644); os.replace(temporary, target)
        except (OSError, ValueError): pass
        time.sleep(2)


def handle(conn):
    with conn:
        root_fd = os.open(ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            request = read_header(conn)
            parts = components(request.get('path'))
            if request.get('type') == 'rename':
                rename_entry(root_fd, parts, request.get('name'))
                send(conn, {'ok': True})
            elif request.get('type') == 'dir':
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
    threading.Thread(target=publish_usage, daemon=True).start()
    shared_socket = ROOT / '.apx-transfer.sock'
    def shared_listener():
        shared_socket.unlink(missing_ok=True)
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as shared:
            shared.bind(str(shared_socket)); os.chmod(shared_socket, 0o666); shared.listen(16)
            while True:
                conn, _ = shared.accept()
                threading.Thread(target=handle, args=(conn,), daemon=True).start()
    threading.Thread(target=shared_listener, daemon=True).start()
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
        listener.bind(str(SOCKET))
        os.chmod(SOCKET, 0o666)
        listener.listen(16)
        while True:
            conn, _ = listener.accept()
            threading.Thread(target=handle, args=(conn,), daemon=True).start()


if __name__ == '__main__':
    main()
