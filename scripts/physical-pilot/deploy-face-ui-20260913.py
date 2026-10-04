#!/usr/bin/env python3
"""Exact pilot UI/status repair. Does not change PAM, models or credentials."""
import ast, datetime, fcntl, hashlib, json, os, re, shutil, subprocess, tempfile
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
BASE = Path('/var/lib/apx/environments')
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')
SOURCE = REPO/'config/environment-shell-v1'
RELS = ['hypr/hyprlock.conf', 'local/bin/apx-face-auth-state-v1']
COMPARE_BEFORE = '7bea3d1ab78964f059c735e35fa9589f71ab32e411df538b903377cebed494f7'


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
        for rel in RELS:
            target = env/'home/apx'/('.'+rel if rel.startswith('local/') else '.config/'+rel)
            assert target.read_bytes() == (SEED/rel).read_bytes(), str(target)
            planned.append((target, (SOURCE/rel).read_bytes()))
    for rel in RELS: planned.append((SEED/rel, (SOURCE/rel).read_bytes()))
    compare = BASE/'hub/root/usr/lib/howdy/compare.py'
    assert hashlib.sha256(compare.read_bytes()).hexdigest() == COMPARE_BEFORE
    old = compare.read_text()
    # Recover the pinned upstream source by removing the old exact UI patch.
    upstream = old[:old.index('camera_state_path = None')] + old[old.index('def exit(code=None):'):]
    upstream = upstream.replace('\tpublish_camera_frame_state()\n', '')
    with tempfile.TemporaryDirectory(prefix='apx-face-status-') as directory:
        candidate = Path(directory)/'howdy/src/compare.py'; candidate.parent.mkdir(parents=True)
        candidate.write_text(upstream)
        subprocess.run(['patch', '-s', '-d', directory, '-p1', '-i',
                        str(REPO/'config/howdy-v1/howdy-apx/apx-camera-frame-state.patch')], check=True)
        data = candidate.read_bytes(); compile(data, str(compare), 'exec')
        planned.append((compare, data))
    for p in [REPO/'scripts/virtual-lab/apx-lab-runtime.py', Path('/usr/lib/apx/apx-lab-runtime.py')]:
        text = p.read_text(); start = text.index('ENVIRONMENT_SHELL_ASSETS = {'); end = text.index('\n}', start)+2
        assets = ast.literal_eval(text[start:end].split(' = ', 1)[1])
        for rel in RELS: assets[rel] = hashlib.sha256((SOURCE/rel).read_bytes()).hexdigest()
        text = text[:start]+'ENVIRONMENT_SHELL_ASSETS = '+json.dumps(assets, indent=4, sort_keys=True)+text[end:]
        planned.append((p, text.encode()))
    runtime = next(data for p, data in planned if p == REPO/'scripts/virtual-lab/apx-lab-runtime.py')
    p = REPO/'scripts/physical-pilot/recover-development-quota-v1.sh'
    planned.append((p, re.sub(r'(?m)^readonly RUNTIME_SHA256=.*$', 'readonly RUNTIME_SHA256='+hashlib.sha256(runtime).hexdigest(), p.read_text()).encode()))
    for p, data in planned: assert p.is_file() and not p.is_symlink(), str(p)
    backup = Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-face-ui-status')
    backup.mkdir(mode=0o700); manifest = []
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
