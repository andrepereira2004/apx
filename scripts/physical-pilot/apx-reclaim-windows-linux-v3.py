#!/usr/bin/env python3
"""Local-console completion of an owner-requested secondary Windows deletion.

Experimental, exact Lenovo pilot only. --preview is read-only. Applying requires
a real terminal and the existing LUKS password; secrets never enter argv/logs.
No restart is performed. Recovery is resumable through the same command.
"""
import argparse
import fcntl
import getpass
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from uuid import uuid4

sys.path.insert(0, '/usr/lib/apx')
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'src'))
from apx_native_instances_v3 import canonical_layout
from apx_native_linux_reclaim_v3 import (plan_reclaim, validate_reclaim, kernel_cmdline,
                                        crypttab, SYSROOT_DEPENDENCY, validate_storage_health)

ROOT = Path('/var/lib/apx/native-environments')
DISK = '/dev/nvme0n1'
PENDING = ROOT/'pending-v3.json'
TRANSACTION = ROOT/'linux-reclaim-v3'
MAPPER = '/dev/mapper/cryptreclaimed'
DROPIN = Path('/etc/systemd/system/sysroot.mount.d/apx-reclaimed.conf')
CONFIGS = [Path('/etc/mkinitcpio.conf'), Path('/etc/kernel/cmdline'),
           Path('/etc/crypttab.initramfs'), Path('/etc/crypttab'), DROPIN]
IMAGES = [Path('/boot/EFI/APX')/name for name in
          ('apx-system-v1.efi', 'apx-nouveau-recovery-v1.efi', 'apx-iommu-audit-v1.efi')]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(*args, input=None, timeout=1800):
    result = subprocess.run(args, input=input, capture_output=True, timeout=timeout,
                            env={'PATH': '/usr/bin', 'LC_ALL': 'C'})
    if result.returncode:
        # Never include input or arbitrary command output in lifecycle metadata.
        raise RuntimeError('Falhou '+Path(args[0]).name+' (código '+str(result.returncode)+').')
    return result.stdout


def load_lifecycle():
    path = Path(__file__).with_name('apx-native-lifecycle-v3.py')
    spec = importlib.util.spec_from_file_location('reclaim_lifecycle', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def table():
    return canonical_layout(json.loads(run('sfdisk', '--json', DISK))['partitiontable'])


def gpt_script(layout):
    lines = ['label: gpt', 'label-id: '+layout['id'], 'device: '+DISK,
             'unit: sectors', 'first-lba: '+str(layout['firstlba']),
             'last-lba: '+str(layout['lastlba']), 'sector-size: 512', '']
    for p in layout['partitions']:
        require(set(p) <= {'node', 'start', 'size', 'type', 'uuid', 'name'},
                'Atributos GPT adicionais precisam de revisão.')
        require('"' not in p.get('name', '') and '\n' not in p.get('name', ''), 'Nome GPT inválido.')
        lines.append(f'{p["node"]} : start={p["start"]}, size={p["size"]}, type={p["type"]}, '
                     f'uuid={p["uuid"]}, name="{p.get("name", "")}"')
    return ('\n'.join(lines)+'\n').encode()


def is_member():
    output = run('btrfs', 'filesystem', 'show', '--raw', '/').decode()
    return any(line.split()[-1:] == [MAPPER] for line in output.splitlines())


def atomic(path, data, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.apx-reclaim-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            os.fchmod(stream.fileno(), mode); stream.write(data); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
        fd = os.open(path.parent, os.O_DIRECTORY)
        try: os.fsync(fd)
        finally: os.close(fd)
    finally:
        Path(temporary).unlink(missing_ok=True)


def extract(image, section, destination):
    # objcopy rewrites its input when OUTPUT is omitted, even with --dump-section.
    # A disposable, explicit output is essential for signed PE images.
    with tempfile.TemporaryDirectory(prefix='.pe-inspect-',dir=destination.parent) as scratch:
        run('objcopy', '--dump-section', section+'='+str(destination), str(image),
            str(Path(scratch)/'discard.efi'))
    return destination.read_bytes().rstrip(b'\0')


def prepare_boot(plan, work):
    """Build and verify all three signed boot images before changing the GPT."""
    backup = work/'backup'
    if not (work/'backed-up.json').exists():
        files = CONFIGS + IMAGES + [Path('/boot/initramfs-linux.img')]
        existed = []
        for path in files:
            if path.exists():
                require(path.is_file() and not path.is_symlink(), 'Ficheiro de arranque inesperado.')
                target = backup/str(path).lstrip('/'); target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target); existed.append(str(path))
        atomic(work/'backed-up.json', json.dumps(existed).encode())
    baseline = lambda path: (backup/str(path).lstrip('/')).read_bytes()
    root_uuid = run('cryptsetup', 'luksUUID', DISK+'p2').decode().strip()
    old_crypttab = backup/'etc/crypttab.initramfs'
    initrd_tab = crypttab(old_crypttab.read_text() if old_crypttab.exists() else '', root_uuid, plan['luks_uuid'])
    # The persistent crypttab is also required for orderly shutdown of both devices.
    persistent = baseline(Path('/etc/crypttab')).decode()
    require('cryptreclaimed' not in persistent, 'crypttab já contém o novo volume.')
    atomic(Path('/etc/crypttab'), (persistent+'\n'+initrd_tab.splitlines()[1]+'\n').encode())
    atomic(Path('/etc/crypttab.initramfs'), initrd_tab.encode())
    atomic(DROPIN, SYSROOT_DEPENDENCY.encode(), 0o644)
    config = baseline(Path('/etc/mkinitcpio.conf')).decode()
    config += '\n# APX: wait for both encrypted root members.\nFILES+=(/etc/systemd/system/sysroot.mount.d/apx-reclaimed.conf)\n'
    atomic(Path('/etc/mkinitcpio.conf'), config.encode(), 0o644)
    atomic(Path('/etc/kernel/cmdline'), kernel_cmdline(baseline(Path('/etc/kernel/cmdline')).decode(), plan['luks_uuid']).encode())
    run('mkinitcpio', '--nopost', '-c', '/etc/mkinitcpio.conf', '-k', os.uname().release,
        '-g', str(work/'initramfs.img'))
    listing = run('lsinitcpio', str(work/'initramfs.img')).decode()
    require('etc/crypttab' in listing and 'sysroot.mount.d/apx-reclaimed.conf' in listing,
            'O initramfs não inclui o desbloqueio adicional.')
    kernel_hash = hashlib.sha256(Path('/boot/vmlinuz-linux').read_bytes()).hexdigest()
    for image in IMAGES:
        old = backup/str(image).lstrip('/')
        extract(old, '.linux', work/'old-kernel')
        embedded = (work/'old-kernel').read_bytes()
        require(hashlib.sha256(embedded).hexdigest() == kernel_hash, 'Kernel de recuperação diferente.')
        old_cmdline = extract(old, '.cmdline', work/'old-cmdline').decode()
        cmdline = work/(image.stem+'.cmdline')
        cmdline.write_text(kernel_cmdline(old_cmdline, plan['luks_uuid']))
        output = work/image.name
        initramfs = work/'initramfs.img'
        if image.name == 'apx-nouveau-recovery-v1.efi':
            # Preserve the independent open-driver recovery option.
            recovery_config = work/'nouveau-mkinitcpio.conf'
            recovery_config.write_text(config+'\nMODULES=(amdgpu nouveau)\n')
            initramfs = work/'nouveau-initramfs.img'
            run('mkinitcpio','--nopost','-c',str(recovery_config),'-k',os.uname().release,
                '-g',str(initramfs))
        run('ukify', '--config=/etc/kernel/uki.conf', 'build', '--linux=/boot/vmlinuz-linux',
            '--initrd='+str(initramfs), '--cmdline=@'+str(cmdline),
            '--uname='+os.uname().release, '--output='+str(output))
        run('sbverify', '--cert', '/etc/kernel/secure-boot-certificate.pem', str(output))
        actual = extract(output, '.cmdline', work/'new-cmdline').decode()
        require(actual.strip() == cmdline.read_text().strip(), 'Linha de arranque gerada diferente.')
    (work/'old-kernel').unlink(missing_ok=True)
    (work/'old-cmdline').unlink(missing_ok=True)
    (work/'new-cmdline').unlink(missing_ok=True)


def restore_configs(work):
    existed = json.loads((work/'backed-up.json').read_bytes())
    for path in CONFIGS:
        if str(path) in existed:
            original = work/'backup'/str(path).lstrip('/')
            atomic(path, original.read_bytes(), original.stat().st_mode & 0o777)
        else:
            path.unlink(missing_ok=True)


def install_boot(work):
    # One atomic replacement at a time; never need room for three extra UKIs on ESP.
    for path in IMAGES + [Path('/boot/initramfs-linux.img')]:
        source = work/('initramfs.img' if path.name == 'initramfs-linux.img' else path.name)
        if path in IMAGES:
            run('sbverify','--cert','/etc/kernel/secure-boot-certificate.pem',str(source))
        require(shutil.disk_usage(path.parent).free > source.stat().st_size+8*1024**2,
                'A partição EFI não tem espaço para uma substituição atómica.')
        atomic(path, source.read_bytes())
        require(hashlib.sha256(path.read_bytes()).digest() == hashlib.sha256(source.read_bytes()).digest(),
                'A imagem instalada difere da imagem verificada.')
        if path in IMAGES:
            run('sbverify','--cert','/etc/kernel/secure-boot-certificate.pem',str(path))


def finish(lifecycle, plan, work):
    receipt = dict(plan, state='integrated', filesystem_uuid=run('findmnt','-no','UUID','/').decode().strip())
    lifecycle.write(ROOT/'linux-storage-v3.json', receipt)
    # Remove only the obsolete reuse authority and icon for this exact generation.
    (ROOT/'free-slot-v3.json').unlink(missing_ok=True)
    icon = Path('/var/lib/apx/environments')/('.icon-'+plan['target']+'-'+plan['generation']+'.json')
    icon.unlink(missing_ok=True)
    if PENDING.exists():
        current = lifecycle.trusted(PENDING)
        require(current.get('generation') == plan['generation'], 'Operação pendente diferente.')
        PENDING.unlink()
    lifecycle.state(plan, 'complete', 100, 'Windows apagado. O espaço foi integrado no Linux atual.')
    atomic(work/'complete.json', json.dumps(receipt).encode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generation', required=True)
    parser.add_argument('--preview', action='store_true')
    args = parser.parse_args()
    require(str(__import__('uuid').UUID(args.generation)) == args.generation, 'Geração inválida.')
    lifecycle = load_lifecycle(); lifecycle.target()
    if not args.preview:
        require(sys.stdin.isatty() and sys.stderr.isatty(), 'Executa este comando num terminal local; não envies a palavra-passe pelo chat.')
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        require(not Path('/run/apx/environment-management-v1.lock').exists(), 'Existe outra operação APX em curso.')
        if PENDING.exists():
            pending = lifecycle.trusted(PENDING)
            require(pending.get('generation') == args.generation and pending.get('stage') == 'awaiting-linux-auth',
                    'Existe outra operação Windows pendente.')
        work = TRANSACTION/args.generation
        if (work/'plan.json').exists():
            plan = validate_reclaim(lifecycle.trusted(work/'plan.json'))
        else:
            marker = lifecycle.trusted(ROOT/'free-slot-v3.json')
            retired_paths = list((ROOT/'retired-v3').glob('*-'+args.generation+'.json'))
            require(len(retired_paths) == 1, 'Não existe um único Windows retirado com esta geração.')
            retired = lifecycle.trusted(retired_paths[0])
            original = lifecycle.trusted(ROOT/'instances-v3/windows.json')
            plan = plan_reclaim(table(), marker, retired, original, str(uuid4()))
        require(plan['generation'] == args.generation, 'Plano de outra geração.')
        current = table()
        require(current in (plan['before'], plan['after']), 'A tabela de partições mudou.')
        if args.preview:
            print(json.dumps(plan, indent=2, ensure_ascii=False)); return
        require(run('findmnt','-no','FSTYPE','/').decode().strip() == 'btrfs', 'O Linux atual não é Btrfs.')
        require(run('findmnt','-no','SOURCE','/').decode().strip().split('[')[0] == '/dev/mapper/cryptroot',
                'O dispositivo raiz não corresponde ao piloto.')
        health_path = ROOT/'linux-reclaim-health-v3.json'
        health = lifecycle.trusted(health_path) if health_path.exists() else None
        if health is not None:
            scrub = run('btrfs','scrub','status','-R','/')
            if hashlib.sha256(scrub).hexdigest() != health.get('scrub_status_sha256'):
                health = None
        stats = json.loads(run('btrfs','--format','json','device','stats','/'))
        filesystem_uuid = run('findmnt','-no','UUID','/').decode().strip()
        validate_storage_health(stats,health,filesystem_uuid,time.time())
        # Validate the existing password without opening/altering the current root.
        secret = getpass.getpass('Palavra-passe de cifragem do Linux (não é guardada): ').encode()
        require(bool(secret), 'Palavra-passe vazia.')
        run('cryptsetup', 'open', '--test-passphrase', '--key-file=-', DISK+'p2', input=secret)
        work.mkdir(parents=True, exist_ok=True, mode=0o700)
        lifecycle.write(work/'plan.json', plan)
        for n in (5, 6, 7):
            node = DISK+'p'+str(n)
            holders = Path('/sys/class/block', Path(node).name, 'holders')
            active = list(holders.iterdir()) if holders.exists() else []
            if active:
                require(n == 5 and current == plan['after'] and len(active) == 1 and
                        (active[0]/'dm/name').read_text().strip() == 'cryptreclaimed', 'O espaço está em uso.')
            found = subprocess.run(['findmnt', '-rn', '-S', node], capture_output=True)
            require(found.returncode == 1, 'Uma partição selecionada está montada.')
        try:
            print('A preparar e verificar o arranque cifrado e as opções de recuperação…', flush=True)
            prepare_boot(plan, work)
            if current == plan['before']:
                # Exact compare again immediately before writing the partition table.
                require(table() == plan['before'], 'A tabela mudou durante a preparação.')
                run('sfdisk', '--no-reread', '--no-tell-kernel', DISK, input=gpt_script(plan['after']))
                run('partx', '--delete', '--nr', '6:7', DISK)
                run('partx', '--update', '--nr', '5', DISK)
                run('udevadm', 'settle')
            require(table() == plan['after'], 'A tabela final não corresponde ao plano.')
            identity = subprocess.run(['cryptsetup', 'luksUUID', DISK+'p5'], capture_output=True)
            if identity.returncode != 0:
                require(not (work/'formatted.json').exists(), 'Cabeçalho cifrado ausente após formatação.')
                run('cryptsetup', 'luksFormat', '--batch-mode', '--type=luks2', '--uuid='+plan['luks_uuid'],
                    '--key-file=-', DISK+'p5', input=secret)
            else:
                require(identity.stdout.decode().strip() == plan['luks_uuid'], 'O volume cifrado pertence a outro plano.')
            lifecycle.write(work/'formatted.json', {'luks_uuid': plan['luks_uuid']})
            if not Path(MAPPER).exists():
                run('cryptsetup', 'open', '--key-file=-', DISK+'p5', 'cryptreclaimed', input=secret)
            require(run('cryptsetup','luksUUID',DISK+'p5').decode().strip() == plan['luks_uuid'], 'UUID cifrado diferente.')
            mapped = Path(MAPPER).resolve().name
            require({p.name for p in Path('/sys/class/block',mapped,'slaves').iterdir()} == {'nvme0n1p5'},
                    'O mapeamento cifrado aponta para outra partição.')
            require(Path('/sys/class/block',mapped,'dm/uuid').read_text().strip().startswith(
                    'CRYPT-LUKS2-'+plan['luks_uuid'].replace('-','')+'-'), 'Mapeamento LUKS inesperado.')
            secret = b''
            if not (work/'header.luks2').exists():
                run('cryptsetup','luksHeaderBackup',DISK+'p5','--header-backup-file',str(work/'header.luks2'))
            print('A instalar o arranque verificado antes de integrar o espaço…', flush=True)
            install_boot(work)
            lifecycle.write(work/'boot-installed.json', {'ready': True})
            if not is_member():
                run('btrfs','device','add',MAPPER,'/')
            require(is_member(), 'O novo volume não aparece no Btrfs.')
            run('btrfs','filesystem','sync','/')
            finish(lifecycle, plan, work)
            print('Concluído: espaço integrado no Linux; Windows Pessoal preservado. O próximo arranque precisa de validação física.')
        except BaseException:
            # After partitioning, retain new unlock config for an explicit resume.
            # Before it, restore the original config; the old UKIs are untouched.
            if table() == plan['before'] and (work/'backed-up.json').exists():
                restore_configs(work)
            lifecycle.state(dict(plan, action='native-delete-v3'), 'recovery-required', 0,
                            'Integração pendente. Executa novamente o comando local da mesma geração.')
            raise
        finally:
            secret = b''


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Não foi possível concluir: '+str(error),file=sys.stderr)
        raise SystemExit(1)
