#!/usr/bin/python3
"""Generation-bound maintenance updates of stopped Environments, then local Hub."""
from __future__ import annotations
import argparse
import fcntl
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

sys.path.insert(0, '/usr/lib/apx')
from apx_environment_update_batch import build_environment_plan

BASE = Path('/var/lib/apx/environment-updates-v1')
ENVIRONMENTS = Path('/var/lib/apx/environments')
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1/local/bin/apx-environment-update-v1')
OPERATION = re.compile(r'[0-9]{8}T[0-9]{6}Z-[0-9a-f]{12}')
TRANSITION_LOCK = Path('/run/apx/machine-transition-v1.lock')
POWER_RESERVATION = Path('/run/apx/system-power-v1.reserved')


def read_json(path):
    st = path.lstat()
    if path.is_symlink() or not path.is_file() or st.st_uid or st.st_gid or st.st_mode & 0o022:
        raise RuntimeError('Untrusted operation or registration')
    return json.loads(path.read_text())


def atomic(path, value):
    tmp = path.with_name('.' + path.name + '.tmp')
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(value, stream); stream.flush(); os.fsync(stream.fileno())
    os.replace(tmp, path)


def inventory():
    records = []
    for directory in sorted(ENVIRONMENTS.iterdir()):
        if not (directory / 'registration.json').exists(): continue
        if directory.is_symlink(): raise RuntimeError('Environment directory is a symlink')
        record = read_json(directory / 'registration.json')
        if record.get('name') != directory.name: raise RuntimeError('Environment name differs')
        for part in ('root', 'home'):
            if (directory / part).is_symlink(): raise RuntimeError('Environment volume is a symlink')
        record['package_database_ready'] = (directory / 'root/var/lib/pacman/local').is_dir()
        record['snapshot_ready'] = all(subprocess.run(
            ['/usr/bin/btrfs', 'subvolume', 'show', str(directory / part)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0 for part in ('root', 'home'))
        record['virtual_machine'] = (directory / 'virtual-machine-v1').exists()
        records.append(record)
    return records


def preview():
    stat = os.statvfs(ENVIRONMENTS)
    return build_environment_plan(inventory(), stat.f_bavail * stat.f_frsize)


def latest_status():
    paths = sorted(BASE.glob('*/status.json'), reverse=True)
    if not paths: return {'state': 'idle'}
    value = read_json(paths[0])
    if value.get('state') in ('queued', 'running'):
        operation = value.get('operation', '')
        if OPERATION.fullmatch(operation) is None: raise RuntimeError('Invalid status operation')
        created = datetime.datetime.strptime(operation[:16], '%Y%m%dT%H%M%SZ').replace(tzinfo=datetime.timezone.utc).timestamp()
        if time.time() - created > 10:
            unit = 'apx-environment-update-' + operation.lower() + '.service'
            active = subprocess.run(['/usr/bin/systemctl', 'is-active', '--quiet', unit]).returncode == 0
            if not active:
                value.update(state='failed', error='A execução foi interrompida; verifica os registos antes de repetir.')
                atomic(paths[0], value)
    return value


def maintenance_command(target, operation_dir):
    name = target['name']
    # Distinct from normal graphical identities; fits Linux's interface limit.
    identity = 'u' + hashlib.sha256((name + target['generation']).encode()).hexdigest()[:7]
    machine = 'apx-' + identity
    unit = 'apx-update-maintenance-' + identity
    directory = ENVIRONMENTS / name
    command = ['/usr/bin/systemd-run', '--unit=' + unit, '--collect',
               '--property=Delegate=yes', '--property=KillMode=mixed',
               '--property=CPUQuota=400%', '--property=MemoryMax=8G', '--property=TasksMax=2048',
               '/usr/bin/systemd-nspawn', '--quiet', '--keep-unit', '--boot',
               '--machine=' + machine, '--directory=' + str(directory / 'root'),
               '--private-users=pick', '--private-users-ownership=chown',
               '--private-network', '--network-veth', '--settings=no', '--link-journal=no', '--resolv-conf=off',
               '--bind=' + str(directory / 'home') + ':/home:idmap',
               '--bind-ro=' + str(SEED) + ':/run/apx-maintenance-update',
               '--bind-ro=' + str(operation_dir / 'sudoers') + ':/etc/sudoers.d:idmap',
               'systemd.unit=multi-user.target']
    return identity, machine, unit + '.service', command


def execute(operation):
    if OPERATION.fullmatch(operation) is None: raise RuntimeError('Invalid operation')
    directory = BASE / operation
    plan = read_json(directory / 'plan.json')
    descriptor = os.open(TRANSITION_LOCK, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    status = {'operation': operation, 'state': 'running', 'completed': [], 'current': ''}
    with os.fdopen(descriptor, 'w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if POWER_RESERVATION.exists(): raise RuntimeError('Power operation pending')
            if preview() != plan: raise RuntimeError('Environment plan changed; preview again')
            if plan['classification'] != 'ready-for-approval': raise RuntimeError('Plan blocked')
            # The desktop helper is installed from a root-owned, digest-pinned seed.
            st = SEED.stat()
            if SEED.is_symlink() or st.st_uid or st.st_gid or st.st_mode & 0o022:
                raise RuntimeError('Untrusted update helper')
            import ast
            tree = ast.parse(Path('/usr/lib/apx/apx-lab-runtime.py').read_text())
            assets = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                          and any(isinstance(t, ast.Name) and t.id == 'ENVIRONMENT_SHELL_ASSETS' for t in n.targets))
            if hashlib.sha256(SEED.read_bytes()).hexdigest() != assets['local/bin/apx-environment-update-v1']:
                raise RuntimeError('Update helper digest differs')
            sudoers = directory / 'sudoers'; sudoers.mkdir(mode=0o755); os.chmod(sudoers, 0o755)
            policy = sudoers / 'apx-update'; policy.write_text('apx ALL=(root) NOPASSWD: /usr/bin/pacman, /usr/bin/flatpak\n')
            os.chmod(policy, 0o440)
            rollback = directory / 'rollback'; rollback.mkdir(mode=0o700)
            atomic(directory / 'status.json', status)
            with (directory / 'update.log').open('a') as log:
                def run(args, timeout=120):
                    return subprocess.run(args, stdout=log, stderr=log, check=True, timeout=timeout)
                # Every target, including the still-active Hub, gets its own copy.
                for target in plan['targets']:
                    name = target['name']
                    for part in ('root', 'home'):
                        run(['/usr/bin/btrfs', 'subvolume', 'snapshot', '-r', str(ENVIRONMENTS / name / part), str(rollback / (name + '-' + part))])
                for target in plan['targets']:
                    if target['execution'] == 'local-last': continue
                    name = target['name']; status['current'] = name; atomic(directory / 'status.json', status)
                    record = read_json(ENVIRONMENTS / name / 'registration.json')
                    if record['generation'] != target['generation'] or record['state'] != 'stopped':
                        raise RuntimeError('Target generation or state changed')
                    identity, machine, unit, command = maintenance_command(target, directory)
                    network = ['/usr/lib/apx/apx-environment-network-v1.py']
                    # Reject a leftover unit/machine rather than claiming or stopping it.
                    for probe in (['/usr/bin/systemctl', 'is-active', '--quiet', unit], ['/usr/bin/machinectl', 'show', machine]):
                        if subprocess.run(probe, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                            raise RuntimeError('Maintenance identity already exists')
                    owned_unit = False
                    run(network + ['apply', '--environment', identity])
                    try:
                        run(command); owned_unit = True
                        for attempt in range(90):
                            ready = subprocess.run(['/usr/bin/systemd-run', '-M', machine, '--wait', '--pipe', '--quiet',
                                                    '/usr/bin/test', '-e', '/run/systemd/system'], stdout=log, stderr=log)
                            if ready.returncode == 0: break
                            time.sleep(1)
                        else: raise RuntimeError('Maintenance boot timed out')
                        run(['/usr/bin/systemd-run', '-M', machine, '--wait', '--pipe', '--quiet',
                             '/usr/bin/systemctl', 'start', 'systemd-resolved.service'])
                        run(['/usr/bin/systemd-run', '-M', machine, '--wait', '--pipe', '--quiet',
                             '--property=TimeoutStartSec=60', '/usr/lib/systemd/systemd-networkd-wait-online', '--interface=host0:routable', '--ipv4', '--timeout=60'])
                        run(['/usr/bin/systemd-run', '-M', machine, '--wait', '--pipe', '--quiet',
                             '/usr/bin/install', '-d', '-o', 'apx', '-g', 'apx', '-m', '0700', '/run/user/1000'])
                        run(['/usr/bin/systemd-run', '-M', machine, '--uid=apx', '--wait', '--pipe', '--quiet',
                             '--setenv=HOME=/home/apx', '--setenv=XDG_RUNTIME_DIR=/run/user/1000',
                             '--property=TimeoutStartSec=infinity', '/usr/bin/dbus-run-session', '--', '/usr/bin/python3', '/run/apx-maintenance-update', '--unattended'], timeout=14400)
                    finally:
                        if owned_unit: run(['/usr/bin/systemctl', 'stop', unit])
                        # Never dismantle egress while an update container survived cleanup.
                        if subprocess.run(['/usr/bin/machinectl', 'show', machine], stdout=log, stderr=log).returncode == 0:
                            raise RuntimeError('Maintenance container did not stop')
                        run(network + ['remove', '--environment', identity])
                    status['completed'].append(name); atomic(directory / 'status.json', status)
            status.update(state='awaiting-hub', current='hub', message='Os outros Environments estão atualizados. Falta atualizar o Hub nesta janela.')
            atomic(directory / 'status.json', status)
        except Exception as error:
            status.update(state='failed', error=str(error), message='A atualização parou; os resultados e cópias de segurança foram preservados.')
            atomic(directory / 'status.json', status)
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--operation', required=True)
    execute(parser.parse_args().operation)
