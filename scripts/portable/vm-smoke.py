#!/usr/bin/env python3
"""Run INSIDE a disposable installed VM. Never run on an established APX Host."""
import json
from pathlib import Path
import subprocess
import sys
import time


def call(*args, check=True):
    result = subprocess.run(args, text=True, capture_output=True, timeout=180)
    if check and result.returncode:
        raise RuntimeError(f'{args}: {result.stderr[-2000:]} {result.stdout[-2000:]}')
    return result


def hub(*args):
    return call('systemd-run', '-M', 'apx-hub', '--wait', '--pipe', '--quiet', '--uid=apx', '/usr/bin/apx', *args).stdout


def main():
    if call('systemd-detect-virt').stdout.strip() not in {'kvm', 'qemu'}:
        raise RuntimeError('disposable QEMU VM required')
    if Path('/etc/hostname').read_text().strip() != 'teste-de-vm':
        raise RuntimeError('wrong VM')
    install = Path('/var/lib/apx/portable-install.json')
    if not install.exists():
        subprocess.run(['bash', '/root/apx/scripts/portable/install-apx-arch.sh', '--apply'], check=True)
    if json.loads(install.read_text())['phase'] != 'complete':
        raise RuntimeError('installation is incomplete')
    for attempt in range(90):
        # is-active with multiple units succeeds when ANY one is active.
        # Require both independently, particularly during the second boot.
        if all(call('systemctl', 'is-active', unit, check=False).returncode == 0
               for unit in ('apx-lab-executor.service', 'apx-portable-hub.service')):
            break
        time.sleep(1)
    else:
        raise RuntimeError('Hub services failed to start')
    print('APX_VM_CHECK: installer and authenticated Hub running', flush=True)
    plan = json.loads(hub('environment', 'create-plan', 'vmtest', '--role', 'minimal'))
    hub('environment', 'create', '--plan', plan['digest'], '--approve', 'CREATE vmtest AS minimal')
    hub('environment', 'start', 'vmtest')
    network = call('networkctl', 'status', 've-apx-vmtest', '--no-pager').stdout
    if '/etc/systemd/network/70-apx-portable.network' not in network:
        raise RuntimeError('workload received an unrelated network policy')
    print('APX_VM_CHECK: workload created and started by Hub', flush=True)
    # A real write inside the workload root must not appear on Host/Hub/release.
    call('systemd-run', '-M', 'apx-vmtest', '--wait', '--pipe', '--quiet',
         '/usr/bin/bash', '-c', 'echo isolated > /etc/apx-vm-smoke-marker')
    for root in (Path('/'), Path('/var/lib/apx/environments/hub/root'), Path('/var/lib/apx/releases/minimal-headless-v1/root')):
        if (root / 'etc/apx-vm-smoke-marker').exists():
            raise RuntimeError(f'workload write leaked into {root}')
    result = call('systemd-run', '-M', 'apx-vmtest', '--wait', '--pipe', '--quiet',
                  '/usr/bin/test', '!', '-S', '/run/apx/executor.sock')
    print('APX_VM_CHECK: private root and absent workload management socket', flush=True)
    # Container boot completion precedes DHCP. Wait for its own network before
    # testing a real repository transaction (never relax the network boundary).
    call('systemd-run', '-M', 'apx-vmtest', '--wait', '--pipe', '--quiet',
         '/usr/lib/systemd/systemd-networkd-wait-online', '--interface=host0', '--ipv4', '--timeout=60')
    call('systemd-run', '-M', 'apx-vmtest', '--wait', '--pipe', '--quiet',
         '/usr/bin/pacman', '-Syu', '--noconfirm', '--needed', 'ed')
    call('systemd-run', '-M', 'apx-vmtest', '--wait', '--pipe', '--quiet', '/usr/bin/pacman', '-Q', 'ed')
    if call('pacman', '-Q', 'ed', check=False).returncode == 0:
        raise RuntimeError('workload package appeared on Host')
    if call('systemd-run', '-M', 'apx-hub', '--wait', '--pipe', '--quiet', '/usr/bin/pacman', '-Q', 'ed', check=False).returncode == 0:
        raise RuntimeError('workload package appeared in Hub')
    print('APX_VM_CHECK: real package transaction isolated from Host and Hub', flush=True)
    hub('environment', 'stop', 'vmtest')
    plan = json.loads(hub('environment', 'destroy-plan', 'vmtest'))
    hub('environment', 'destroy', '--plan', plan['digest'], '--approve', 'DESTROY vmtest')
    if Path('/var/lib/apx/environments/vmtest').exists():
        raise RuntimeError('deleted workload remains')
    refused = call('bash', '/root/apx/scripts/portable/install-apx-arch.sh', '--apply', check=False)
    if refused.returncode != 2:
        raise RuntimeError('installer did not refuse existing state')
    print('APX_VM_CHECK: destroy and overwrite refusal passed', flush=True)
    print('APX_VM_SMOKE_PASS', flush=True)

if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'APX_VM_SMOKE_FAIL: {error}', flush=True)
        sys.exit(1)
