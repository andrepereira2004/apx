#!/usr/bin/python
"""Stop only the retained manual guest if the unchanged Host reserve is approached."""
import json
import os
from pathlib import Path
import shutil
import signal
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'audit/2026-10-18-portable-manual'
intent = json.loads((OUT / 'intent.json').read_text())
REGISTRATION = Path('/var/lib/apx/environments/teste/registration.json')
prefix = '/system.slice/apx-graphical-teste-' + intent['generation'].split('-')[0] + '.service'
if os.geteuid(): raise SystemExit('Host root only')
while REGISTRATION.exists():
    metadata = REGISTRATION.lstat()
    if REGISTRATION.is_symlink() or metadata.st_uid or metadata.st_gid or metadata.st_mode & 0o022:
        raise SystemExit('untrusted Teste registration')
    if json.loads(REGISTRATION.read_text()).get('generation') != intent['generation']:
        raise SystemExit('Teste generation changed')
    if shutil.disk_usage('/').free < 97 * 1024**3:
        stopped = []
        for process in Path('/proc').iterdir():
            if not process.name.isdecimal(): continue
            try:
                group = (process / 'cgroup').read_text().strip().split(':', 2)[-1]
                args = (process / 'cmdline').read_bytes().split(b'\0')
                if not (group == prefix or group.startswith(prefix + '/')): continue
                if b'/home/apx/VMs/APX-Rebuild/disk.raw' not in b'\0'.join(args): continue
                if (process / 'comm').read_text().strip() != 'qemu-system-x86': continue
                os.kill(int(process.name), signal.SIGTERM); stopped.append(int(process.name))
            except (OSError, ProcessLookupError): continue
        if stopped:
            (OUT / 'manual-space-stop.json').write_text(json.dumps({'free_bytes':shutil.disk_usage('/').free,'stopped_vm_pids':stopped})+'\n')
    time.sleep(2)
