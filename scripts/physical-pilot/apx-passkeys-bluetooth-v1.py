#!/usr/bin/python
"""Expose only host BlueZ to the active APX desktop, across its UID namespace.

xdg-dbus-proxy supplies the D-Bus policy. The relay translates EXTERNAL
authentication, verifies the desktop user's kernel credentials, and disables
FD negotiation because its stream transport does not forward SCM_RIGHTS.
"""
import asyncio
import contextlib
import json
import os
from pathlib import Path
import signal
import socket
import struct

UPSTREAM = '/run/apx/passkeys-v1/bluez-bus'
STATE = Path('/run/apx/active-graphical-environment-v1.json')
SOCKET = '/run/apx/passkeys-browser-bus'


def desktop():
    state = json.loads(STATE.read_text())
    pid = int(state['pid'])
    if pid <= 1 or Path(f'/proc/{pid}/comm').read_text().strip() != 'Hyprland':
        raise ValueError('No active desktop')
    maps = [tuple(map(int, line.split())) for line in Path(f'/proc/{pid}/uid_map').read_text().splitlines()]
    uid = next(outside + 1000 - inside for inside, outside, length in maps if inside <= 1000 < inside + length)
    maps = [tuple(map(int, line.split())) for line in Path(f'/proc/{pid}/gid_map').read_text().splitlines()]
    gid = next(outside + 1000 - inside for inside, outside, length in maps if inside <= 1000 < inside + length)
    start = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[19]
    return pid, uid, gid, start


async def relay(reader, writer, uid):
    upstream = None
    tasks = []
    try:
        peer = writer.get_extra_info('socket').getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)
        if struct.unpack('3i', peer)[1] != uid:
            return
        first = await asyncio.wait_for(reader.readline(), 5)
        if not first.startswith(b'\0AUTH EXTERNAL') or not first.endswith(b'\r\n'):
            return
        remote, upstream = await asyncio.open_unix_connection(UPSTREAM)
        # The filtered upstream connection belongs to this host service.
        upstream.write(b'\0AUTH EXTERNAL ' + str(os.getuid()).encode().hex().encode() + b'\r\n')
        await upstream.drain()
        reply = await asyncio.wait_for(remote.readline(), 5)
        writer.write(reply)
        await writer.drain()
        if not reply.startswith(b'OK '):
            return
        while True:
            line = await asyncio.wait_for(reader.readline(), 5)
            if line == b'BEGIN\r\n':
                upstream.write(line)
                await upstream.drain()
                break
            if line == b'NEGOTIATE_UNIX_FD\r\n':
                writer.write(b'ERROR Unix FD passing is not supported\r\n')
                await writer.drain()
            else:
                return

        async def pump(source, target):
            while data := await source.read(65536):
                target.write(data)
                await target.drain()

        tasks = [asyncio.create_task(pump(reader, upstream)), asyncio.create_task(pump(remote, writer))]
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    except (OSError, ValueError, asyncio.TimeoutError):
        pass
    finally:
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        writer.close()
        if upstream:
            upstream.close()


async def main():
    os.makedirs(os.path.dirname(UPSTREAM), mode=0o700, exist_ok=True)
    with contextlib.suppress(FileNotFoundError):
        os.unlink(UPSTREAM)
    proxy = await asyncio.create_subprocess_exec(
        '/usr/local/lib/apx-passkeys/xdg-dbus-proxy',
        'unix:path=/run/dbus/system_bus_socket', UPSTREAM, '--filter', '--talk=org.bluez')
    server = None
    identity = None
    endpoint = None
    clients = set()
    stopped = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stopped.set)
    try:
        while not stopped.is_set():
            if proxy.returncode is not None:
                raise RuntimeError('Filtered BlueZ proxy exited')
            try:
                current = desktop()
            except (OSError, ValueError, KeyError, StopIteration):
                current = None
            if current != identity:
                if server:
                    server.close()
                    await server.wait_closed()
                    for client in list(clients):
                        client.cancel()
                    await asyncio.gather(*clients, return_exceptions=True)
                    clients.clear()
                    server = None
                if endpoint:
                    with contextlib.suppress(FileNotFoundError, ProcessLookupError):
                        os.unlink(endpoint)
                    endpoint = None
                identity = None
                if current:
                    pid, uid, gid, _ = current
                    path = f'/proc/{pid}/root{SOCKET}'
                    with contextlib.suppress(FileNotFoundError):
                        os.unlink(path)

                    async def accept(reader, writer, expected_uid=uid):
                        task = asyncio.current_task()
                        clients.add(task)
                        try:
                            await relay(reader, writer, expected_uid)
                        finally:
                            clients.discard(task)

                    server = await asyncio.start_unix_server(accept, path, limit=4096)
                    os.chown(path, uid, gid)
                    os.chmod(path, 0o600)
                    identity, endpoint = current, path
                    print(f'BlueZ ready for active desktop PID {pid}', flush=True)
            try:
                await asyncio.wait_for(stopped.wait(), 2)
            except asyncio.TimeoutError:
                pass
    finally:
        if server:
            server.close()
            await server.wait_closed()
        for task in list(clients):
            task.cancel()
        await asyncio.gather(*clients, return_exceptions=True)
        if endpoint:
            with contextlib.suppress(OSError):
                os.unlink(endpoint)
        if proxy.returncode is None:
            proxy.terminate()
            await proxy.wait()
        with contextlib.suppress(FileNotFoundError):
            os.unlink(UPSTREAM)


if __name__ == '__main__':
    asyncio.run(main())
