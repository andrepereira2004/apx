#!/usr/bin/env python3
"""Read-only residual inventory. Absence here never proves secure erasure."""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import subprocess


def command(*args):
    result = subprocess.run(args, text=True, capture_output=True)
    return {'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path, default=Path('/var/lib/apx'))
    parser.add_argument('--scan', type=Path, action='append', default=[])
    args = parser.parse_args()
    state = args.state
    live = {p.parent.name for p in (state / 'environments').glob('*/registration.json')}
    events = [json.loads(line) for line in (state / 'journal/operations.jsonl').read_text().splitlines() if line]
    deleted = sorted({e['name'] for e in events if 'name' in e and (
        e.get('action') == 'destroy' and e.get('status') == 'complete' and e.get('effect') == 'operation'
        or e.get('recovery') == 'approved-clean-unpublished' and e.get('status') == 'complete'
    )} - live)
    roots = [state / 'backups', state / 'archives', state / 'snapshots',
             state / 'native-environments', Path('/.snapshots/local-recovery'), *args.scan]
    roots = list(dict.fromkeys(roots))
    findings, errors = [], []
    # Scan backup filenames/metadata, not personal contents. Do not follow symlinks.
    for root in roots:
        if not root.exists():
            continue
        for base, directories, files in os.walk(root, followlinks=False, onerror=lambda e: errors.append(str(e))):
            directories[:] = [d for d in directories if d not in {'.git', 'proc', 'sys', 'dev', 'run', '__pycache__'}]
            for name in files + directories:
                path = Path(base) / name
                if path.is_symlink():
                    continue
                is_file = name in files
                matches = [identity for identity in deleted if re.search(r'(?<![a-z0-9])' + re.escape(identity) + r'(?![a-z0-9])', name)]
                image = is_file and (name.endswith(('.raw', '.qcow2', '.vhd', '.vhdx', '.wim', '.wim.before')))
                if not matches and not image:
                    continue
                try:
                    st = path.stat()
                    findings.append({'path': str(path), 'deleted_name_matches': matches,
                        'kind': 'disk-or-install-image' if image else 'name-match-requires-attribution',
                        'logical_bytes': st.st_size if is_file else None,
                        'allocated_bytes': st.st_blocks * 512 if is_file else None})
                except OSError as e:
                    errors.append(str(e))
    native = []
    for path in sorted((state / 'native-environments/instances-v3').glob('*.json')):
        record = json.loads(path.read_text())
        native.append({key: record.get(key) for key in ('name', 'display_name', 'state', 'generation')})
    report = {'schema': 1, 'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'live_environments': sorted(live), 'deleted_or_cleaned_names': deleted,
              'registered_native_windows': native, 'roots_scanned': [str(p) for p in roots],
              'findings': findings, 'scan_errors': errors,
              'btrfs_subvolumes': command('btrfs', 'subvolume', 'list', str(state)),
              'limits': ['Name matches require attribution before deletion.',
                         'Offline/external/cloud backups and unallocated disk sectors are not covered.',
                         'No secure-erasure claim; no files have been deleted by this tool.']}
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
