#!/usr/bin/python
"""Apply the owner's layout-grid/layout-panel-left Rofi icons without replacing homes."""
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
import importlib.util
spec=importlib.util.spec_from_file_location('menu_update',REPO/'scripts/physical-pilot/update-menu-icons-20261018.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
ICONS=['layout-grid','layout-panel-left','layout-dashboard','book-a','book-open','box','folder-open','calendar-search','copy-plus','cpu','trash-2','undo-2','check','x','bring-to-front']
ACTION_ICONS=['copy-plus','cpu','x','trash-2','check','undo-2']
RELATIVES=['quickshell/apx/icons/rofi/'+name+'.svg' for name in ACTION_ICONS]+list(module.TRANSFORMS)+['quickshell/apx/icons/lucide/'+name+'.svg' for name in ICONS]

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
        for rel,transform in module.TRANSFORMS.items():
            target=(directory/"home/apx/.local"/rel.removeprefix("local/")) if rel.startswith("local/") else config/rel
            if target.is_file():planned[target]=transform(target.read_text()).encode()
        for name in ACTION_ICONS:
            planned[home/'icons/rofi'/f'{name}.svg']=(SOURCE/'quickshell/apx/icons/rofi'/f'{name}.svg').read_bytes()
        for name in ICONS:planned[home/'icons/lucide'/f'{name}.svg']=(SOURCE/'quickshell/apx/icons/lucide'/f'{name}.svg').read_bytes()
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
    backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-menu-icons-behavior')
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
        temp=target.with_name('.'+target.name+'.package-icons-tmp');fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,info.st_mode&0o777 if existed else 0o644)
        with os.fdopen(fd,'wb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
        os.chmod(temp,info.st_mode&0o777 if existed else 0o644);os.chown(temp,info.st_uid,info.st_gid);os.replace(temp,target)
        inventory.append({'path':str(target),'previously_existed':existed,'sha256':hashlib.sha256(data).hexdigest()})
    (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    print(json.dumps({'backup':str(backup),'changed_files':len(inventory)},indent=2))


if __name__=='__main__':main()
