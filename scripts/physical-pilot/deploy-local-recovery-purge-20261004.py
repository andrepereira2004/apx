#!/usr/bin/env python3
"""Install the reviewed deletion fix without replacing pilot-specific assets."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

REPO = Path(__file__).resolve().parents[2]
runtime = Path('/usr/lib/apx/apx-lab-runtime.py')
snapshots = Path('/usr/local/sbin/apx-local-snapshots')
expected = {runtime: 'afa1007be948f64eaf4c05286bd2328f152b6063e1a3052087a9c985502582e9',
            snapshots: 'febaabaac8411fadfca9d8dba10c8e0d8142223be463d1d416bf703db15a81a4'}


def main():
    if os.geteuid() != 0 or os.uname().nodename != 'apx-host':
        raise RuntimeError('audited pilot root required')
    for path, digest in expected.items():
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError('installed source changed: ' + str(path))
    if subprocess.run(['systemctl', 'is-active', '--quiet', 'apx-local-snapshots.service']).returncode == 0:
        raise RuntimeError('wait for current snapshot job to finish')
    source = (REPO / 'scripts/virtual-lab/apx-lab-runtime.py').read_text()
    text = runtime.read_text().replace('import argparse\n', 'import argparse\nimport contextlib\nimport fcntl\n', 1)
    text = text.replace('BACKUPS = STATE / "backups"', 'BACKUPS = STATE / "backups"\nLOCAL_RECOVERY = Path("/.snapshots/local-recovery")\nRECOVERY_LOCK = Path("/run/lock/apx-local-recovery.lock")', 1)
    text = text.replace('"purge-backups", "remove-home",', '"purge-backups", "purge-local-recovery", "remove-home",', 1)
    for start, end in [('def destroy(', '\ndef delete_subvolume_tree('),
                       ('def recover_unpublished(', '\ndef parser(')]:
        begin, finish = text.index(start), text.index(end, text.index(start))
        text = text[:begin] + source[source.index(start):source.index(end, source.index(start))] + text[finish:]
    helpers = source[source.index('@contextlib.contextmanager'):source.index('\ndef environment_update_rollbacks(')]
    text = text.replace('\ndef environment_update_rollbacks(', '\n' + helpers + '\ndef environment_update_rollbacks(', 1)
    compile(text, str(runtime), 'exec')
    replacements = {runtime: text.encode(), snapshots: (REPO / 'scripts/physical-pilot/apx-local-snapshots.sh').read_bytes()}
    backup = Path('/var/lib/apx/backups/20261004-local-recovery-code')
    backup.mkdir(mode=0o700)  # Exclusive: this one-shot cannot overwrite history.
    evidence = []
    for path, content in replacements.items():
        shutil.copy2(path, backup / path.name)
        temporary = path.with_name('.' + path.name + '.purge-update')
        with temporary.open('xb') as stream:
            stream.write(content); stream.flush(); os.fsync(stream.fileno())
        temporary.chmod(0o755)
        os.replace(temporary, path)
        evidence.append({'target': str(path), 'before': expected[path], 'after': hashlib.sha256(content).hexdigest()})
    (REPO / 'audit/2026-10-04-portable/deletion-deployment.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print('Deletion runtime and serialized snapshot producer installed; graphical Hub unchanged.')


if __name__ == '__main__':
    main()
