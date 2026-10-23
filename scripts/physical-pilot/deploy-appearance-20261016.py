#!/usr/bin/env python3
"""Install scoped appearance and compact controls on the identity-bound pilot."""
from pathlib import Path
import datetime,fcntl,hashlib,importlib.util,json,os,re,shutil,subprocess
REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/'config/environment-shell-v1'
SEED=Path('/usr/share/apx/config-seeds/environment-shell-v1')


def load(name):
    spec=importlib.util.spec_from_file_location(name,REPO/'audit/2026-10-16-appearance'/f'{name}.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def main():
    assert Path('/etc/hostname').read_text().strip()=='apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    transform=load('transform');compact=load('compact');ghost=load('ghost')
    components=['shell.qml','BarButton.qml','LucideIcon.qml','IconLabel.qml','Appearance.qml','PersonalizationPanel.qml','DesktopActivity.qml','ControlTile.qml','ControlDashboard.qml','ActivityPanel.qml','qmldir','GhostLines.js']
    relatives=['quickshell/apx/'+name for name in components]
    relatives += ['local/bin/apx-appearance-v1','local/bin/apx-desktop-activity-v1','kitty/kitty.conf','kitty/apx-appearance.conf','rofi/config.rasi','rofi/apx-appearance.rasi']
    relatives += ['quickshell/apx/icons/lucide/'+name+'.svg' for name in ['music','video','bell','play','pause','skip-back','skip-forward','battery','battery-full','battery-medium','battery-low','battery-warning','battery-charging']]
    planned={SEED/rel:(SOURCE/rel).read_bytes() for rel in relatives}
    for name in ['hub','faculdade','hytale','minecraft','steam']:
        home=Path('/var/lib/apx/environments')/name/'home/apx'
        for rel in relatives:
            dest=home/('.local/'+rel[6:] if rel.startswith('local/') else '.config/'+rel)
            if rel.endswith('/shell.qml'):data=ghost.ghost(compact.compact(transform.shell(dest.read_text()))).encode()
            elif rel=='kitty/kitty.conf':
                text=dest.read_text()
                if 'include apx-appearance.conf' not in text:text+='\n# Environment-local, owner-selected appearance tint.\ninclude apx-appearance.conf\n'
                data=text.encode()
            elif rel=='rofi/config.rasi':
                text=dest.read_text().replace('Selawik','JetBrains Mono')
                if '@import "apx-appearance.rasi"' not in text:text+='\n@import "apx-appearance.rasi"\n'
                data=text.encode()
            elif rel in ['kitty/apx-appearance.conf','rofi/apx-appearance.rasi'] and dest.exists():continue
            else:data=(SOURCE/rel).read_bytes()
            planned[dest]=data
    host={
        Path('/usr/lib/apx/apx-host-services-v3.py'):REPO/'scripts/physical-pilot/apx-host-services-v3.py',
        Path('/usr/lib/apx/apx-host-services-client-v3.py'):REPO/'scripts/physical-pilot/apx-host-services-client-v3.py',
        Path('/usr/lib/apx/apx_host_services_v3_contract.py'):REPO/'src/apx_host_services_v3_contract.py',
        Path('/etc/systemd/system/apx-host-services-v3.service'):REPO/'config/systemd/apx-host-services-v3.service',
    }
    planned.update({dest:source.read_bytes() for dest,source in host.items()})
    for runtime,assets in [(REPO/'scripts/virtual-lab/apx-lab-runtime.py',SOURCE),(Path('/usr/lib/apx/apx-lab-runtime.py'),SEED)]:
        original=runtime.read_text();start=original.index('ENVIRONMENT_SHELL_ASSETS = {');end=original.index('\n}',start)+2;section=original[start:end]
        for rel in relatives:
            asset=assets/rel;data=planned[asset] if asset in planned else asset.read_bytes();digest=hashlib.sha256(data).hexdigest()
            section,count=re.subn(r'("'+re.escape(rel)+r'": ")[a-f0-9]{64}("[,])',lambda m:m[1]+digest+m[2],section)
            assert count<=1
            if not count:section=section.replace('ENVIRONMENT_SHELL_ASSETS = {','ENVIRONMENT_SHELL_ASSETS = {\n    '+json.dumps(rel)+': '+json.dumps(digest)+',',1)
        planned[runtime]=(original[:start]+section+original[end:]).encode()
    recovery=REPO/'scripts/physical-pilot/recover-development-quota-v1.sh'
    text,count=re.subn(r'(?m)^readonly RUNTIME_SHA256=[a-f0-9]{64}$','readonly RUNTIME_SHA256='+hashlib.sha256(planned[REPO/'scripts/virtual-lab/apx-lab-runtime.py']).hexdigest(),recovery.read_text());assert count==1
    planned[recovery]=text.encode()
    planned={dest:data for dest,data in planned.items() if not dest.exists() or dest.read_bytes()!=data}
    if not planned:print('Appearance files already installed.');return
    backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-appearance-controls')
    inventory=[]
    shells=[]
    for dest,data in sorted(planned.items(),key=lambda pair:pair[0].name=='shell.qml'):
        assert not dest.is_symlink(),dest
        saved=backup/str(dest).lstrip('/');saved.parent.mkdir(parents=True,exist_ok=True)
        exists=dest.exists()
        if exists:shutil.copy2(dest,saved)
        else:saved.with_suffix(saved.suffix+'.absent').touch()
        parent=dest.parent;missing=[]
        while not parent.exists():missing.append(parent);parent=parent.parent
        metadata=dest.stat() if exists else parent.stat()
        for directory in reversed(missing):directory.mkdir(mode=0o755);os.chown(directory,metadata.st_uid,metadata.st_gid)
        # These two files are mounted read-only by inode into live Environments.
        # Preserve their Host inode so current sessions also see the new client contract.
        in_place=dest in [Path('/usr/lib/apx/apx-host-services-client-v3.py'),Path('/usr/lib/apx/apx_host_services_v3_contract.py')]
        if in_place:dest.write_bytes(data)
        else:
            temporary=dest.with_name(dest.name+'.appearance-tmp');temporary.write_bytes(data)
            mode=(metadata.st_mode&0o777) if exists else (0o755 if '/bin/' in str(dest) else 0o644)
            os.chmod(temporary,mode);os.chown(temporary,metadata.st_uid,metadata.st_gid);os.replace(temporary,dest)
        assert dest.read_bytes()==data
        inventory.append({'path':str(dest),'existed':exists,'sha256':hashlib.sha256(data).hexdigest(),'in_place':in_place})
        if dest.name=='shell.qml' and str(dest).startswith('/var/lib/apx/environments/'):shells.append(dest)
    (backup/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    if any(dest in planned for dest in host if dest.name != "apx-host-services-client-v3.py"):
        subprocess.run(['systemctl','daemon-reload'],check=True)
        subprocess.run(['systemctl','restart','apx-host-services-v3.service'],check=True)
        subprocess.run(['systemctl','is-active','--quiet','apx-host-services-v3.service'],check=True)
    for path in shells:path.touch()
    print(backup);print('Verified',len(planned),'installed/seed files.')


if __name__=='__main__':
    with open('/run/apx/machine-transition-v1.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        main()
