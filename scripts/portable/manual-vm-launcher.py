#!/usr/bin/python
"""Local SDL viewer/launcher inside disposable Teste; never installed by APX."""
import base64
import fcntl
import getpass
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import time

VM = Path.home() / 'VMs/APX-Rebuild'


def exchange(args, timeout=90):
    request_id = secrets.token_hex(12)
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(timeout + 10)
        connection.connect(str(VM / 'agent.sock'))
        connection.sendall((json.dumps({'args': args, 'timeout': timeout, 'request_id': request_id}) + '\n').encode())
        data = bytearray()
        while len(data) < 200000:
            block = connection.recv(16384)
            if not block: break
            data.extend(block)
            while b'\n' in data:
                line, _, rest = data.partition(b'\n'); data = bytearray(rest)
                result = json.loads(line)
                if result.get('request_id') == request_id:
                    if result.get('exit_code') != 0:
                        raise RuntimeError('A VM recusou a operação; consulta o registo local de arranque.')
                    return result
        raise RuntimeError('A VM não respondeu ao pedido local.')


def main():
    if os.getuid() != 1000 or not VM.is_dir() or not Path('/dev/kvm').is_char_device():
        raise RuntimeError('Abre este atalho dentro do Environment Teste, com KVM disponível.')
    lock = (VM / 'viewer.lock').open('a')
    try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError: raise RuntimeError('A VM já está aberta.')
    for name in ['disk.raw', 'vmlinuz', 'initramfs']:
        if (VM / name).is_symlink() or not (VM / name).is_file(): raise RuntimeError('Falta um ficheiro da VM.')
    if not (VM / 'manual-ready.json').is_file():
        raise RuntimeError('A instalação da VM ainda está a ser preparada.')
    marker = VM / 'manual-password-configured'
    password = None
    if not marker.exists():
        print('Cria uma palavra-passe SÓ para esta VM. Não uses a palavra-passe do teu computador.', flush=True)
        while True:
            password = getpass.getpass('Nova palavra-passe da VM (mínimo 12 caracteres): ')
            if 12 <= len(password) <= 255 and '\n' not in password and '\r' not in password \
                    and password == getpass.getpass('Repetir: '): break
            print('As palavras-passe devem coincidir e ter pelo menos 12 caracteres.')
    for name in ['agent.sock', 'qmp.sock']: (VM / name).unlink(missing_ok=True)
    command = ['qemu-system-x86_64', '-name', 'APX — Teste na VM', '-machine', 'q35,accel=kvm',
               '-cpu', 'host', '-m', '4096', '-smp', '4', '-nodefaults',
               '-display', 'sdl,gl=off', '-kernel', str(VM / 'vmlinuz'), '-initrd', str(VM / 'initramfs'),
               '-append', 'root=/dev/vda rw console=ttyS0 loglevel=4',
               '-drive', 'if=none,id=disk,format=raw,discard=unmap,detect-zeroes=unmap,file=' + str(VM / 'disk.raw'),
               '-device', 'virtio-blk-pci,drive=disk', '-device', 'virtio-vga',
               '-netdev', 'user,id=n0', '-device', 'virtio-net-pci,netdev=n0',
               '-device', 'virtio-serial-pci', '-chardev', 'socket,id=lab,path=' + str(VM / 'agent.sock') + ',server=on,wait=off',
               '-device', 'virtserialport,chardev=lab,name=apx.lab',
               '-qmp', 'unix:' + str(VM / 'qmp.sock') + ',server=on,wait=off',
               '-serial', 'file:' + str(VM / 'serial-manual.log')]
    pulse = Path(os.environ.get('XDG_RUNTIME_DIR', '/run/user/1000')) / 'pulse/native'
    if pulse.is_socket():
        command += ['-audiodev', 'pa,id=sound,server=unix:' + str(pulse),
                    '-device', 'ich9-intel-hda', '-device', 'hda-duplex,audiodev=sound']
    print('A abrir APX na VM. Ctrl+Alt+G liberta o rato/teclado da janela.', flush=True)
    with (VM / 'viewer.log').open('a') as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        try:
            if password is not None:
                for _ in range(900):
                    if process.poll() is not None: raise RuntimeError('QEMU terminou; consulta ~/VMs/APX-Rebuild/viewer.log.')
                    try:
                        exchange(['systemd-run','-M','apx-hub','--quiet','--wait','--pipe','--collect','/usr/bin/true'], timeout=3)
                        break
                    except (OSError, RuntimeError): pass
                    time.sleep(.2)
                else: raise RuntimeError('O Hub da VM demorou demasiado a arrancar.')
                encoded = base64.b64encode(('apx:' + password + '\n').encode()).decode()
                code = ("import base64,subprocess;from pathlib import Path;"
                        "subprocess.run(['systemd-run','-M','apx-hub','--quiet','--wait','--pipe','--collect','/usr/bin/chpasswd'],"
                        f"input=base64.b64decode('{encoded}'),capture_output=True,check=True);"
                        "subprocess.run(['systemctl','stop','apx-portable-graphical'],check=True);"
                        "subprocess.run(['systemctl','disable','--now','apx-full-vm-auth-fixture'],check=True);"
                        "Path('/run/apx/portable-vm-authenticated-fixture').unlink(missing_ok=True);"
                        "subprocess.run(['systemctl','start','apx-portable-graphical'],check=True)")
                exchange(['python', '-c', code], timeout=90)
                password = encoded = code = None
                marker.touch(mode=0o600)
                print('Entra na VM com a palavra-passe que acabaste de criar.', flush=True)
            process.wait()
        except BaseException:
            process.terminate()
            try: process.wait(timeout=20)
            except subprocess.TimeoutExpired: process.kill(); process.wait()
            raise
    if process.returncode:
        raise RuntimeError('A VM terminou. Pode ter sido atingido o limite de espaço (reserva de 97 GiB). Consulta ~/VMs/APX-Rebuild/viewer.log.')


if __name__ == '__main__':
    try: main()
    except (OSError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        input('Enter para fechar…')
        raise SystemExit(1)
