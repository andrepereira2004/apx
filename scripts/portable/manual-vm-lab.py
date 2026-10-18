#!/usr/bin/env python3
"""Owner's retained hands-on Teste lab, separate from the retired automatic run."""
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'audit/2026-10-18-portable-manual'
spec = importlib.util.spec_from_file_location('automatic_lab', Path(__file__).with_name('full-vm-lab.py'))
lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
intent = json.loads((EVIDENCE / 'intent.json').read_text())
lab.GENERATION = intent['generation']
lab.OUT = EVIDENCE / 'vm'
lab.GUARD_ENTRYPOINT = Path(__file__).resolve()
builder = Path('/var/lib/apx/test-labs/manual-' + intent['generation'])
if (builder / 'root').exists(): lab.MAINTENANCE_ROOT = builder / 'root'
lab.assert_test()
if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'prepare': lab.prepare()
    elif action == 'start': lab.start('q35')
    elif action == 'attach': lab.attach()
    elif action == 'command': print(json.dumps(lab.guest(sys.argv[2:], timeout=600), indent=2))
    elif action == 'cleanup':
        unit = Path('/etc/systemd/system/apx-manual-vm-budget.service')
        if unit.exists():
            if unit.is_symlink() or '# APX_MANUAL_GENERATION=' + lab.GENERATION not in unit.read_text():
                raise RuntimeError('manual guard ownership changed')
            lab.call('systemctl', 'disable', '--now', unit.name)
            unit.unlink()
            lab.call('systemctl', 'daemon-reload')
        lab.cleanup()
    elif action == 'guard': lab.guard()
    else: raise SystemExit('prepare | start | command | guard | cleanup')
