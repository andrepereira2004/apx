#!/usr/bin/env python3
"""Discover removable USB partitions; reuse the bounded Host file bridge."""
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

UUID = re.compile(r'(?:[0-9A-Fa-f]{16}|[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}|[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}|[0-9A-Fa-f]{8}(?:-[0-9A-Fa-f]{4}){3}-[0-9A-Fa-f]{12})')


def admitted_volumes(tree):
    result = []
    for disk in tree.get('blockdevices', []):
        if disk.get('type') != 'disk' or disk.get('tran') != 'usb' or disk.get('rm') not in (True, 1, '1'):
            continue
        children = disk.get('children', [])
        # Never claim a disk with mounted system/data partitions outside APX.
        def mounts(node):
            return [m for m in node.get('mountpoints', []) if m] + [m for c in node.get('children', []) for m in mounts(c)]
        if any(not m.startswith('/run/apx/removable-media-v1/') for m in mounts(disk)):
            continue
        for part in children:
            identity, filesystem = part.get('uuid'), part.get('fstype')
            serial = part.get('serial') or disk.get('serial')
            if part.get('type') != 'part' or filesystem not in {'vfat', 'exfat', 'ntfs'} or not isinstance(identity, str) or not UUID.fullmatch(identity):
                continue
            if not isinstance(serial, str) or not serial or len(serial) > 128:
                continue
            result.append((identity, filesystem, 'USB-' + identity, serial))
    if len(result) > 32 or len({x[0] for x in result}) != len(result):
        raise ValueError('Removable volume identities are ambiguous')
    return tuple(result)


def main():
    if os.geteuid():
        raise PermissionError('Host root required')
    path = Path(__file__).with_name('apx-removable-media-v1.py')
    spec = importlib.util.spec_from_file_location('apx_portable_media_core', path)
    core = importlib.util.module_from_spec(spec); spec.loader.exec_module(core)
    core.APPROVED_VOLUMES = ()
    core.ROOT.mkdir(parents=True, exist_ok=True)
    if core.ROOT.is_symlink() or core.ROOT.stat().st_uid != 0:
        raise ValueError('Untrusted USB bridge')
    if not os.path.ismount(core.ROOT):
        core.run('/usr/bin/mount', '--bind', str(core.ROOT), str(core.ROOT))
    core.run('/usr/bin/mount', '--make-shared', str(core.ROOT))
    def prepare():
        for _, _, name, _ in core.APPROVED_VOLUMES:
            target = core.ROOT / name
            target.mkdir(mode=0o755, exist_ok=True)
            if target.is_symlink() or target.stat().st_uid != 0:
                raise ValueError('Untrusted USB mount destination')
    core.prepare_root = prepare
    original = core.refresh
    def refresh():
        tree = json.loads(core.run('/usr/bin/lsblk', '--json', '--paths', '--output',
                          'NAME,TYPE,RM,TRAN,FSTYPE,UUID,SERIAL,MOUNTPOINTS').stdout)
        current = admitted_volumes(tree)
        # Retain disconnected identities long enough for safe unmount/cleanup.
        known = {item[0]: item for item in core.APPROVED_VOLUMES}
        known.update({item[0]: item for item in current})
        core.APPROVED_VOLUMES = tuple(known.values())
        original()
        current_ids = {item[0] for item in current}
        core.APPROVED_VOLUMES = tuple(item for item in core.APPROVED_VOLUMES
                                     if item[0] in current_ids or core.mounted_source(core.ROOT / item[2]) is not None)
        inventory = {uuid: {'name': name, 'label': 'USB ' + uuid} for uuid, _, name, _ in core.APPROVED_VOLUMES}
        temporary = core.ROOT / '.volumes.json.tmp'
        temporary.write_text(json.dumps(inventory) + '\n'); temporary.chmod(0o644)
        os.replace(temporary, core.ROOT / 'volumes.json')
    core.refresh = refresh
    core.watch()


if __name__ == '__main__':
    main()
