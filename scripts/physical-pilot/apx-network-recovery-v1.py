#!/usr/bin/env python3
"""Bounded recovery for failed APX veth links on the experimental physical host."""
import json
from pathlib import Path
import re
import subprocess
import time

STAMP = Path('/run/apx-network-recovery-v1/last-attempt')


def failed_links(state):
    return [link['Name'] for link in state.get('Interfaces', [])
            if re.fullmatch(r've-apx-[a-z0-9-]+', link.get('Name', ''))
            and link.get('AdministrativeState') == 'failed']


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=25)


def main():
    state = json.loads(run('/usr/bin/networkctl', 'list', '--json=short', '--no-pager').stdout)
    failed = failed_links(state)
    if not failed:
        return
    now = time.monotonic()
    if STAMP.exists() and now - float(STAMP.read_text()) < 120:
        print('Recovery cooldown active; preserving network', flush=True)
        return
    STAMP.parent.mkdir(parents=True, exist_ok=True)
    STAMP.write_text(str(now))
    print('Recovering failed APX links: ' + ', '.join(failed), flush=True)
    run('/usr/bin/systemctl', 'restart', 'systemd-networkd.service')
    # Renew all running APX clients because they share the restarted DHCP server.
    machines = run('/usr/bin/machinectl', 'list', '--no-legend', '--no-pager').stdout
    for line in machines.splitlines():
        fields = line.split()
        if len(fields) < 3:
            continue
        name, machine_class, service = fields[:3]
        if re.fullmatch(r'apx-[a-z0-9-]+', name) and machine_class == 'container' and service == 'systemd-nspawn':
            try:
                run('/usr/bin/systemd-run', '--machine=' + name, '--wait', '--pipe',
                    '--quiet', '/usr/bin/networkctl', 'renew', 'host0')
            except (subprocess.SubprocessError, OSError) as error:
                print('DHCP renewal failed for ' + name + ': ' + str(error), flush=True)


if __name__ == '__main__':
    main()
