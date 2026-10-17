#!/usr/bin/env python3
"""Install the owner-selected Lucide bar without replacing Environment logic."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,os,re,shutil

REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/'config/environment-shell-v1'
SEED=Path('/usr/share/apx/config-seeds/environment-shell-v1')

def main():
    assert Path('/etc/hostname').read_text().strip()=='apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    spec=importlib.util.spec_from_file_location('transform',REPO/'audit/2026-10-16-lucide-bar/transform.py')
    transform=importlib.util.module_from_spec(spec);spec.loader.exec_module(transform)
    spec=importlib.util.spec_from_file_location('polish',REPO/'audit/2026-10-16-lucide-bar/polish.py')
    polish=importlib.util.module_from_spec(spec);spec.loader.exec_module(polish)
    relatives=['quickshell/apx/'+name for name in ['shell.qml','BarButton.qml','WorkspaceStrip.qml','LucideIcon.qml','IconLabel.qml']]
    relatives += [str(p.relative_to(SOURCE)) for folder in ['quickshell/apx/icons/lucide','local/share/fonts/jetbrains-mono'] for p in (SOURCE/folder).iterdir() if p.is_file()]
    planned={}
    for rel in relatives:planned[SEED/rel]=(SOURCE/rel).read_bytes()
    for env in ('hub','faculdade','hytale','minecraft','steam'):
        home=Path('/var/lib/apx/environments')/env/'home/apx'
        for rel in relatives:
            dest=home/('.local/'+rel[6:] if rel.startswith('local/') else '.config/'+rel)
            if rel.endswith('/shell.qml'):
                text=dest.read_text()
                if 'readonly property string batteryIconName' not in text:text=transform.shell(text)
                if 'property string iconName: ""' not in text[text.index('    component MenuButton: Rectangle'):text.index('    component MenuButton: Rectangle')+200]:text=polish.polish(text)
                data=text.encode()
            elif rel.endswith('/WorkspaceStrip.qml'):
                text=dest.read_text()
                data=(transform.workspace(text) if '// Lucide chevron-right:' in text else text).encode()
            else:data=(SOURCE/rel).read_bytes()
            planned[dest]=data
    for runtime,assets in [(REPO/'scripts/virtual-lab/apx-lab-runtime.py',SOURCE),(Path('/usr/lib/apx/apx-lab-runtime.py'),SEED)]:
        original=runtime.read_text();start=original.index('ENVIRONMENT_SHELL_ASSETS = {');end=original.index('\n}',start)+2;section=original[start:end]
        for rel in relatives:
            asset=assets/rel;data=planned.get(asset,asset.read_bytes() if asset.exists() else b'');digest=hashlib.sha256(data).hexdigest()
            section,count=re.subn(r'("'+re.escape(rel)+r'": ")[a-f0-9]{64}("[,])',lambda m:m[1]+digest+m[2],section)
            assert count<=1
            if not count:section=section.replace('ENVIRONMENT_SHELL_ASSETS = {','ENVIRONMENT_SHELL_ASSETS = {\n    '+json.dumps(rel)+': '+json.dumps(digest)+',',1)
        planned[runtime]=(original[:start]+section+original[end:]).encode()
    recovery=REPO/'scripts/physical-pilot/recover-development-quota-v1.sh'
    text,count=re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+hashlib.sha256(planned[REPO/'scripts/virtual-lab/apx-lab-runtime.py']).hexdigest(),recovery.read_text());assert count==1
    planned[recovery]=text.encode()
    backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-lucide-bar')
    for dest in planned:
        assert not dest.is_symlink()
        parent=dest.parent
        while not parent.exists():parent=parent.parent
        assert not parent.is_symlink()
    planned={dest:data for dest,data in planned.items() if not dest.exists() or dest.read_bytes()!=data}
    if not planned:
        print("All Lucide bar files already match; no changes.")
        return
    inventory=[]
    # Install resources before the watched shell files so reloads see complete assets.
    for dest,data in sorted(planned.items(),key=lambda entry:entry[0].name=='shell.qml'):
        saved=backup/str(dest).lstrip('/');saved.parent.mkdir(parents=True,exist_ok=True)
        existed=dest.exists()
        if existed:shutil.copy2(dest,saved)
        else:saved.with_suffix(saved.suffix+'.absent').touch()
        ancestor=dest.parent;missing=[]
        while not ancestor.exists():missing.append(ancestor);ancestor=ancestor.parent
        metadata=dest.stat() if existed else ancestor.stat()
        for directory in reversed(missing):
            directory.mkdir(mode=0o755);os.chown(directory,metadata.st_uid,metadata.st_gid)
        temp=dest.with_name(dest.name+'.lucide-tmp');temp.write_bytes(data)
        os.chmod(temp,metadata.st_mode&0o777 if existed else 0o644);os.chown(temp,metadata.st_uid,metadata.st_gid);os.replace(temp,dest)
        assert dest.read_bytes()==data
        inventory.append({'path':str(dest),'existed':existed,'sha256':hashlib.sha256(data).hexdigest()})
    (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    print(backup)
    print('Verified',len(planned),'files')

if __name__=='__main__':main()
