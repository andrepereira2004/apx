#!/usr/bin/env python3
"""Owner-requested, reversible per-environment touchpad/font trial."""
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
    fonts=sorted(str(p.relative_to(SOURCE)) for p in (SOURCE/'local/share/fonts').rglob('*') if p.is_file())
    assert len([p for p in fonts if p.endswith('.ttf')])==9
    rels=['gtk-3.0/settings.ini','gtk-4.0/settings.ini','fontconfig/fonts.conf','rofi/config.rasi',
          'kitty/kitty.conf','hypr/hyprlock.conf','local/bin/apx-desktop-activation-v1','quickshell/apx/shell.qml']
    device='\n-- Owner-requested touchpad trial'+(SOURCE/'hypr/hyprland.lua').read_text().split('\n-- Owner-requested touchpad trial',1)[1]
    planned=[]
    for name in ['hub','faculdade','hytale','minecraft','steam']:
        env=BASE/name;reg=json.loads((env/'registration.json').read_text())
        assert reg['state'] in ('running','stopped') and reg['role']==('hub' if name=='hub' else 'graphical-base')
        home=env/'home/apx';st=home.stat();owner=(st.st_uid,st.st_gid)
        for rel in rels+fonts:
            target=home/('.'+rel if rel.startswith('local/') else '.config/'+rel)
            data=(SOURCE/rel).read_bytes()
            if rel=='kitty/kitty.conf':
                text=target.read_text()
                text=re.sub(r'(?m)^font_family .*$','font_family Cascadia Mono',text) if re.search(r'(?m)^font_family ',text) else text+'\nfont_family Cascadia Mono\n'
                data=text.encode()
            elif rel in rels: assert target.read_bytes()==(SEED/rel).read_bytes(),str(target)
            else: assert not target.exists(),str(target)
            planned.append((target,data,owner,0o755 if rel.startswith('local/bin/') else 0o600))
        lua=home/'.config/hypr/hyprland.lua'
        assert '-- Owner-requested touchpad trial' not in lua.read_text()
        planned.append((lua,(lua.read_text()+device).encode(),owner,0o600))
        # The top-bar component and its typeface must be preserved exactly.
        assert (home/'.config/quickshell/apx/BarButton.qml').read_bytes()==(SOURCE/'quickshell/apx/BarButton.qml').read_bytes()
    for rel in rels+fonts+['hypr/hyprland.lua']:
        planned.append((SEED/rel,(SOURCE/rel).read_bytes(),(0,0),0o755 if rel.startswith('local/bin/') else 0o644))
    for p in [REPO/'scripts/virtual-lab/apx-lab-runtime.py',Path('/usr/lib/apx/apx-lab-runtime.py')]:
        text=p.read_text();start=text.index('ENVIRONMENT_SHELL_ASSETS = {');end=text.index('\n}',start)+2
        assets=ast.literal_eval(text[start:end].split(' = ',1)[1])
        for rel in rels+fonts+['hypr/hyprland.lua']:assets[rel]=hashlib.sha256((SOURCE/rel).read_bytes()).hexdigest()
        text=text[:start]+'ENVIRONMENT_SHELL_ASSETS = '+json.dumps(assets,indent=4,sort_keys=True)+text[end:]
        planned.append((p,text.encode(),(0,0),0o644))
    runtime=next(d for p,d,_,_ in planned if p==REPO/'scripts/virtual-lab/apx-lab-runtime.py')
    p=REPO/'scripts/physical-pilot/recover-development-quota-v1.sh'
    planned.append((p,re.sub(r'(?m)^readonly RUNTIME_SHA256=.*$','readonly RUNTIME_SHA256='+hashlib.sha256(runtime).hexdigest(),p.read_text()).encode(),(0,0),0o755))
    backup=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-touchpad-font-trial');backup.mkdir(mode=0o700)
    manifest=[]
    for i,(p,data,owner,mode) in enumerate(planned):
        assert not p.is_symlink()
        exists=p.exists();st=p.stat() if exists else None
        entry=dict(target=str(p),existed=exists,uid=st.st_uid if st else owner[0],gid=st.st_gid if st else owner[1],mode=st.st_mode&0o777 if st else mode,after=hashlib.sha256(data).hexdigest())
        if exists:
            saved=backup/str(i);shutil.copy2(p,saved);entry.update(backup=str(saved),before=hashlib.sha256(p.read_bytes()).hexdigest())
        manifest.append(entry)
    (backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
    for (p,data,owner,mode),e in zip(planned,manifest):
        missing=[];parent=p.parent
        while not parent.exists():missing.append(parent);parent=parent.parent
        for parent in reversed(missing):parent.mkdir();os.chown(parent,*owner);os.chmod(parent,0o755 if owner==(0,0) else 0o700)
        p.write_bytes(data);os.chown(p,e['uid'],e['gid']);os.chmod(p,e['mode'])
    print(backup)

if __name__=='__main__':main()
