#!/usr/bin/env python3
"""Bundle only reviewed portable sources, not this machine or its credentials."""
import argparse
import hashlib
import importlib.util
import io
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('output', type=Path)
parser.add_argument('--profile', choices=('headless', 'graphical'), default='headless',
                    help='graphical is an experimental local-source candidate')
args = parser.parse_args()
filename = 'install_apx_full.py' if args.profile == 'graphical' else 'install_apx_arch.py'
spec = importlib.util.spec_from_file_location('portable_installer', Path(__file__).with_name(filename))
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)
if args.profile == 'graphical':
    installer.verify_sources()
    files = sorted(set(installer.source_files()) | {'docs/portable-full-rebuild-v1.md',
        'docs/empty-disk-install-v1.md', 'docs/empty-disk-validation-2026-10-18.md',
        'docs/install-apx-from-usb-pt.md'})
else:
    files = sorted(set(installer.SOURCES) | {
    'scripts/portable/install-apx-arch.sh', 'scripts/portable/install_apx_arch.py',
    'docs/portable-arch-base-v1.md', 'LICENSE',
    'audit/2026-10-04-portable/result.json',
    })
# Exclusive creation avoids accidentally replacing another bundle/file.
with args.output.open('xb') as output, tarfile.open(fileobj=output, mode='w:gz') as archive:
    hashes = []
    for relative in files:
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise SystemExit('unsafe bundle source: ' + relative)
        hashes.append(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + relative)
        info = archive.gettarinfo(str(path), arcname='apx-portable/' + relative)
        info.uid = info.gid = 0; info.uname = info.gname = 'root'
        info.mode = 0o755 if path.suffix == '.sh' or relative.startswith('scripts/') else 0o644
        with path.open('rb') as stream:
            archive.addfile(info, stream)
    payload = ('\n'.join(hashes) + '\n').encode()
    info = tarfile.TarInfo('apx-portable/SHA256SUMS');info.size = len(payload);info.mode = 0o644
    archive.addfile(info, io.BytesIO(payload))
print(args.output)
print('sha256=' + hashlib.sha256(args.output.read_bytes()).hexdigest())
