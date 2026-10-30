#!/usr/bin/python3
"""Bounded pilot Host API update; retain client bind inodes and refresh live socket."""
import ctypes
import datetime
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

REPO=Path(__file__).resolve().parents[2]
FILES={
 '/usr/lib/apx/apx-host-services-v3.py':'scripts/physical-pilot/apx-host-services-v3.py',
 '/usr/lib/apx/apx-host-services-client-v3.py':'scripts/physical-pilot/apx-host-services-client-v3.py',
 '/usr/lib/apx/apx-host-services-ui-v3.py':'scripts/physical-pilot/apx-host-services-ui-v3.py',
 '/usr/lib/apx/apx_host_services_v3_contract.py':'src/apx_host_services_v3_contract.py',
}

def refresh_socket(pid):
    target=Path(f'/proc/{pid}/root/run/apx/host-services-v3-refresh.sock')
    assert not target.is_symlink()
    if target.exists() and target.stat().st_nlink == 0:
        # The previous bind still resolves an unlinked old socket. Remove only
        # our replaceable fallback mount before attaching the new endpoint.
        subprocess.run(["nsenter","-t",str(pid),"-m","-U","-p","-r","-w","--","/usr/bin/umount","/run/apx/host-services-v3-refresh.sock"],check=True)
    if not target.exists():target.touch(mode=0o600)
    libc=ctypes.CDLL(None,use_errno=True)
    fd=libc.syscall(428,-100,b'/run/apx/host-services-v3.sock',1|os.O_CLOEXEC)
    if fd<0:raise OSError(ctypes.get_errno(),'open_tree')
    try:
        program='import ctypes;libc=ctypes.CDLL(None,use_errno=True);r=libc.syscall(429,'+str(fd)+',b"",-100,b"/run/apx/host-services-v3-refresh.sock",4);assert r==0,(r,ctypes.get_errno())'
        subprocess.run(['nsenter','-t',str(pid),'-m','-U','-p','-r','-w','--','/usr/bin/python3','-c',program],pass_fds=(fd,),check=True)
    finally:os.close(fd)

def main():
    assert Path('/etc/hostname').read_text().strip()=='apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    planned={Path(target):(REPO/source).read_bytes() for target,source in FILES.items() if Path(target).read_bytes()!=(REPO/source).read_bytes()}
    if not planned:print('Host radio API already matches');return
    socket=Path('/run/apx/host-services-v3.sock');lease=socket.stat()
    backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-radio-power');backup.mkdir()
    inventory=[]
    for target,data in planned.items():
        assert not target.is_symlink()
        saved=backup/str(target).lstrip('/');saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
        inventory.append(str(target))
    (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    for target,data in planned.items():target.write_bytes(data);assert target.read_bytes()==data
    subprocess.run(['systemctl','restart','apx-host-services-v3.service'],check=True)
    for attempt in range(50):
        if socket.exists() and socket.stat().st_ino!=lease.st_ino:break
        time.sleep(.1)
    else:raise RuntimeError('New broker socket unavailable')
    os.chown(socket,lease.st_uid,lease.st_gid);os.chmod(socket,lease.st_mode&0o777)
    marker=Path('/run/apx/active-graphical-environment-v1.json')
    if not marker.exists():marker=Path('/run/apx/official-hub-graphical-v1.json')
    if marker.exists():refresh_socket(int(json.loads(marker.read_text())['pid']))
    subprocess.run(['systemctl','is-active','--quiet','apx-host-services-v3.service'],check=True)
    print(backup)

if __name__=='__main__':
    with open('/run/apx/machine-transition-v1.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);main()
