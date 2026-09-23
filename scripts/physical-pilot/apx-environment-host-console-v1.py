#!/usr/bin/env python3
"""Owner-authorized Host console from the active workload's QuickShell.

Separate endpoint preserves Hub role detection and existing Hub console lifetime.
The shared broker supplies framing and the fixed root PTY, never a command API.
"""
from __future__ import annotations
import importlib.util
import json
import os
from pathlib import Path
import secrets
import select
import threading
import time
import sys
sys.path.insert(0, "/usr/lib/apx")

from apx_host_services_peer import HostServicesPeer, authorize_active_environment_peer

spec = importlib.util.spec_from_file_location('apx_host_console_base', Path(__file__).with_name('apx-host-console-v1.py'))
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
SOCKET = Path('/run/apx/environment-host-console-v1.sock')
AUDIT = Path('/var/lib/apx/host-console-v1/environment-audit.jsonl')
LOCK = threading.Lock()
TICKETS = {}
IDENTITIES = {}


def authorize(peer):
    identity = authorize_active_environment_peer(peer)
    if identity.role != 'graphical-base':
        raise PermissionError('Host console requires the active graphical workload')
    with LOCK:
        IDENTITIES[peer.uid] = identity
    return identity


def ancestry(peer, proc=Path('/proc')):
    # authorize() first proves the peer belongs to the trusted active unit.
    # Every ancestor must stay in that exact service cgroup boundary.
    lines = (proc / str(peer.pid) / 'cgroup').read_text().splitlines()
    groups = [line.split(':', 2)[2] for line in lines if line.startswith('0::')]
    if len(groups) != 1:
        raise PermissionError('Host console cgroup identity unavailable')
    parts = groups[0].split('/')
    if len(parts) < 3 or parts[1] != 'system.slice' or not parts[2].endswith('.service'):
        raise PermissionError('Host console service boundary differs')
    unit = '/system.slice/' + parts[2]
    current = peer.pid
    for _ in range(8):
        fields = dict(line.split(':', 1) for line in (proc / str(current) / 'status').read_text().splitlines() if ':' in line)
        parent = int(fields['PPid'].strip())
        if parent <= 1:
            break
        cgroups = (proc / str(parent) / 'cgroup').read_text().splitlines()
        if not any(line == '0::' + unit or line.startswith('0::' + unit + '/') for line in cgroups):
            break
        if (proc / str(parent) / 'comm').read_text().strip() == 'quickshell' and os.readlink(proc / str(parent) / 'exe') == '/usr/bin/quickshell':
            return parent
        current = parent
    raise PermissionError('Host-console caller is not an active QuickShell descendant')


def issue_ticket(peer):
    identity = authorize(peer)
    ancestry(peer)
    now = time.monotonic()
    token = secrets.token_urlsafe(32)
    with LOCK:
        for key in [k for k,v in TICKETS.items() if v[2] <= now]:
            del TICKETS[key]
        TICKETS[token] = (peer.uid, identity, now + base.TICKET_TTL_SECONDS)
    return token


def consume_ticket(token, peer):
    identity = authorize(peer)
    if type(token) is not str or not 32 <= len(token) <= 128:
        raise PermissionError('Host-console ticket differs')
    with LOCK:
        admitted = TICKETS.pop(token, None)
    if admitted is None or admitted[:2] != (peer.uid, identity) or admitted[2] <= time.monotonic():
        raise PermissionError('Host-console ticket is stale, used or belongs to another Environment')


def audit(event, result, uid=None):
    AUDIT.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with LOCK:
        identity = IDENTITIES.get(uid)
    record = dict(schema=1, time=int(time.time()), event=event, result=result,
                  peer_uid=uid, environment=identity.name if identity else None,
                  generation=identity.generation if identity else None)
    fd = os.open(AUDIT, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        os.write(fd, (json.dumps(record, sort_keys=True) + '\n').encode())
    finally:
        os.close(fd)


def bridge(connection, peer, rows, columns):
    identity = authorize(peer)
    session = base.RootConsole(rows, columns, peer.uid)
    try:
        base.response(connection, True, dict(opened=True, identity='HOST root', reattached=False, persistent=False))
        checked = time.monotonic()
        while True:
            if time.monotonic() - checked >= 0.5:
                if authorize(peer) != identity:
                    raise PermissionError('Host console active generation changed')
                checked = time.monotonic()
            readable, _, _ = select.select((connection,), (), (), .1)
            if connection in readable:
                data = connection.recv(8192)
                if not data:
                    break
                session.write_input(data)
            data = session.take_output()
            if data:
                connection.sendall(data)
            with session.condition:
                if not session.alive and not session.output:
                    break
    finally:
        session.release(peer.uid)
        session.terminate()


def configure():
    base.SOCKET = SOCKET
    base.AUTHORIZATION = "active-environment-button"
    base.authorize_official_hub_peer = authorize
    base.issue_ticket = issue_ticket
    base.consume_ticket = consume_ticket
    base.bridge_root_console = bridge
    base.audit = audit
    # The launcher grants/revokes this endpoint to the mapped active user.
    # Never infer workload ownership from the Hub's active-session record.
    base.admit_existing_active_session = lambda: None


if __name__ == '__main__':
    configure()
    base.serve()
