#!/usr/bin/env python3
"""Owner-requested file-manager repair on the identity-matched physical pilot."""
import ast
import configparser
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

REPO = Path(__file__).resolve().parents[2]
BASE = Path('/var/lib/apx/environments')
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')
assert Path('/etc/hostname').read_text().strip() == 'apx-host'
assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
assert Path('/sys/class/dmi/id/board_name').read_text().strip() == 'LNVNB161216'
assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
lock = open('/run/apx/machine-transition-v1.lock', 'a')
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
assert not Path('/run/apx/system-power-v1.reserved').exists()
names = ['faculdade', 'hytale', 'minecraft', 'steam']
for name in ['hub'] + names:
    record = json.loads((BASE/name/'registration.json').read_text())
    assert record['name'] == name
    assert record['state'] == ('running' if name == 'hub' else 'stopped')
    assert record['role'] == ('hub' if name == 'hub' else 'graphical-base')
    assert (BASE/name/'root/usr/bin/thunar').is_file()
backup = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-file-manager')
backup.mkdir(mode=0o700)
print(backup, flush=True)
manifest = []
def write(target, content, owner=None, mode=0o600):
    assert not target.is_symlink()
    existed = target.exists()
    st = target.stat() if existed else None
    entry = dict(target=str(target), existed=existed, uid=st.st_uid if st else owner[0], gid=st.st_gid if st else owner[1], mode=st.st_mode & 0o777 if st else mode)
    if existed:
        saved = backup / str(len(manifest)); shutil.copy2(target, saved)
        entry['backup'] = str(saved)
    manifest.append(entry)
    (backup/'manifest.json').write_text(json.dumps(manifest, indent=2))
    missing = []; parent = target.parent
    while not parent.exists(): missing.append(parent); parent = parent.parent
    for parent in reversed(missing):
        parent.mkdir(mode=0o700 if owner and owner != (0,0) else 0o755)
        os.chown(parent, *(owner or (entry['uid'],entry['gid'])))
    target.write_bytes(content)
    os.chown(target, entry['uid'], entry['gid']); os.chmod(target, entry['mode'])
    entry['after'] = hashlib.sha256(content).hexdigest()

source = REPO/'config/environment-shell-v1'
helper = (source/'local/bin/apx-laptop-action-v1').read_text()
files_fn = helper[helper.index('def files()'):helper.index('def screenshot()')]
assets = ['local/bin/apx-laptop-action-v1','quickshell/apx/shell.qml','gtk-3.0/settings.ini','gtk-3.0/gtk.css','gtk-3.0/bookmarks','xfce4/xfconf/xfce-perchannel-xml/thunar.xml','mimeapps.list']
for name in ['hub'] + names:
    home = BASE/name/'home/apx'; st = home.stat(); owner = (st.st_uid,st.st_gid)
    path = home/'.local/bin/apx-laptop-action-v1'
    text = path.read_text()
    if 'def files()' in text: text = text[:text.index('def files()')] + files_fn + text[text.index('def screenshot()'):]
    else:
        text = text.replace('def screenshot()', files_fn + 'def screenshot()', 1)
        text = text.replace('actions = {', 'actions = {\n        "files": files,', 1)
    write(path, text.encode(), owner); os.chmod(path, 0o700)
    path = home/'.config/quickshell/apx/shell.qml'; text = path.read_text()
    assert 'function openFiles(): void {' in text
    text = text.replace('function openFiles(): void {\n', 'function openFiles(): void {\n            if (root.isHub) return\n', 1)
    text = text.replace('Process { id: environmentFilesProcess; command: ["/usr/bin/thunar"] }', 'Process { id: environmentFilesProcess; command: ["/home/apx/.local/bin/apx-laptop-action-v1", "files"] }')
    write(path, text.encode(), owner)
    if name == 'hub': continue
    for rel in ['gtk-3.0/settings.ini','gtk-3.0/gtk.css','gtk-3.0/bookmarks','xfce4/xfconf/xfce-perchannel-xml/thunar.xml','mimeapps.list']:
        path = home/'.config'/rel
        if path.exists():
            if rel in ('gtk-3.0/settings.ini','mimeapps.list'):
                cfg = configparser.ConfigParser(interpolation=None);cfg.optionxform=str
                cfg.read(path); cfg.read(source/rel)
                import io
                stream=io.StringIO();cfg.write(stream, space_around_delimiters=False); content=stream.getvalue().encode()
            elif rel == 'gtk-3.0/gtk.css': content = path.read_bytes()+b'\n'+(source/rel).read_bytes()
            elif rel == 'gtk-3.0/bookmarks':
                old=path.read_text();content=(old+'\n'+''.join(line+'\n' for line in (source/rel).read_text().splitlines() if line.split()[0] not in old)).encode()
            else: continue  # Keep any existing personal Thunar preferences.
        else: content=(source/rel).read_bytes()
        write(path,content,owner)
    # xdg-user-dirs-update will populate any missing XDG configuration on launch.
    for folder in ['Downloads','Documents','Pictures','Videos','Music','Desktop','Templates','Public']:
        path=home/folder
        if not path.exists(): path.mkdir(mode=0o700);os.chown(path,*owner)
for rel in assets:
    write(SEED/rel,(source/rel).read_bytes(),(0,0),0o755 if rel.startswith('local/bin/') else 0o644)
runtime=Path('/usr/lib/apx/apx-lab-runtime.py');text=runtime.read_text()
for rel in assets:
    digest=hashlib.sha256((source/rel).read_bytes()).hexdigest()
    pattern=r'("'+re.escape(rel)+r'": ")[a-f0-9]+'
    if re.search(pattern,text):text=re.sub(pattern,lambda m:m[1]+digest,text)
    else:text=text.replace('ENVIRONMENT_SHELL_ASSETS = {','ENVIRONMENT_SHELL_ASSETS = {\n    "'+rel+'": "'+digest+'",')
write(runtime,text.encode(),(0,0))
write(Path('/usr/lib/apx/apx_environment_features.py'),(REPO/'src/apx_environment_features.py').read_bytes(),(0,0),0o644)
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
package=REPO/'tmp/file-manager/papirus.pkg.tar.zst'
shutil.copy2(package,backup/'papirus.pkg.tar.zst');shutil.copy2(str(package)+'.sig',backup/'papirus.pkg.tar.zst.sig')
hubpkg=BASE/'hub/root/var/cache/pacman/pkg/thunar-4.20.9-1-x86_64.pkg.tar.zst'
shutil.copy2(hubpkg,backup/hubpkg.name)
for name in names:
    command=['systemd-nspawn','--quiet','--register=no','--settings=no','--private-network','--private-users=pick','--private-users-ownership=chown','--directory='+str(BASE/name/'root'),'--bind-ro='+str(backup/'papirus.pkg.tar.zst')+':/run/papirus.pkg.tar.zst:idmap','--bind-ro='+str(backup/'papirus.pkg.tar.zst.sig')+':/run/papirus.pkg.tar.zst.sig:idmap','/usr/bin/pacman','-U','--needed','--noconfirm','/run/papirus.pkg.tar.zst']
    with (backup/(name+'-package.log')).open('w') as log:
        subprocess.run(command,check=True,stdout=log,stderr=subprocess.STDOUT)
    print(name+': Papirus installed',flush=True)
subprocess.run(['systemd-run','-M','apx-hub','--pipe','--wait','--quiet','/usr/bin/pacman','-R','--noconfirm','thunar'],check=True)
print('Hub: Thunar removed; deployment complete',flush=True)
