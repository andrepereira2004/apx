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
from apx_environment_update_batch import MINIMUM_UPDATE_FREE_BYTES, build_environment_plan

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


def require_update_space():
    stat = os.statvfs(ENVIRONMENTS)
    if stat.f_bavail * stat.f_frsize < MINIMUM_UPDATE_FREE_BYTES:
        raise RuntimeError('Espaço livre abaixo de 16 GiB; atualização interrompida antes do próximo alvo.')


def latest_status():
    paths = sorted(BASE.glob('*/status.json'), reverse=True)
    if not paths: return {'state': 'idle'}
    value = read_json(paths[0])
    if value.get('state') == 'awaiting-hub':
        plan = read_json(paths[0].parent / 'plan.json')
        current = preview()
        if current['targets'] != plan['targets']:
            value.update(state='failed', error='A operação antiga pertence a outra geração dos Environments. É necessária uma nova atualização com cópias de segurança atuais.')
            atomic(paths[0], value)
    if value.get('state') == 'queued-hub' and time.time() - value.get('hub_queue_time', 0) > 30:
        unit = 'apx-environment-hub-update-' + value['operation'].lower() + '.service'
        if subprocess.run(['/usr/bin/systemctl', 'is-active', '--quiet', unit]).returncode != 0:
            value.update(state='failed', error='A etapa do Hub não arrancou; verifica os registos antes de repetir.')
            atomic(paths[0], value)
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


def runtime_assets(library=Path('/usr/lib/apx')):
    """Wrapped portable entrypoints keep the canonical pinned core separately."""
    import ast
    import stat
    path = library / 'apx-lab-runtime-core.py'
    if not path.exists(): path = library / 'apx-lab-runtime.py'
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid or info.st_gid or info.st_mode & 0o022 \
            or info.st_size > 256 * 1024:
        raise RuntimeError('Untrusted canonical runtime source')
    tree = ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'ENVIRONMENT_SHELL_ASSETS'
                                               for t in node.targets):
            assets = ast.literal_eval(node.value)
            if type(assets) is not dict: break
            return assets
    raise RuntimeError('Canonical runtime has no pinned shell asset manifest')


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


def execute(operation, *, resume_hub=False, host_digest=None):
    if OPERATION.fullmatch(operation) is None: raise RuntimeError('Invalid operation')
    directory = BASE / operation
    plan = read_json(directory / 'plan.json')
    previous = read_json(directory / 'status.json') if resume_hub else None
    if resume_hub:
        if previous.get('state') != 'queued-hub' or (host_digest is not None and not re.fullmatch(r'[0-9a-f]{64}', host_digest)):
            raise RuntimeError('No matching approved Hub completion')
        expected = {target['name'] for target in plan['targets'] if target['execution'] != 'local-last'}
        if set(previous.get('completed', [])) != expected:
            raise RuntimeError('Other Environments are not complete')
    descriptor = os.open(TRANSITION_LOCK, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    status = dict(previous) if resume_hub else {'operation': operation, 'state': 'running', 'completed': [], 'current': ''}
    if resume_hub: status.update(state='updating-hub', current='hub')
    with os.fdopen(descriptor, 'w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if POWER_RESERVATION.exists(): raise RuntimeError('Power operation pending')
            require_update_space()
            if not resume_hub and preview() != plan: raise RuntimeError('Environment plan changed; preview again')
            if resume_hub and preview()['targets'] != plan['targets']:
                raise RuntimeError('Environment generations changed; preview again')
            if plan['classification'] != 'ready-for-approval': raise RuntimeError('Plan blocked')
            # The desktop helper is installed from a root-owned, digest-pinned seed.
            st = SEED.stat()
            if SEED.is_symlink() or st.st_uid or st.st_gid or st.st_mode & 0o022:
                raise RuntimeError('Untrusted update helper')
            assets = runtime_assets()
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
                for target in (plan['targets'] if not resume_hub else [target for target in plan['targets'] if target['execution'] == 'local-last']):
                    require_update_space()
                    name = target['name']
                    for part in ('root', 'home'):
                        suffix = '-final' if resume_hub else ''
                        run(['/usr/bin/btrfs', 'subvolume', 'snapshot', '-r', str(ENVIRONMENTS / name / part), str(rollback / (name + '-' + part + suffix))])
                for target in plan['targets']:
                    if (target['execution'] == 'local-last') != resume_hub: continue
                    require_update_space()
                    name = target['name']; status['current'] = name; atomic(directory / 'status.json', status)
                    if resume_hub:
                        run(['/var/lib/apx/official-hub-v1/apx-official-hub-graphical-v1.py', '--recover'], timeout=180)
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
                    require_update_space()
            if resume_hub:
                status.update(state='return-pending', current='', message='Environments concluídos; a preparar o regresso do Hub.')
            else:
                status.update(state='awaiting-hub', current='hub', message='Os outros Environments estão atualizados. Falta atualizar o Hub nesta janela.')
            atomic(directory / 'status.json', status)
        except Exception as error:
            status.update(state='failed', error=str(error), message='A atualização parou; os resultados e cópias de segurança foram preservados.')
            atomic(directory / 'status.json', status)
            if resume_hub and read_json(ENVIRONMENTS / 'hub/registration.json').get('state') == 'stopped':
                import importlib.util
                spec = importlib.util.spec_from_file_location('apx_update_return', '/usr/lib/apx/apx-coordinated-update-runner-v1.py')
                module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
                module.schedule_hub_return(operation)
            raise
    if resume_hub:
        try:
            import importlib.util
            if host_digest is not None:
                spec = importlib.util.spec_from_file_location('apx_coordinated_update_authority', '/usr/lib/apx/apx-coordinated-update-v1.py')
                authority = importlib.util.module_from_spec(spec); spec.loader.exec_module(authority)
                result = authority.apply('apply', {'plan_digest': host_digest, 'confirmation': 'CONFIRMAR'})
                status.update(state='complete', current='', message='Environments concluídos; atualização do Host em curso.', host_operation=result['operation'])
            else:
                spec = importlib.util.spec_from_file_location('apx_update_return', '/usr/lib/apx/apx-coordinated-update-runner-v1.py')
                module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
                module.schedule_hub_return(operation)
                status.update(state='complete', current='', message='Todos os Environments foram atualizados. O Hub está a regressar.')
            atomic(directory / 'status.json', status)
        except Exception as error:
            status.update(state='failed', error=str(error), message='A etapa do Host não começou; cópias preservadas.')
            atomic(directory / 'status.json', status)
            import importlib.util
            spec = importlib.util.spec_from_file_location('apx_update_return', '/usr/lib/apx/apx-coordinated-update-runner-v1.py')
            module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
            module.schedule_hub_return(operation)
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--operation', required=True)
    parser.add_argument('--resume-hub', action='store_true'); parser.add_argument('--host-digest')
    args = parser.parse_args()
    execute(args.operation, resume_hub=args.resume_hub, host_digest=args.host_digest)
