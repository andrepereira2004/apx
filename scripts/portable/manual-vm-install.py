#!/usr/bin/python
"""Prepare only a fresh graphical Hub for the owner's retained manual VM."""
import hashlib
import importlib.util
import json
from pathlib import Path
import secrets
import subprocess
import time

if __name__ == '__main__':
    result = Path('/root/manual-install-result.json')
    try:
        if subprocess.run(['systemd-detect-virt','--vm','--quiet']).returncode or not Path('/etc/apx-disposable-full-vm').is_file():
            raise RuntimeError('disposable VM only')
        subprocess.run(['/usr/lib/systemd/systemd-networkd-wait-online','--any','--ipv4','--timeout=60'],check=True)
        with Path('/root/manual-install.log').open('w') as log:
            subprocess.run(['bash','/root/apx/scripts/portable/install-apx-full.sh','--apply','--password-stdin'],
                           input=secrets.token_urlsafe(30)+'\n',text=True,stdout=log,stderr=subprocess.STDOUT,check=True)
        subprocess.run(['systemctl','start','apx-portable-graphical'],check=True)
        for _ in range(1200):
            active = Path('/run/apx/active-graphical-environment-v1.json')
            if active.is_file() and json.loads(active.read_text()).get('name') == 'hub': break
            time.sleep(.25)
        else: raise RuntimeError('graphical Hub readiness timed out')
        spec=importlib.util.spec_from_file_location('installer','/root/apx/scripts/portable/install_apx_full.py')
        installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
        assets=installer.manifests()['ENVIRONMENT_SHELL_ASSETS']
        for name,pin in assets.items():
            if hashlib.sha256((Path('/usr/share/apx/config-seeds/environment-shell-v1')/name).read_bytes()).hexdigest()!=pin:
                raise RuntimeError('shell seed differs: '+name)
        removed=0
        for package in Path('/var/cache/pacman/pkg').iterdir():
            if package.is_file() and not package.is_symlink() and (package.name.endswith(('.pkg.tar.zst','.pkg.tar.zst.sig'))):
                removed+=package.stat().st_size;package.unlink()
        subprocess.run(['fstrim','/'],check=True)
        result.write_text(json.dumps({'state':'ready','shell_assets_verified':len(assets),'package_cache_bytes_removed':removed,
                                      'retention':'Keep for owner hands-on test','human_password':'Owner chooses locally on first SDL launch; never recorded here'},indent=2)+'\n')
        print('APX_MANUAL_VM_READY',flush=True)
    except Exception as error:
        result.write_text(json.dumps({'state':'failed','error':str(error)},indent=2)+'\n')
        raise
