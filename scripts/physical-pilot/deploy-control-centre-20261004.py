#!/usr/bin/env python3
"""Owner-approved Control Centre repair on the identity-matched APX pilot."""
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / 'config/environment-shell-v1'
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')
NAMES = ('hub', 'faculdade', 'hytale', 'minecraft', 'steam')
BEFORE = {
    'seed': '18aafa659ff5a5096cef496873aed54da2e4042ebf721f52253e43d7425fc8c8',
    'hub': 'e5904b5061de3e020093fb1a364b2daffaa86969c64ef06d2b9bede8af837c2a',
    'workload': '1068699ce64319cb6b54ff99b87da9bcf4c228b560d603604ef14e266eac9671',
}
LOADER = b'''\n-- Persisted external-mouse choices from the Control Centre override the base.
local mouseChoice = "/home/apx/.config/hypr/apx-mouse-sensitivity.lua"
local mouseChoiceFile = io.open(mouseChoice, "r")
if mouseChoiceFile then
    mouseChoiceFile:close()
    dofile(mouseChoice)
end
'''


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    assert os.geteuid() == 0
    assert tuple(Path(p).read_text().strip() for p in (
        '/etc/hostname', '/sys/class/dmi/id/product_name', '/sys/class/dmi/id/board_name'
    )) == ('apx-host', '82JU', 'LNVNB161216')
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert not Path('/run/apx/system-power-v1.reserved').exists()
        homes = {name: Path(f'/var/lib/apx/environments/{name}/home/apx') for name in NAMES}
        for name in NAMES:
            registration = json.loads(Path(f'/var/lib/apx/environments/{name}/registration.json').read_text())
            assert registration['state'] in ('running', 'stopped')
        plan = {}
        pinned = {}
        targets = {'seed': SEED / 'quickshell/apx/shell.qml'}
        targets.update({name: home / '.config/quickshell/apx/shell.qml' for name, home in homes.items()})
        with tempfile.TemporaryDirectory(prefix='apx-control-stage-') as directory:
            for name, target in targets.items():
                assert target.is_file() and not target.is_symlink()
                before = target.read_bytes()
                assert digest(before) == BEFORE.get(name, BEFORE['workload']), name
                temporary = Path(directory) / name
                temporary.write_bytes(before)
                patch = REPO / f'scripts/physical-pilot/control-centre-20261004-patches/{name}.diff'
                subprocess.run(['patch', '--batch', '--fuzz=0', str(temporary), str(patch)],
                               check=True, capture_output=True)
                plan[target] = temporary.read_bytes()
                if name == 'seed': pinned['quickshell/apx/shell.qml'] = plan[target]
        for relative in ('local/bin/apx-mouse-sensitivity-v1', 'local/bin/apx-environment-update-v1'):
            content = (SOURCE / relative).read_bytes()
            pinned[relative] = content
            plan[SEED / relative] = content
            for home in homes.values(): plan[home / '.local/bin' / Path(relative).name] = content
        # Hub already calls this catalogue from its bar, but its helper was absent.
        plan[homes['hub'] / '.local/bin/apx-window-apps-v1'] = (SOURCE / 'local/bin/apx-window-apps-v1').read_bytes()
        hypr_targets = [SEED / 'hypr/hyprland.lua'] + [home / '.config/hypr/hyprland.lua' for home in homes.values()]
        for target in hypr_targets:
            before = target.read_bytes()
            assert b'apx-mouse-sensitivity.lua' not in before
            plan[target] = before + LOADER
        pinned['hypr/hyprland.lua'] = plan[hypr_targets[0]]
        host = {
            '/usr/lib/apx/apx-host-services-v3.py': 'scripts/physical-pilot/apx-host-services-v3.py',
            '/usr/lib/apx/apx-host-services-client-v3.py': 'scripts/physical-pilot/apx-host-services-client-v3.py',
            '/usr/lib/apx/apx_host_services_v3_contract.py': 'src/apx_host_services_v3_contract.py',
            '/usr/lib/apx/apx-coordinated-update-client-v1.py': 'scripts/physical-pilot/apx-coordinated-update-client-v1.py',
            '/etc/systemd/system/apx-host-services-v3.service': 'config/systemd/apx-host-services-v3.service',
        }
        for target, source in host.items(): plan[Path(target)] = (REPO / source).read_bytes()
        runtime = Path('/usr/lib/apx/apx-lab-runtime.py')
        runtime_text = runtime.read_text()
        for relative, content in pinned.items():
            pattern = r'(?m)^    "' + re.escape(relative) + r'": "[0-9a-f]{64}",$'
            replacement = f'    "{relative}": "{digest(content)}",'
            runtime_text, count = re.subn(pattern, lambda _: replacement, runtime_text)
            if count == 0 and relative == 'local/bin/apx-mouse-sensitivity-v1':
                marker = '    "local/bin/apx-laptop-action-v1":'
                lines = runtime_text.splitlines(keepends=True)
                index = next(i for i, line in enumerate(lines) if line.startswith(marker))
                lines.insert(index + 1, replacement + '\n')
                runtime_text = ''.join(lines)
            else: assert count == 1, relative
        plan[runtime] = runtime_text.encode()
        compile(runtime_text, str(runtime), 'exec')
        for target, content in plan.items():
            assert target.parent.is_dir() and not target.is_symlink(), target
            if target.suffix == '.py' or target.name in ('apx-mouse-sensitivity-v1', 'apx-window-apps-v1', 'apx-environment-update-v1'):
                compile(content, str(target), 'exec')
        backup = Path('/var/lib/apx/backups') / (
            datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-control-centre-all-environments')
        backup.mkdir(mode=0o700)
        entries = []
        for index, (target, content) in enumerate(plan.items()):
            previous = target.read_bytes() if target.exists() else None
            metadata = target.stat() if previous is not None else target.parent.stat()
            mode = metadata.st_mode & 0o777 if previous is not None else 0o755
            saved = backup / str(index)
            if previous is not None: shutil.copy2(target, saved)
            entries.append({'target': str(target), 'backup': str(saved) if previous is not None else None,
                            'before': digest(previous) if previous is not None else None,
                            'after': digest(content), 'uid': metadata.st_uid, 'gid': metadata.st_gid, 'mode': mode})
        (backup / 'manifest.json').write_text(json.dumps(entries, indent=2) + '\n')
        for (target, content), entry in zip(plan.items(), entries):
            fd, temporary = tempfile.mkstemp(prefix='.apx-control-centre-', dir=target.parent)
            try:
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(content); stream.flush(); os.fsync(stream.fileno())
                os.chown(temporary, entry['uid'], entry['gid']); os.chmod(temporary, entry['mode'])
                os.replace(temporary, target)
            finally:
                if os.path.exists(temporary): os.unlink(temporary)
            assert digest(target.read_bytes()) == entry['after']
        print(backup)


if __name__ == '__main__':
    main()
