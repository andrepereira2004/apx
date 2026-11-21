"""Execute new-Environment package transactions inside a private nspawn root."""
import time
import uuid


def install(runtime, root, packages, artifacts):
    identity = 'p' + uuid.uuid4().hex[:7]
    machine = 'apx-' + identity
    unit = 'apx-package-setup-' + identity + '.service'
    adapter = runtime.NETWORK_ADAPTER
    runtime.run([adapter, 'apply', '--environment', identity])
    try:
        command = ['systemd-run', '--unit', unit, '--collect', '--property=Delegate=yes',
                   '--property=KillMode=mixed', '--property=TimeoutStopSec=15s',
                   '--property=RuntimeMaxSec=30min', '--property=MemoryMax=4G',
                   f'--property=ExecStopPost={adapter} remove --environment {identity}', '--',
                   'systemd-nspawn', '--keep-unit', '--boot', '--settings=no', '--console=pipe',
                   '--link-journal=no', f'--machine={machine}', f'--directory={root}',
                   '--private-users=pick', '--private-users-ownership=chown',
                   '--network-veth', '--private-network', '--resolv-conf=off',
                   f'--bind={root.parent / "home"}:/home:idmap']
        if artifacts:
            command.append(f'--bind-ro={runtime.LOCAL_PACKAGE_ARTIFACTS}:/run/apx-packages')
        runtime.run(command)
        for _ in range(120):
            status = runtime.run(['systemctl', '-M', machine, 'is-system-running'], check=False, capture=True)
            if status.stdout.strip() in {'running', 'degraded'}:
                break
            time.sleep(.5)
        else:
            raise runtime.Refusal('O instalador isolado de pacotes não arrancou.')
        runtime.run(['timeout', '90s', 'systemd-run', '-M', machine, '--wait', '--pipe',
                     '--collect', '--', '/usr/lib/systemd/systemd-networkd-wait-online',
                     '--interface=host0:routable', '--ipv4', '--timeout=60'])
        prefix = ['timeout', '25m', 'systemd-run', '-M', machine, '--wait', '--pipe',
                  '--collect', '--property=RuntimeMaxSec=24min', '--', '/usr/bin/pacman']
        ignored = ['--ignore', 'nvidia-utils,lib32-nvidia-utils,opencl-nvidia'] if runtime.host_nvidia_version() else []
        runtime.run(prefix + ['-Syu', '--needed', '--noconfirm', *ignored, *packages])
        if artifacts:
            runtime.run(prefix + ['-U', '--needed', '--noconfirm',
                                  *['/run/apx-packages/' + p.name for p in artifacts]])
    finally:
        runtime.run(['systemctl', 'stop', unit], check=False, capture=True)
        status = runtime.run(['systemctl', 'is-active', unit], check=False, capture=True)
        if status.stdout.strip() not in {'inactive', 'failed', 'unknown'}:
            raise runtime.Refusal('O instalador de pacotes continua ativo.')
        runtime.run([adapter, 'remove', '--environment', identity])
