#!/usr/bin/env python3
"""Bounded owner-requested identity/menu repair; preserves PAM and credentials."""
import ast, datetime, fcntl, hashlib, json, os, re, shutil
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
BASE = Path('/var/lib/apx/environments')
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')
SOURCE = REPO/'config/environment-shell-v1'
RELS = ['quickshell/apx/shell.qml', 'local/bin/apx-shell-v1',
        'local/bin/apx-laptop-action-v1', 'local/bin/apx-face-auth-state-v1',
        'hypr/hyprlock.conf']

def main():
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    assert Path('/sys/class/dmi/id/board_name').read_text().strip() == 'LNVNB161216'
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    lock = open('/run/apx/machine-transition-v1.lock', 'a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    assert not Path('/run/apx/system-power-v1.reserved').exists()
    planned = []
    for name in ['hub', 'faculdade', 'hytale', 'minecraft', 'steam']:
        env = BASE/name
        reg = json.loads((env/'registration.json').read_text())
        assert reg['state'] in ('running', 'stopped')
        assert reg['role'] == ('hub' if name == 'hub' else 'graphical-base')
        passwd = env/'root/etc/passwd'
        lines = passwd.read_text().splitlines()
        alias = 'home:x:1000:1000:Home:/home/apx:/usr/bin/bash'
        uid_names = [line.split(':')[0] for line in lines if line.split(':')[2] == '1000']
        assert set(uid_names) in ({'apx'}, {'apx', 'home'})
        if 'home' in uid_names:
            assert lines.count(alias) == 1
            planned.append((passwd, ('\n'.join(line for line in lines if line != alias)+'\n').encode()))
        for rel in RELS:
            target = env/'home/apx'/('.'+rel if rel.startswith('local/') else '.config/'+rel)
            # All copies must match the admitted predecessor before replacement.
            assert target.read_bytes() == (SEED/rel).read_bytes(), str(target)
            planned.append((target, (SOURCE/rel).read_bytes()))
    for rel in RELS:
        planned.append((SEED/rel, (SOURCE/rel).read_bytes()))
    for p in [REPO/'scripts/virtual-lab/apx-lab-runtime.py', Path('/usr/lib/apx/apx-lab-runtime.py')]:
        text = p.read_text(); start = text.index('ENVIRONMENT_SHELL_ASSETS = {'); end = text.index('\n}', start)+2
        assets = ast.literal_eval(text[start:end].split(' = ', 1)[1])
        for rel in RELS: assets[rel] = hashlib.sha256((SOURCE/rel).read_bytes()).hexdigest()
        text = text[:start]+'ENVIRONMENT_SHELL_ASSETS = '+json.dumps(assets, indent=4, sort_keys=True)+text[end:]
        planned.append((p, text.encode()))
    runtime = next(data for p, data in planned if p == REPO/'scripts/virtual-lab/apx-lab-runtime.py')
    p = REPO/'scripts/physical-pilot/recover-development-quota-v1.sh'
    planned.append((p, re.sub(r'(?m)^readonly RUNTIME_SHA256=.*$', 'readonly RUNTIME_SHA256='+hashlib.sha256(runtime).hexdigest(), p.read_text()).encode()))
    # Narrowly remove only the known duplicate in the installed future release builder.
    p = Path('/usr/lib/apx/apx_hyprland_release_promote.py')
    duplicate = '    _append_unique(TARGET_ROOT / "etc/passwd", "home:", "home:x:1000:1000:Home:/home/apx:/usr/bin/bash")\n'
    if duplicate in p.read_text(): planned.append((p, p.read_text().replace(duplicate, '').encode()))
    for p, data in planned:
        assert p.is_file() and not p.is_symlink(), str(p)
    backup = Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-lock-menu-repair')
    backup.mkdir(mode=0o700); manifest = []
    # Save every predecessor before any live write. Preserve inodes for existing mounts.
    for i, (p, data) in enumerate(planned):
        st = p.stat(); saved = backup/str(i); shutil.copy2(p, saved)
        manifest.append(dict(target=str(p), backup=str(saved), uid=st.st_uid, gid=st.st_gid,
                             mode=st.st_mode & 0o777, before=hashlib.sha256(p.read_bytes()).hexdigest(),
                             after=hashlib.sha256(data).hexdigest()))
    (backup/'manifest.json').write_text(json.dumps(manifest, indent=2))
    for (p, data), entry in zip(planned, manifest):
        p.write_bytes(data); os.chown(p, entry['uid'], entry['gid']); os.chmod(p, entry['mode'])
        assert hashlib.sha256(p.read_bytes()).hexdigest() == entry['after']
    print(backup)

if __name__ == '__main__': main()
