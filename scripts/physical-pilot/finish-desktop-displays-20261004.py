#!/usr/bin/env python3
"""Install confirmed display choices without touching the live Hub session."""
import ast
import datetime
import fcntl
import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('foundation_deploy', REPO / 'scripts/physical-pilot/deploy-desktop-foundation-20261004.py')
deploy = importlib.util.module_from_spec(spec); spec.loader.exec_module(deploy)

with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    assert not Path('/run/apx/system-power-v1.reserved').exists()
    for name in deploy.NAMES:
        assert json.loads((deploy.BASE / name / 'registration.json').read_text())['state'] == 'stopped'
        assert not deploy.run(['/usr/bin/machinectl', 'list', '--no-legend']).count('apx-' + name + ' ')
    plan = {}
    for rel in ('local/bin/apx-settings', 'local/bin/apx-desktop-preferences-v1'):
        data = (deploy.SOURCE / rel).read_bytes(); compile(data, rel, 'exec')
        plan[deploy.SEED / rel] = data
        for name in deploy.NAMES:
            plan[deploy.BASE / name / 'home/apx/.local' / Path(rel).relative_to('local')] = data
    for target in [deploy.SEED] + [deploy.BASE / name / 'home/apx/.config' for name in deploy.NAMES]:
        path = target / 'hypr/hyprland.lua'; text = path.read_text()
        before = '{"apx-desktop-preferences.lua", "apx-shortcuts.lua"}'
        after = '{"apx-desktop-preferences.lua", "apx-shortcuts.lua", "apx-display-preferences.lua"}'
        assert text.count(before) == 1
        plan[path] = text.replace(before, after, 1).encode()
    runtime = Path('/usr/lib/apx/apx-lab-runtime.py'); text = runtime.read_text()
    begin = text.index('ENVIRONMENT_SHELL_ASSETS = {'); end = text.index('\n}', begin) + 2
    assets = ast.literal_eval(text[begin:end].split('=', 1)[1].strip())
    for rel in ('local/bin/apx-settings', 'local/bin/apx-desktop-preferences-v1', 'hypr/hyprland.lua'):
        assets[rel] = deploy.digest(plan[deploy.SEED / rel])
    text = text[:begin] + 'ENVIRONMENT_SHELL_ASSETS = {\n' + ''.join(f'    "{key}": "{value}",\n' for key, value in assets.items()) + '}' + text[end:]
    compile(text, str(runtime), 'exec'); plan[runtime] = text.encode()
    backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-desktop-displays')
    backup.mkdir(mode=0o700); deploy.write_plan(plan, backup); print(backup)
