#!/usr/bin/env python3
"""Generation-bound, single-peer LocalSend TCP opt-in for the physical pilot."""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import time
import uuid

CONFIG = Path('/var/lib/apx/localsend-network-v1/config.json')
ACTIVE = Path('/run/apx/active-graphical-environment-v1.json')
BASE = Path('/var/lib/apx/environments')
FORWARD = 'localsend_peer_forward'
NAT = 'localsend_prerouting'
TABLE = re.compile(r'apx_[a-z0-9_]+_egress_v1')
NAME = re.compile(r'[a-z][a-z0-9-]{0,26}')
INTERFACE = re.compile(r'[a-zA-Z0-9_.-]{1,15}')
PRIVATE = tuple(ipaddress.ip_network(x) for x in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'))


def run(*args: str, input_text: str | None = None) -> str:
    return subprocess.run(args, input=input_text, text=True, capture_output=True,
                          check=True, timeout=8, env={'PATH': '/usr/bin', 'LC_ALL': 'C'}).stdout


def trusted_json(path: Path) -> dict:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        info = os.fstat(fd)
        raw = os.read(fd, 32769)
    finally:
        os.close(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_gid != 0 \
            or stat.S_IMODE(info.st_mode) != 0o600 or len(raw) > 32768:
        raise ValueError('untrusted LocalSend/APX metadata')
    value = json.loads(raw)
    if type(value) is not dict:
        raise ValueError('invalid LocalSend/APX metadata')
    return value


def selection(config: dict, active: dict, record: dict) -> tuple[str, str, str]:
    if set(config) != {'schema', 'enabled', 'environment', 'generation', 'peer'} \
            or type(config['schema']) is not int or config['schema'] != 1 \
            or type(config['enabled']) is not bool:
        raise ValueError('invalid LocalSend configuration')
    name, generation, peer = (config[k] for k in ('environment', 'generation', 'peer'))
    if type(name) is not str or NAME.fullmatch(name) is None \
            or type(generation) is not str or str(uuid.UUID(generation)) != generation \
            or type(peer) is not str:
        raise ValueError('invalid LocalSend identity')
    address = ipaddress.IPv4Address(peer)
    if not any(address in net for net in PRIVATE):
        raise ValueError('LocalSend peer must be a private LAN IPv4 address')
    if (active.get('name'), active.get('generation'), active.get('role')) != (name, generation, 'graphical-base') \
            or (record.get('name'), record.get('generation'), record.get('role'), record.get('state')) \
            != (name, generation, 'graphical-base', 'running'):
        raise ValueError('LocalSend generation is not the active workload')
    short = generation.replace('-', '')[:8]
    if active.get('unit') != f'apx-graphical-{name}-{short}.service':
        raise ValueError('LocalSend active unit differs')
    return name, generation, str(address)


def validate_lan(peer: str, route: dict, interfaces: list[dict], defaults: list[dict]) -> tuple[str, str]:
    address = ipaddress.IPv4Address(peer)
    device, source = route.get('dev'), route.get('prefsrc')
    if type(device) is not str or INTERFACE.fullmatch(device) is None \
            or device.startswith(('ve-', 'veth', 'lo')) or route.get('gateway'):
        raise ValueError('LocalSend peer is not directly reachable on a physical LAN')
    ipaddress.IPv4Address(source)
    if any(row.get('gateway') == peer for row in defaults):
        raise ValueError('LocalSend peer cannot be the LAN gateway')
    local = {a['local'] for row in interfaces for a in row.get('addr_info', []) if a.get('family') == 'inet'}
    if peer in local:
        raise ValueError('LocalSend peer cannot be a Host address')
    for row in interfaces:
        if row.get('ifname') != device:
            continue
        for a in row.get('addr_info', []):
            if a.get('family') != 'inet' or a.get('local') != source:
                continue
            network = ipaddress.ip_network(f"{source}/{a['prefixlen']}", strict=False)
            if address in network and address not in {network.network_address, network.broadcast_address}:
                return device, source
    raise ValueError('LocalSend peer is outside the current LAN')


def tables() -> list[str]:
    value = json.loads(run('/usr/bin/nft', '-j', 'list', 'tables'))
    return [t['table']['name'] for t in value['nftables'] if 'table' in t
            and t['table']['family'] == 'inet' and TABLE.fullmatch(t['table']['name'])]


def table_state(table: str) -> list[dict]:
    if TABLE.fullmatch(table) is None:
        raise ValueError('invalid APX network table')
    return json.loads(run('/usr/bin/nft', '-j', 'list', 'table', 'inet', table))['nftables']


def revoke(except_table: str | None = None) -> None:
    commands = []
    for table in tables():
        if table == except_table:
            continue
        chains = {v['chain']['name'] for v in table_state(table) if 'chain' in v}
        commands.extend(f'flush chain inet {table} {chain}' for chain in (FORWARD, NAT) if chain in chains)
    if commands:
        run('/usr/bin/nft', '-f', '-', input_text='\n'.join(commands) + '\n')


def render(table: str, interface: str, uplink: str, peer: str, host: str, workload: str,
           state: list[dict]) -> str:
    if TABLE.fullmatch(table) is None or any(INTERFACE.fullmatch(x) is None for x in (interface, uplink)):
        raise ValueError('invalid network rule identity')
    for value in (peer, host, workload):
        if str(ipaddress.IPv4Address(value)) != value:
            raise ValueError('invalid network rule address')
    chains = {v['chain']['name'] for v in state if 'chain' in v}
    if 'environment_forward' not in chains:
        raise ValueError('APX network boundary is unavailable')
    commands = []
    if FORWARD not in chains:
        commands.append(f'add chain inet {table} {FORWARD}')
    if NAT not in chains:
        commands.append(f'add chain inet {table} {NAT} {{ type nat hook prerouting priority -105; policy accept; }}')
    jump = any(v.get('rule', {}).get('chain') == 'environment_forward'
               and any(e.get('jump', {}).get('target') == FORWARD for e in v['rule'].get('expr', [])) for v in state)
    if not jump:
        commands.append(f'insert rule inet {table} environment_forward jump {FORWARD} comment "APX LocalSend opt-in"')
    guard = any(v.get('rule', {}).get('chain') == 'environment_forward'
                and v['rule'].get('comment') == 'APX LocalSend receive guard' for v in state)
    if not guard:
        # Also deny packets using an old conntrack DNAT entry after revocation.
        commands.append(f'add rule inet {table} environment_forward oifname "{interface}" tcp dport 53317 drop comment "APX LocalSend receive guard"')
    commands.extend((f'flush chain inet {table} {FORWARD}', f'flush chain inet {table} {NAT}',
        f'add rule inet {table} {FORWARD} iifname "{interface}" oifname "{uplink}" ip daddr {peer} tcp dport 53317 accept',
        f'add rule inet {table} {FORWARD} iifname "{interface}" oifname "{uplink}" ip daddr {peer} tcp sport 53317 ct state established accept',
        f'add rule inet {table} {FORWARD} iifname "{uplink}" oifname "{interface}" ip saddr {peer} tcp dport 53317 accept',
        f'add rule inet {table} {NAT} iifname "{uplink}" ip saddr {peer} ip daddr {host} tcp dport 53317 dnat ip to {workload}:53317'))
    return '\n'.join(commands) + '\n'


def reconcile() -> None:
    if not CONFIG.exists():
        revoke()
        return
    config = trusted_json(CONFIG)
    if config.get('enabled') is False:
        revoke()
        return
    name = config.get('environment')
    if type(name) is not str or NAME.fullmatch(name) is None:
        raise ValueError('invalid LocalSend Environment')
    active = trusted_json(ACTIVE)
    _, generation, peer = selection(config, active, trusted_json(BASE / name / 'registration.json'))
    if run('/usr/bin/systemctl', 'show', active['unit'], '-p', 'ActiveState', '--value').strip() != 'active':
        raise ValueError('LocalSend workload unit is not active')
    network = 'g' + generation.replace('-', '')[:7]
    table, interface = f'apx_{network}_egress_v1', f've-apx-{network}'
    if table not in tables():
        raise ValueError('LocalSend workload network boundary is absent')
    leader = run('/usr/bin/machinectl', 'show', 'apx-' + network, '-p', 'Leader', '--value').strip()
    if not leader.isdigit() or int(leader) <= 1:
        raise ValueError('invalid LocalSend network leader')
    route = json.loads(run('/usr/bin/ip', '-j', '-4', 'route', 'get', peer))[0]
    interfaces = json.loads(run('/usr/bin/ip', '-j', '-4', 'address'))
    defaults = json.loads(run('/usr/bin/ip', '-j', '-4', 'route', 'show', 'default'))
    uplink, host = validate_lan(peer, route, interfaces, defaults)
    if not (Path('/sys/class/net') / uplink / 'device').exists():
        raise ValueError('LocalSend uplink is not physical')
    addresses = json.loads(run('/usr/bin/nsenter', '-t', leader, '-n', '--',
                               '/usr/bin/ip', '-j', '-4', 'address', 'show', 'host0'))
    candidates = [a['local'] for r in addresses for a in r.get('addr_info', [])
                  if a.get('family') == 'inet' and a.get('scope') == 'global'
                  and any(ipaddress.IPv4Address(a['local']) in n for n in PRIVATE)]
    if len(candidates) != 1:
        raise ValueError('LocalSend workload IPv4 is unavailable or ambiguous')
    # Recheck generation before authorizing traffic; a teardown also removes the table.
    if trusted_json(ACTIVE) != active:
        raise ValueError('LocalSend active generation changed')
    revoke(except_table=table)
    rules = render(table, interface, uplink, peer, host, candidates[0], table_state(table))
    run('/usr/bin/nft', '-c', '-f', '-', input_text=rules)
    run('/usr/bin/nft', '-f', '-', input_text=rules)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--revoke', action='store_true')
    parser.add_argument('--watch', action='store_true')
    args = parser.parse_args()
    if os.geteuid() != 0:
        raise PermissionError('LocalSend network authority requires Host root')
    if args.watch:
        stopping = False

        def stop(_signum, _frame):
            nonlocal stopping
            stopping = True

        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        try:
            while not stopping:
                try:
                    reconcile()
                except (OSError, ValueError, KeyError, IndexError, subprocess.SubprocessError) as error:
                    revoke()
                    print(f'APX LocalSend network inactive: {error}', file=sys.stderr, flush=True)
                for _ in range(10):
                    if stopping:
                        break
                    time.sleep(0.5)
        finally:
            revoke()
        return 0
    try:
        revoke() if args.revoke else reconcile()
        return 0
    except (OSError, ValueError, KeyError, IndexError, subprocess.SubprocessError) as error:
        # Invalid configuration/identity must not leave a previously authorized peer open.
        revoke()
        print(f'APX LocalSend network inactive: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
