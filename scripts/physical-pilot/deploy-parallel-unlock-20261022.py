#!/usr/bin/env python3
"""Bounded pilot parallel unlock; backup contains private config, never models."""
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys

REPO=Path(__file__).resolve().parents[2]
BASE=Path('/var/lib/apx/environments')
IDENTITY=Path('/var/lib/apx/face-auth-v1')

def native(data):
    text=data.decode()
    assert len(re.findall(r'(?m)^workaround\s*=\s*(?:off|native)\s*$',text))==1
    return re.sub(r'(?m)^workaround\s*=\s*(?:off|native)\s*$', 'workaround = native',text).encode()

def atomic(path,data):
    assert path.is_file() and not path.is_symlink(),path
    st=path.stat(); temp=path.with_name(path.name+'.parallel-unlock-tmp')
    descriptor=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL,st.st_mode&0o777)
    try:
        with os.fdopen(descriptor,'wb') as out:
            out.write(data);out.flush();os.fsync(out.fileno())
        os.chown(temp,st.st_uid,st.st_gid);os.replace(temp,path)
    finally:
        if temp.exists():temp.unlink()

def main():
    assert tuple(Path(p).read_text().strip() for p in ['/etc/hostname','/sys/class/dmi/id/product_name','/sys/class/dmi/id/board_name'])==('apx-host','82JU','LNVNB161216')
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    with open('/run/apx/machine-transition-v1.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        assert not Path('/run/apx/system-power-v1.reserved').exists()
        if len(sys.argv)==3 and sys.argv[1]=='--rollback':
            backup=Path(sys.argv[2]).resolve()
            assert backup.parent==Path('/var/lib/apx/backups') and backup.name.endswith('-parallel-unlock')
            for item in reversed(json.loads((backup/'inventory.json').read_text())):
                target=Path(item['path'])
                assert hashlib.sha256(target.read_bytes()).hexdigest()==item['after']
                atomic(target,(backup/item['saved']).read_bytes())
            print('Restored parallel unlock predecessors');return
        pam=(REPO/'config/howdy-v1/pam/hyprlock-workload').read_bytes()
        previous=pam.decode().replace('# Howdy requests the password while scanning (core.workaround=native).\n# Submitted input is retained in PAM_AUTHTOK for pam_unix; either successful\n# method clears faillock and finishes authentication.','# A submitted password is checked first. An empty Enter falls through to\n# Howdy; either successful method clears faillock and finishes authentication.').replace('auth       [success=2 default=ignore] pam_howdy.so\nauth       [success=1 default=ignore] pam_unix.so','auth       [success=2 default=ignore] pam_unix.so\nauth       [success=1 default=ignore] pam_howdy.so').encode()
        planned={}
        for name in ('hub','faculdade','hytale','minecraft','steam'):
            env=BASE/name; record=json.loads((env/'registration.json').read_text())
            assert record['state'] in ('running','stopped')
            assert record['role']==('hub' if name=='hub' else 'graphical-base')
            root=env/'root'
            target=root/'etc/pam.d/hyprlock'
            assert target.read_bytes() in (previous,pam),target
            planned[root/'etc/howdy/config.ini']=native((root/'etc/howdy/config.ini').read_bytes())
            planned[target]=pam
        # Keep the opt-in creation policy independent and digest-validated.
        sys.path.insert(0,str(REPO/'src'))
        from apx_face_auth import load_identity
        identity=load_identity(IDENTITY);assert identity
        assert identity['hyprlock.pam'] in (previous,pam)
        planned[IDENTITY/'config.ini']=native(identity['config.ini'])
        planned[IDENTITY/'hyprlock.pam']=pam
        manifest=json.loads((IDENTITY/'manifest.json').read_text())
        for name in ('config.ini','hyprlock.pam'):
            manifest['files'][name]=hashlib.sha256(planned[IDENTITY/name]).hexdigest()
        planned[IDENTITY/'manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode()
        planned={p:d for p,d in planned.items() if p.read_bytes()!=d}
        if sys.argv[1:]==['--check']:
            print('Pending authentication files:',len(planned));return
        if not planned:
            print('Authentication already updated');return
        backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-parallel-unlock')
        backup.mkdir(mode=0o700)
        inventory=[]
        for index,(path,data) in enumerate(planned.items()):
            saved=str(index);shutil.copy2(path,backup/saved)
            inventory.append(dict(path=str(path),saved=saved,before=hashlib.sha256(path.read_bytes()).hexdigest(),after=hashlib.sha256(data).hexdigest()))
        (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
        try:
            for path,data in planned.items():atomic(path,data)
            assert load_identity(IDENTITY)
            assert all(hashlib.sha256(Path(i['path']).read_bytes()).hexdigest()==i['after'] for i in inventory)
        except BaseException:
            for item in reversed(inventory):atomic(Path(item['path']),(backup/item['saved']).read_bytes())
            raise
        print('Authentication backup:',backup)
if __name__=='__main__':main()
