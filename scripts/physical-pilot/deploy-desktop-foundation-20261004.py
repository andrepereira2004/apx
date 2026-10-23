#!/usr/bin/env python3
"""Owner-authorized stopped workload desktop additions; Hub is never a target."""
import argparse
import ast
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import urllib.request
import urllib.error

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / 'config/environment-shell-v1'
SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')
BASE = Path('/var/lib/apx/environments')
NAMES = ('faculdade', 'hytale', 'minecraft', 'steam')
ASSETS = ('local/bin/apx-settings', 'local/bin/apx-desktop-preferences-v1',
          'local/bin/apx-clipboard-menu-v1', 'local/bin/apx-desktop-activation-v1', 'local/share/applications/apx-settings.desktop')

def digest(data): return hashlib.sha256(data).hexdigest()

def run(argv, timeout=120):
    result = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    if result.returncode: raise RuntimeError((result.stderr or result.stdout)[-2500:])
    return result.stdout

def patch_shell(text):
    before = 'return environmentModuleCatalog.slice(0, 14).map(function(item) { return item.key }).concat(["shortcuts"])'
    after = 'return environmentModuleCatalog.filter(function(item) { return item.key !== "office" && item.key !== "development" }).map(function(item) { return item.key })'
    assert text.count(before) == 1; text = text.replace(before, after, 1)
    assert text.count('    property string powerAction: ""') == 1
    text = text.replace('    property string powerAction: ""', '    property string powerAction: ""\n    property bool idleSuspendRequested: false', 1)
    source = (SOURCE / 'quickshell/apx/shell.qml').read_text()
    methods = source.split('        function openShortcuts(): void {', 1)[1].split('        function openTerminal()', 1)[0]
    marker = '        function openTerminal()'
    assert text.count(marker) == 1
    text = text.replace(marker, '        function openShortcuts(): void {' + methods + marker, 1)
    needle = 'if (root.powerAction !== "suspend") root.confirmPower()'
    assert text.count(needle) == 1
    text = text.replace(needle, 'if (root.powerAction !== "suspend" || root.idleSuspendRequested) root.confirmPower()\n                        root.idleSuspendRequested = false', 1)
    text = text.replace('root.powerMessage = "AÇÃO BLOQUEADA :: "', 'root.idleSuspendRequested = false\n                        root.powerMessage = "AÇÃO BLOQUEADA :: "', 1)
    text = text.replace('root.powerMessage = "Não foi possível consultar o Host."', 'root.idleSuspendRequested = false\n                    root.powerMessage = "Não foi possível consultar o Host."', 1)
    text = text.replace('if (root.powerMessage === "A verificar o Host...") root.powerMessage = "O Host recusou a ação."',
                        'root.idleSuspendRequested = false\n                if (root.powerMessage === "A verificar o Host...") root.powerMessage = "O Host recusou a ação."', 1)
    text = text.replace('additions: "+ Brave · PDF · MPV"', 'additions: "+ PDF · MPV · impressão"').replace('description: "Tudo do Intermédio, Office, periféricos e programação."', 'description: "Tudo do Intermédio, Office e programação."').replace('additions: "+ LibreOffice · dev · impressão"', 'additions: "+ LibreOffice · programação"')
    return text

def patch_launcher(text):
    assert text.count('export LOGNAME=apx\n') == 1
    snippet = (SOURCE / 'local/bin/apx-shell-v1').read_text().split('# Locale choices apply',1)[1].split('config=/home',1)[0]
    text = text.replace('export LOGNAME=apx\n','export LOGNAME=apx\n\n# Locale choices apply'+snippet,1)
    marker = 'while true; do\n'; assert text.count(marker) == 1
    source = (SOURCE / 'local/bin/apx-shell-v1').read_text()
    addition = '# User-selected startup applications' + source.split('# User-selected startup applications',1)[1].split(marker,1)[0]
    return text.replace(marker,addition+marker,1)

def configuration_plan():
    plan = {}
    for target in [SEED] + [BASE / name / 'home/apx/.config' for name in NAMES]:
        # Workload bin/share live under .local, seed stores both kinds in one tree.
        if target == SEED:
            assets_root = target
        else:
            assets_root = target.parent / '.local'
        for relative in ASSETS:
            destination = target / relative if target == SEED else assets_root / Path(relative).relative_to('local')
            plan[destination] = (SOURCE / relative).read_bytes()
        qml = target / 'quickshell/apx/shell.qml'
        plan[qml] = patch_shell(qml.read_text()).encode()
        hypr = target / 'hypr/hyprland.lua'
        loader = '\n-- Environment-local choices edited by APX Settings.' + (SOURCE / 'hypr/hyprland.lua').read_text().split('\n-- Environment-local choices edited by APX Settings.',1)[1]
        assert 'apx-desktop-preferences.lua' not in hypr.read_text()
        plan[hypr] = hypr.read_bytes() + loader.encode()
        launcher = target / 'local/bin/apx-shell-v1' if target == SEED else assets_root / 'bin/apx-shell-v1'
        plan[launcher] = patch_launcher(launcher.read_text()).encode()
    hub_qml = BASE / 'hub/home/apx/.config/quickshell/apx/shell.qml'
    hub_text = hub_qml.read_text()
    before = 'return environmentModuleCatalog.slice(0, 14).map(function(item) { return item.key }).concat(["shortcuts"])'
    after = 'return environmentModuleCatalog.filter(function(item) { return item.key !== "office" && item.key !== "development" }).map(function(item) { return item.key })'
    assert hub_text.count(before) == 1
    hub_text = hub_text.replace(before, after, 1).replace('additions: "+ Brave · PDF · MPV"', 'additions: "+ PDF · MPV · impressão"').replace('description: "Tudo do Intermédio, Office, periféricos e programação."', 'description: "Tudo do Intermédio, Office e programação."').replace('additions: "+ LibreOffice · dev · impressão"', 'additions: "+ LibreOffice · programação"')
    plan[hub_qml] = hub_text.encode()
    plan[Path('/usr/lib/apx/apx_environment_features.py')] = (REPO / 'src/apx_environment_features.py').read_bytes()
    runtime = Path('/usr/lib/apx/apx-lab-runtime.py'); text = runtime.read_text()
    source = (REPO / 'scripts/virtual-lab/apx-lab-runtime.py').read_text()
    # Preserve the installed runtime's other accepted pilot differences.
    effects = '"stop", "purge-snapshots", "purge-archives", "purge-backups", "remove-home",'
    assert text.count(effects) == 1
    text = text.replace(effects, '"stop", "purge-update-rollbacks", "purge-snapshots", "purge-archives", "purge-backups", "remove-home",',1)
    for start, end in [('def destroy(', '\ndef delete_subvolume_tree('), ('def environment_update_rollbacks(', '\ndef _remove_exact_copy('), ('def purge_environment_backups(', '\ndef snapshot(')]:
        addition = source[source.index(start):source.index(end,source.index(start))]
        if start in text:
            begin = text.index(start); finish = text.index(end,begin); text = text[:begin] + addition + text[finish:]
        else:
            index = text.index(end); text = text[:index] + '\n\n' + addition + text[index:]
    start = text.index('ENVIRONMENT_SHELL_ASSETS = {'); end = text.index('\n}', start)+2
    assets = ast.literal_eval(text[start:end].split('=',1)[1].strip())
    for relative in (*ASSETS, 'quickshell/apx/shell.qml', 'hypr/hyprland.lua', 'local/bin/apx-shell-v1'):
        assets[relative] = digest(plan[SEED / relative])
    block = 'ENVIRONMENT_SHELL_ASSETS = {\n' + ''.join(f'    "{key}": "{value}",\n' for key,value in assets.items()) + '}'
    text = text[:start] + block + text[end:]
    compile(text,str(runtime),'exec'); plan[runtime] = text.encode()
    return plan

def write_plan(plan, backup):
    entries = []
    for index,(target,content) in enumerate(plan.items()):
        assert not target.is_symlink()
        info = target.stat() if target.exists() else target.parent.stat()
        previous = target.read_bytes() if target.exists() else None
        saved = backup / str(index)
        if previous is not None: shutil.copy2(target,saved)
        mode = info.st_mode & 0o777 if previous is not None else (0o755 if '/bin/' in str(target) else 0o644)
        entries.append(dict(target=str(target),backup=str(saved) if previous is not None else None,
                            before=digest(previous) if previous is not None else None,after=digest(content),uid=info.st_uid,gid=info.st_gid,mode=mode))
    (backup/'manifest.json').write_text(json.dumps(entries,indent=2)+'\n')
    for (target,content),entry in zip(plan.items(),entries):
        fd,temporary = tempfile.mkstemp(prefix='.apx-foundation-',dir=target.parent)
        with os.fdopen(fd,'wb') as stream:stream.write(content);stream.flush();os.fsync(stream.fileno())
        os.chown(temporary,entry['uid'],entry['gid']);os.chmod(temporary,entry['mode']);os.replace(temporary,target)
        assert digest(target.read_bytes()) == entry['after']


def install_packages(directory, records):
    packages = directory / 'packages';packages.mkdir(mode=0o755);packages.chmod(0o755)
    urls = {}
    selections = {}
    requested = ['noto-fonts-emoji','ttf-liberation','cliphist','cups','sane','sane-airscan','simple-scan','system-config-printer']
    for name in NAMES:
        root = BASE / name / 'root'
        rows = run(['pacman','--root',str(root),'-Sp','--print-format','%n %v %l','--needed',*requested]).splitlines()
        selection = []
        for row in rows:
            package,version,url = row.split(' ',2)
            assert url.startswith('https://fastly.mirror.pkgbuild.com/')
            urls[Path(url).name] = url;selection.append(Path(url).name)
        version = run(['pacman','--root',str(root),'-Q','pipewire']).split()[1]
        filename = f'pipewire-alsa-{version}-x86_64.pkg.tar.zst'
        urls[filename] = 'https://archive.archlinux.org/packages/p/pipewire-alsa/' + filename.replace(':','%3A')
        selection.append(filename);selections[name]=selection
    for filename,url in urls.items():
        for suffix in ['', '.sig']:
            path=packages/(filename+suffix)
            try:
                with urllib.request.urlopen(url+suffix,timeout=30) as response:path.write_bytes(response.read())
            except urllib.error.HTTPError as error:
                if error.code != 404: raise
                # Mirrors retire older versions; retrieve the exact signed package from Arch's archive.
                package = filename.rsplit('-',3)[0]
                archive = 'https://archive.archlinux.org/packages/' + package[0] + '/' + package + '/' + filename.replace(':','%3A') + suffix
                with urllib.request.urlopen(archive,timeout=30) as response:path.write_bytes(response.read())
            path.chmod(0o644)
        run(['pacman-key','--verify',str(packages/(filename+'.sig')),str(packages/filename)])
        print(filename + ': signature verified',flush=True)
    (directory/'packages.json').write_text(json.dumps({name:[{'file':file,'sha256':digest((packages/file).read_bytes())} for file in values] for name,values in selections.items()},indent=2)+'\n')
    (directory/'packages.json').chmod(0o644)
    for name in NAMES:
        record = json.loads((BASE/name/'registration.json').read_text())
        assert record == records[name] and record['state']=='stopped'
        # Preview the entire offline transaction before taking a snapshot or writing packages.
        run(['pacman','--root',str(BASE/name/'root'),'-Up','--print-format','%n %v',*[str(packages/file) for file in selections[name]]])
    for name in NAMES:
        stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        snapshot=Path('/var/lib/apx/snapshots')/(name+'-'+records[name]['generation']+'-'+stamp)
        snapshot.mkdir(mode=0o700)
        for part in ['root','home']:
            run(['btrfs','subvolume','snapshot','-r',str(BASE/name/part),str(snapshot/part)])
        command=['systemd-nspawn','--quiet','--directory='+str(BASE/name/'root'),'--private-users=pick','--private-users-ownership=chown',
                 '--private-network','--register=no','--bind-ro='+str(packages)+':/run/apx-desktop-packages',
                 '/usr/bin/pacman','-U','--needed','--noconfirm',*['/run/apx-desktop-packages/'+file for file in selections[name]]]
        output=run(command,timeout=600)
        (directory/(name+'-packages.log')).write_text(output)
        print(name+': signed package transaction completed',flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--packages',action='store_true');args=parser.parse_args()
    assert os.geteuid()==0
    assert tuple(Path(p).read_text().strip() for p in ['/etc/hostname','/sys/class/dmi/id/product_name','/sys/class/dmi/id/board_name']) == ('apx-host','82JU','LNVNB161216')
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    with open('/run/apx/machine-transition-v1.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        assert not Path('/run/apx/system-power-v1.reserved').exists()
        records={name:json.loads((BASE/name/'registration.json').read_text()) for name in NAMES}
        assert all(record['state']=='stopped' and record['role']=='graphical-base' for record in records.values())
        assert shutil.disk_usage(BASE).free > 2*1024**3
        plan=configuration_plan()
        for target,content in plan.items():
            assert target.parent.is_dir(),target
            if target.suffix=='.py' or target.name in ['apx-settings','apx-desktop-preferences-v1','apx-clipboard-menu-v1']:compile(content,str(target),'exec')
        directory=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-desktop-foundation')
        directory.mkdir(mode=0o700)
        (directory/'records.json').write_text(json.dumps(records,indent=2))
        if args.packages:install_packages(directory,records)
        write_plan(plan,directory)
        print(directory)

if __name__=='__main__':main()
