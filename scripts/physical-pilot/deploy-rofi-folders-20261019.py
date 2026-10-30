#!/usr/bin/python
"""Deploy owner-requested application folders and global search, preserving homes."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import shutil

REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/'config/environment-shell-v1'
SEED=Path('/usr/share/apx/config-seeds/environment-shell-v1')
RELATIVES=['local/bin/apx-laptop-action-v1', 'local/bin/apx-window-apps-v1', 'local/lib/rofi/apx-rofi-apps-v1.so',
           'quickshell/apx/shell.qml', 'quickshell/apx/icons/rofi/bring-to-front.svg']

def shell_update(text):
    return text.replace('apps:/home/apx/.local/bin/apx-window-apps-v1,files', 'apps,files')


def main():
    if os.geteuid() or Path('/etc/hostname').read_text().strip()!='apx-host' \
            or Path('/sys/class/dmi/id/product_name').read_text().strip()!='82JU':
        raise RuntimeError('owner-authorized physical pilot only')
    planned={}
    for rel in RELATIVES:planned[SEED/rel]=(SOURCE/rel).read_bytes()
    for directory in sorted(Path('/var/lib/apx/environments').iterdir()):
        registration=directory/'registration.json'
        if not registration.is_file() or registration.is_symlink():continue
        record=json.loads(registration.read_text())
        home=directory/'home/apx/.config/quickshell/apx'
        if record.get('name')!=directory.name or not (home/'shell.qml').is_file():continue
        config=directory/'home/apx/.config'
        for rel in RELATIVES:
            target=(directory/'home/apx/.local'/rel.removeprefix('local/')) if rel.startswith('local/') else config/rel
            if rel == 'local/bin/apx-laptop-action-v1':
                planned[target]=target.read_text().replace('detached([rofi, \"-show\", \"drun\"])', 'detached([\"/usr/bin/env\", \"ROFI_PLUGIN_PATH=/home/apx/.local/lib/rofi\", rofi, \"-modi\", \"apps,files\", \"-show\", \"apps\", \"-me-accept-entry\", \"MousePrimary\", \"-me-accept-custom\", \"MouseSecondary\"])').encode()
            elif rel == 'quickshell/apx/shell.qml':
                planned[target]=shell_update(target.read_text()).encode()
            else:
                planned[target]=(SOURCE/rel).read_bytes()
    for runtime in [REPO/'scripts/virtual-lab/apx-lab-runtime.py',Path('/usr/lib/apx/apx-lab-runtime.py')]:
        original=runtime.read_text();start=original.index('ENVIRONMENT_SHELL_ASSETS = {');end=original.index('\n}',start)+2;section=original[start:end]
        for rel in RELATIVES:
            digest=hashlib.sha256((SOURCE/rel).read_bytes()).hexdigest()
            section,count=re.subn(r'("'+re.escape(rel)+r'": ")[a-f0-9]{64}("[,])',lambda m:m[1]+digest+m[2],section)
            if count>1:raise RuntimeError('duplicate pin')
            if not count:section=section.replace('ENVIRONMENT_SHELL_ASSETS = {','ENVIRONMENT_SHELL_ASSETS = {\n    '+json.dumps(rel)+': '+json.dumps(digest)+',',1)
        planned[runtime]=(original[:start]+section+original[end:]).encode()
    recovery=REPO/'scripts/physical-pilot/recover-development-quota-v1.sh'
    data,count=re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+hashlib.sha256(planned[REPO/'scripts/virtual-lab/apx-lab-runtime.py']).hexdigest(),recovery.read_text())
    if count!=1:raise RuntimeError('recovery runtime pin is missing')
    planned[recovery]=data.encode()
    planned={p:data for p,data in planned.items() if not p.exists() or p.read_bytes()!=data}
    if not planned:
        print('Menu assets already installed.');return
    backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-rofi-folders')
    inventory=[]
    for target,data in sorted(planned.items(),key=lambda item:item[0].name=='shell.qml'):
        if target.is_symlink() or target.parent.is_symlink():raise RuntimeError('unsafe target')
        existed=target.exists();saved=backup/str(target).lstrip('/');saved.parent.mkdir(parents=True,exist_ok=True)
        if existed:shutil.copy2(target,saved)
        else:saved.with_suffix(saved.suffix+'.absent').touch()
        if not target.parent.exists():
            target.parent.mkdir(parents=True,exist_ok=True)
            parent_info=target.parent.parent.stat();os.chown(target.parent,parent_info.st_uid,parent_info.st_gid)
        info=(target if existed else target.parent).stat()
        temp=target.with_name('.'+target.name+'.package-icons-tmp');fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,info.st_mode&0o777 if existed else (0o755 if '/bin/' in str(target) else 0o644))
        with os.fdopen(fd,'wb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
        os.chmod(temp,info.st_mode&0o777 if existed else (0o755 if '/bin/' in str(target) else 0o644));os.chown(temp,info.st_uid,info.st_gid);os.replace(temp,target)
        inventory.append({'path':str(target),'previously_existed':existed,'sha256':hashlib.sha256(data).hexdigest()})
    (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    print(json.dumps({'backup':str(backup),'changed_files':len(inventory)},indent=2))


if __name__=='__main__':main()
