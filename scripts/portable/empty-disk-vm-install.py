#!/usr/bin/python
"""TEST ONLY: exercise interactive disk installer with synthetic credentials."""
from pathlib import Path
import importlib.util
import json
import os
import pty
import secrets
import select
import subprocess
import time


def main():
    if subprocess.run(['systemd-detect-virt','--vm','--quiet']).returncode or not Path('/etc/apx-disposable-full-vm').is_file():
        raise RuntimeError('disposable VM only')
    os.umask(0o077)  # Exercise installation despite a restrictive live-root umask.
    script=Path('/root/apx-portable/scripts/portable/install_apx_disk.py')
    root=Path('/mnt/apx-owned-test-target')
    if root.exists(): raise RuntimeError('test mount already exists')
    master,slave=pty.openpty()
    process=subprocess.Popen(['python',str(script),'--disk','/dev/vda','--apply'],
                             stdin=slave,stdout=slave,stderr=slave,start_new_session=True)
    os.close(slave)
    password=secrets.token_urlsafe(30)
    log=Path('/root/empty-disk-install.log').open('wb')
    tail=b''; sent=set(); deadline=time.monotonic()+3600
    try:
        while time.monotonic()<deadline:
            if select.select([master],[],[],1)[0]:
                try: block=os.read(master,65536)
                except OSError: break
                if not block: break
                # getpass disables terminal echo. Never emit synthetic passwords.
                if password.encode() in block: raise RuntimeError('unexpected password echo')
                log.write(block);log.flush();tail=(tail+block)[-20000:]
                if b'Type exactly: ' in tail and 'confirmation' not in sent:
                    line=tail.split(b'Type exactly: ',1)[1].splitlines()[0]
                    os.write(master,line+b'\n');sent.add('confirmation');tail=b''
                if b'New recovery root password (12+ characters): ' in tail and 'password' not in sent:
                    os.write(master,password.encode()+b'\n');sent.add('password');tail=b''
                if b'Repeat recovery root password: ' in tail and 'repeat' not in sent:
                    os.write(master,password.encode()+b'\n');sent.add('repeat');tail=b''
            if process.poll() is not None: break
        else:
            process.terminate();raise RuntimeError('disk installation timed out')
        if process.wait()!=0: raise RuntimeError('interactive disk installer failed; inspect private guest log')
    finally:
        log.close();os.close(master);password=None
    # Fixture only: root serial channel after installed-disk boot, not part of
    # the source bundle/product. No shared Host folders or network listener.
    root.mkdir()
    subprocess.run(['mount','-o','subvol=@','/dev/vda2',str(root)],check=True)
    try:
        if not (root/'etc/apx-empty-disk-install.json').is_file(): raise RuntimeError('wrong test target')
        import shutil
        shutil.copy2('/root/full-vm-agent.py',root/'root/full-vm-agent.py')
        shutil.copy2('/root/full-vm-smoke.py',root/'root/full-vm-smoke.py')
        (root/'root/apx').symlink_to('/opt/apx-installer')
        (root/'etc/apx-disposable-full-vm').write_text('disposable-blank-disk-vm-only\n')
        unit=root/'etc/systemd/system/apx-empty-test-agent.service'
        unit.write_text('''[Unit]
Description=Disposable blank-disk test control fixture
ConditionVirtualization=vm
[Service]
ExecStart=/usr/bin/python /root/full-vm-agent.py
Restart=on-failure
[Install]
WantedBy=multi-user.target
''')
        subprocess.run(['systemctl','--root',str(root),'enable',unit.name],check=True)
    finally:
        subprocess.run(['umount',str(root)],check=True);root.rmdir()
    Path('/root/empty-stage1-result.json').write_text(json.dumps({'state':'passed','interactive_prompts':sorted(sent),
        'disk':'/dev/vda','scope':'disposable QEMU virtual disk only','installer_initial_umask':'0077',
        'fixture_excluded_from_product':True})+'\n')


if __name__=='__main__':
    try: main()
    except Exception as error:
        Path('/root/empty-stage1-result.json').write_text(json.dumps({'state':'failed','error':str(error)})+'\n')
        raise
