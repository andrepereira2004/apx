#!/usr/bin/env python3
"""Owner-requested bounded cleanup on the fixed disposable APX pilot.

Remove unused legacy packages and optional executables bundled with needed
libraries. Pacman NoExtract records the deliberately omitted components.
Never force dependencies, sweep arbitrary orphans, or remove personal data.
"""
from pathlib import Path
import datetime
import fcntl
import fnmatch
import json
import os
import shutil
import subprocess
import sys

BASE = Path('/var/lib/apx/environments')
REMOVE = {'waybar', 'gpsd', 'uwsm', 'fuzzel'}
# Narrow leftover dependencies of the already removed scanner/document/search apps.
ORPHANS = {'djvulibre', 'exempi', 'gnome-desktop', 'gsfonts', 'gspell',
           'libgxps', 'libhandy', 'libspectre', 'libsynctex', 'python-pexpect'}
COMPONENTS = {
    'v4l-utils': ['*qv4l2*', '*qvidcap*'],
    'avahi': ['usr/bin/avahi-discover*', 'usr/bin/bshell', 'usr/bin/bssh',
              'usr/bin/bvnc', 'usr/share/applications/avahi-discover.desktop',
              'usr/share/applications/bssh.desktop', 'usr/share/applications/bvnc.desktop',
              'usr/share/avahi/interfaces/avahi-discover.ui',
              'usr/share/man/man1/avahi-discover.*', 'usr/share/man/man1/bshell.*',
              'usr/share/man/man1/bssh.*', 'usr/share/man/man1/bvnc.*'],
    'hwloc': ['usr/bin/lstopo*', 'usr/share/applications/lstopo.desktop',
              'usr/share/man/man1/lstopo*'],
    'libxfce4ui': ['usr/bin/xfce4-about', 'usr/share/applications/xfce4-about.desktop'],
    'cmake': ['usr/bin/cmake-gui', 'usr/share/applications/cmake-gui.desktop',
              'usr/share/man/man1/cmake-gui.*'],
    'rofi': ['usr/bin/rofi-theme-selector', 'usr/share/applications/rofi-theme-selector.desktop',
             'usr/share/man/man1/rofi-theme-selector.*'],
}


def metadata(root):
    result = {}
    for item in (root / 'var/lib/pacman/local').glob('*/desc'):
        data = item.read_text()
        result[data.split('%NAME%\n')[1].split('\n')[0]] = item.parent
    return result


def main():
    assert Path('/etc/hostname').read_text().strip() == 'apx-host'
    assert Path('/sys/class/dmi/id/product_name').read_text().strip() == '82JU'
    assert not sys.argv[1:] or (sys.argv[1] == '--apply' and len(sys.argv) in (2, 3))
    with open('/run/apx/machine-transition-v1.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        active = json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text())
        plans = []
        for name in ['hub', 'faculdade', 'hytale', 'minecraft', 'steam']:
            directory = BASE / name
            root = directory / 'root'
            home = directory / 'home/apx'
            assert (home / '.config/quickshell/apx/shell.qml').is_file()
            assert not (root / 'var/lib/pacman/db.lck').exists()
            if name == active['name']:
                assert int((Path('/proc') / str(active['pid']) / 'uid_map').read_text().split()[1]) == root.stat().st_uid
                prefix = ['nsenter', '-t', str(active['pid']), '-m', '-U', '-p', '-n', '--']
            else:
                assert json.loads((directory / 'registration.json').read_text())['state'] == 'stopped'
                prefix = ['systemd-nspawn', '--quiet', '--register=no', '--settings=no',
                          '--link-journal=no', '--resolv-conf=off', '--private-network',
                          '--directory=' + str(root), '--private-users=' + str(root.stat().st_uid) + ':65536',
                          '--private-users-ownership=off', '--bind=' + str(directory / 'home') + ':/home:idmap', '--']
            packages = metadata(root)
            orphan_check = subprocess.run(prefix + ['/usr/bin/pacman', '-Qdtq'], text=True, capture_output=True, timeout=30)
            assert orphan_check.returncode in (0, 1)
            targets = sorted((REMOVE & packages.keys()) | (ORPHANS & set(orphan_check.stdout.split())))
            if targets:
                subprocess.run(prefix + ['/usr/bin/pacman', '-R', '--print', '--', *targets],
                               capture_output=True, text=True, timeout=30, check=True)
            components = []
            for package, patterns in COMPONENTS.items():
                if package not in packages:
                    continue
                for rel in (packages[package] / 'files').read_text().splitlines():
                    if rel.startswith('usr/') and not rel.endswith('/') and any(fnmatch.fnmatchcase(rel, p) for p in patterns):
                        path = root / rel
                        assert '..' not in Path(rel).parts
                        if path.exists() or path.is_symlink():
                            assert not path.is_dir()
                            components.append(rel)
            plans.append(dict(name=name, targets=targets, components=sorted(components), prefix=prefix))
        print(json.dumps([{k: v for k, v in p.items() if k != 'prefix'} for p in plans], indent=2), flush=True)
        if not sys.argv[1:] or sys.argv[1] != '--apply':
            return
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        backup = Path(sys.argv[2]) if len(sys.argv) == 3 else Path('/var/lib/apx/backups') / (stamp + '-support-cleanup')
        assert backup.parent == Path('/var/lib/apx/backups') and backup.name.endswith('-support-cleanup')
        backup.mkdir(mode=0o700, exist_ok=len(sys.argv) == 3)
        (backup / ('resume-plan.json' if len(sys.argv) == 3 else 'plan.json')).write_text(json.dumps(plans, indent=2))
        # Preserve exact package roots before every transaction, including Hub.
        for plan in plans:
            name = plan['name']
            if len(sys.argv) != 3:
                subprocess.run(['btrfs', 'subvolume', 'snapshot', '-r', str(BASE / name / 'root'),
                                str(backup / (name + '-root'))], check=True, capture_output=True)
            else:
                assert (backup / (name + '-root')).is_dir()
        for plan in plans:
            name, prefix = plan['name'], plan['prefix']
            root = BASE / name / 'root'
            def run(label, args):
                result = subprocess.run(prefix + args, capture_output=True, text=True, timeout=120)
                (backup / (name + '-' + label + '.log')).write_text(result.stdout + result.stderr)
                result.check_returncode()
            if plan['targets']:
                run('remove', ['/usr/bin/pacman', '-R', '--noconfirm', '--', *plan['targets']])
            config = root / 'etc/pacman.conf'
            include = root / 'etc/pacman.d/apx-minimal-tools.conf'
            assert not include.is_symlink()
            assert not config.is_symlink()
            text = config.read_text()
            assert text.count('[options]') == 1
            patterns = sorted({p for values in COMPONENTS.values() for p in values})
            policy = '# Owner-selected omission of optional executables; runtime libraries remain.\n'
            policy += '\n'.join('NoExtract = ' + pattern for pattern in patterns) + '\n'
            if include.exists():
                assert include.read_text() == policy
            include.write_text(policy)
            os.chown(include, root.stat().st_uid, root.stat().st_gid)
            os.chmod(include, 0o644)
            directive = 'Include = /etc/pacman.d/apx-minimal-tools.conf'
            if directive not in text.splitlines():
                config.write_text(text.replace('[options]', '[options]\n' + directive, 1))
            for rel in plan['components']:
                (root / rel).unlink()
            # Checking required files honors NoExtract; missing optional tools are intentional.
            checked = sorted(metadata(root).keys() & COMPONENTS.keys())
            run('component-integrity', ['/usr/bin/pacman', '-Qk', *checked])
            run('db-check', ['/usr/bin/pacman', '-Dk'])
            run('desktop-db', ['/usr/bin/update-desktop-database', '/usr/share/applications'])
            run('catalog', ['/usr/bin/runuser', '-u', 'apx', '--', '/usr/bin/env', 'HOME=/home/apx',
                            '/home/apx/.local/bin/apx-application-catalog-v1'])
            assert not any((root / rel).exists() for rel in plan['components'])
            for executable in ['/usr/bin/rofi', '/usr/bin/quickshell', '/usr/bin/kitty']:
                if executable == '/usr/bin/rofi' and 'rofi' not in metadata(root):
                    continue  # Legacy Hub lacks Rofi before this cleanup too.
                run('executable-' + Path(executable).name, ['/usr/bin/test', '-x', executable])
            if 'v4l-utils' in metadata(root):
                assert (root / 'usr/lib/libv4l2.so.0').exists()
            print(name + ': package/component removal and integrity checks passed', flush=True)
        (backup / 'complete.json').write_text(json.dumps({'completed': [p['name'] for p in plans]}, indent=2))
        print('Backup/evidence: ' + str(backup), flush=True)


if __name__ == '__main__':
    main()
