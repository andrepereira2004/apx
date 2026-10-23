#!/usr/bin/env python3
"""Reversible, target-bound Island presentation experiment; no auth/service changes."""
from pathlib import Path
import datetime,fcntl,hashlib,importlib.util,json,os,re,shutil,sys
REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/'config/environment-shell-v1'
CANDIDATE=REPO/'audit/2026-10-16-island/candidate'
SEED=Path('/usr/share/apx/config-seeds/environment-shell-v1')

def write(path,data,mode,uid,gid):
    assert not path.is_symlink(),path
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+'.island-tmp');temporary.write_bytes(data)
    os.chmod(temporary,mode);os.chown(temporary,uid,gid);os.replace(temporary,path)

def main():
    assert Path('/etc/hostname').read_text().strip()=='apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    if len(sys.argv)==3 and sys.argv[1]=='--rollback':
        backup=Path(sys.argv[2]).resolve();assert backup.parent==Path('/var/lib/apx/backups') and backup.name.endswith('-island-trial')
        for item in json.loads((backup/'inventory.json').read_text()):
            path=Path(item['path'])
            if item['existed']:write(path,(backup/str(path).lstrip('/')).read_bytes(),item['mode'],item['uid'],item['gid'])
            elif path.exists():path.unlink()
        for p in Path('/var/lib/apx/environments').glob('*/home/apx/.config/quickshell/apx/shell.qml'):p.touch()
        print('Restored',backup);return
    assert len(sys.argv)==1
    spec=importlib.util.spec_from_file_location('island_transform',CANDIDATE.parent/'transform.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    resources=[str(p.relative_to(CANDIDATE)) for p in CANDIDATE.rglob('*') if p.is_file() and '__pycache__' not in str(p)]
    relatives=resources+['quickshell/apx/shell.qml']
    planned={}
    roots=[SOURCE,SEED]+[Path('/var/lib/apx/environments')/n/'home/apx' for n in ['hub','faculdade','hytale','minecraft','steam']]
    for base in roots:
        for rel in relatives:
            dest=base/rel if base in (SOURCE,SEED) else base/('.local/'+rel[6:] if rel.startswith('local/') else '.config/'+rel)
            data=module.shell(dest.read_text()).encode() if rel=='quickshell/apx/shell.qml' else (CANDIDATE/rel).read_bytes()
            if rel=='hypr/apx-lock-appearance.conf' and dest.exists():continue
            planned[dest]=data
    for runtime,base in [(REPO/'scripts/virtual-lab/apx-lab-runtime.py',SOURCE),(Path('/usr/lib/apx/apx-lab-runtime.py'),SEED)]:
        text=runtime.read_text();start=text.index('ENVIRONMENT_SHELL_ASSETS = {');end=text.index('\n}',start)+2;section=text[start:end]
        for rel in relatives:
            path=base/rel;digest=hashlib.sha256(planned.get(path,path.read_bytes() if path.exists() else b'')).hexdigest()
            section,count=re.subn(r'("'+re.escape(rel)+r'": ")[a-f0-9]{64}("[,])',lambda m:m[1]+digest+m[2],section);assert count<=1
            if not count:section=section.replace('ENVIRONMENT_SHELL_ASSETS = {','ENVIRONMENT_SHELL_ASSETS = {\n    '+json.dumps(rel)+': '+json.dumps(digest)+',',1)
        planned[runtime]=(text[:start]+section+text[end:]).encode()
    recovery=REPO/'scripts/physical-pilot/recover-development-quota-v1.sh'
    text,count=re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+hashlib.sha256(planned[REPO/'scripts/virtual-lab/apx-lab-runtime.py']).hexdigest(),recovery.read_text());assert count==1
    planned[recovery]=text.encode()
    planned={path:data for path,data in planned.items() if not path.exists() or path.read_bytes()!=data}
    if not planned:print('Island trial already installed.');return
    backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-island-trial');backup.mkdir(parents=True)
    inventory=[]
    for path in planned:
        existed=path.exists();metadata=path.stat() if existed else path.parent.stat()
        mode=metadata.st_mode&0o777 if existed else (0o755 if '/bin/' in str(path) else 0o644)
        saved=backup/str(path).lstrip('/');saved.parent.mkdir(parents=True,exist_ok=True)
        if existed:shutil.copy2(path,saved)
        inventory.append(dict(path=str(path),existed=existed,mode=mode,uid=metadata.st_uid,gid=metadata.st_gid))
    (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    # Keep the original pre-trial rollback complete as later refinements add files.
    anchor=REPO/'audit/2026-10-16-island/baseline-backup.txt'
    if not anchor.exists():anchor.write_text(str(backup)+'\n')
    baseline=Path(anchor.read_text().strip())
    if baseline!=backup:
        original=json.loads((baseline/'inventory.json').read_text());known={item['path'] for item in original}
        for item in inventory:
            if item['path'] in known:continue
            original.append(item)
            if item['existed']:
                old=backup/item['path'].lstrip('/');saved=baseline/item['path'].lstrip('/');saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,saved)
        (baseline/'inventory.json').write_text(json.dumps(original,indent=2)+'\n')
    for item in sorted(inventory,key=lambda i:Path(i['path']).name=='shell.qml'):
        path=Path(item['path']);write(path,planned[path],item['mode'],item['uid'],item['gid'])
        assert path.read_bytes()==planned[path]
    for p in Path('/var/lib/apx/environments').glob('*/home/apx/.config/quickshell/apx/shell.qml'):p.touch()
    print(backup);print('Verified',len(planned),'files. No authentication, service or Hyprland animation changes.')

if __name__=='__main__':
    with open('/run/apx/machine-transition-v1.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);main()
