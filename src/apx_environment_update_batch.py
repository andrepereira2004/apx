"""Environment-only batch plans; the Host is never a package target."""
from __future__ import annotations
import hashlib
import json
import re

NAME = re.compile(r'[a-z](?:[a-z0-9]|-(?=[a-z0-9])){0,26}')
GENERATION = re.compile(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}')


def build_environment_plan(records: list[dict], available_bytes: int) -> dict:
    targets = []
    blockers = []
    seen = set()
    for record in sorted(records, key=lambda r: r['name']):
        name, generation = record['name'], record['generation']
        if not NAME.fullmatch(name) or not GENERATION.fullmatch(generation) or name in seen:
            raise ValueError('invalid Environment identity')
        seen.add(name)
        if record.get('role') not in ('hub', 'hub-graphical', 'graphical-base', 'development', 'minimal'):
            blockers.append(f'unsupported-environment:{name}')
        if record.get('virtual_machine', False):
            blockers.append(f'guest-update-required:{name}')
        if record['state'] != ('running' if name == 'hub' else 'stopped'):
            blockers.append(f'environment-state:{name}')
        if not record.get('package_database_ready') or not record.get('snapshot_ready'):
            blockers.append(f'environment-storage:{name}')
        targets.append({'name': name, 'generation': generation,
                        'execution': 'local-last' if name == 'hub' else 'isolated-maintenance'})
    if 'hub' not in seen:
        blockers.append('active-hub-required')
    if available_bytes < 96 * 1024**3:
        blockers.append('host-reserve-unavailable')
    value = {'schema': 1, 'scope': 'all-environments', 'targets': targets,
             'blockers': blockers, 'classification': 'blocked' if blockers else 'ready-for-approval'}
    value['plan_digest'] = hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return value
