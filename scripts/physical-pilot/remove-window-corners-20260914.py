#!/usr/bin/env python3
"""Owner follow-up: app-specific scrolling and proportional-font bar spacing."""
import ast,datetime,fcntl,hashlib,json,os,re,shutil
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/'config/environment-shell-v1'
SEED=Path('/usr/share/apx/config-seeds/environment-shell-v1')
BASE=Path('/var/lib/apx/environments')
def main():
    assert Path('/etc/hostname').read_text().strip()=='apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip()=='82JU'
    assert Path('/sys/class/dmi/id/board_name').read_text().strip()=='LNVNB161216'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    lock=open('/run/apx/machine-transition-v1.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert not Path('/run/apx/system-power-v1.reserved').exists()
    rels=['quickshell/apx/shell.qml','rofi/config.rasi']
    retired=['quickshell/apx/WindowCornerControls.qml','local/bin/apx-window-corner-watch']
    planned=[]
    for name in ['hub','faculdade','hytale','minecraft','steam']:
        env=BASE/name;reg=json.loads((env/'registration.json').read_text())
        assert reg['state'] in ('running','stopped')
        for rel in rels:
            p=env/'home/apx'/('.'+rel if rel.startswith('local/') else '.config/'+rel)
            if p.exists(): assert p.read_bytes()==(SEED/rel).read_bytes()
            planned.append((p,(SOURCE/rel).read_bytes()))
    for rel in retired:
        for name in ['hub','faculdade','hytale','minecraft','steam']:
            p=BASE/name/'home/apx'/('.'+rel if rel.startswith('local/') else '.config/'+rel)
            assert p.read_bytes()==(SEED/rel).read_bytes();planned.append((p,None))
        planned.append((SEED/rel,None))
    for rel in rels: planned.append((SEED/rel,(SOURCE/rel).read_bytes()))
    for p in [REPO/'scripts/virtual-lab/apx-lab-runtime.py',Path('/usr/lib/apx/apx-lab-runtime.py')]:
        text=p.read_text();start=text.index('ENVIRONMENT_SHELL_ASSETS = {');end=text.index('\n}',start)+2
        assets=ast.literal_eval(text[start:end].split(' = ',1)[1])
        for rel in retired: assets.pop(rel,None)
        for rel in rels:assets[rel]=hashlib.sha256((SOURCE/rel).read_bytes()).hexdigest()
        text=text[:start]+'ENVIRONMENT_SHELL_ASSETS = '+json.dumps(assets,indent=4,sort_keys=True)+text[end:]
        planned.append((p,text.encode()))
    runtime=next(data for p,data in planned if p==REPO/'scripts/virtual-lab/apx-lab-runtime.py')
    p=REPO/'scripts/physical-pilot/recover-development-quota-v1.sh';planned.append((p,re.sub(r'(?m)^readonly RUNTIME_SHA256=.*$','readonly RUNTIME_SHA256='+hashlib.sha256(runtime).hexdigest(),p.read_text()).encode()))
    backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-remove-window-corners');backup.mkdir(mode=0o700)
    manifest=[]
    for i,(p,data) in enumerate(planned):
        assert not p.is_symlink()
        exists=p.exists()
        st=p.stat() if exists else p.parent.stat()
        saved=backup/str(i)
        if exists: shutil.copy2(p,saved)
        mode=(st.st_mode&0o777) if exists else (0o755 if p.name=='apx-sysinfo' else 0o644)
        manifest.append(dict(target=str(p),backup=str(saved) if exists else None,uid=st.st_uid,gid=st.st_gid,mode=mode,before=hashlib.sha256(p.read_bytes()).hexdigest() if exists else None,after=hashlib.sha256(data).hexdigest() if data is not None else None))
    (backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
    for (p,data),e in zip(planned,manifest):
        if not p.parent.exists():
            p.parent.mkdir(mode=0o755);os.chown(p.parent,e['uid'],e['gid'])
        if data is None:
            p.unlink();continue
        p.write_bytes(data);os.chown(p,e['uid'],e['gid']);os.chmod(p,e['mode'])
    print(backup)
if __name__=='__main__':main()
