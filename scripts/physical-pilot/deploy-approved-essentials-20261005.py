#!/usr/bin/env python3
"""Install owner-approved essentials in stopped, registered APX workloads only.

Uses the established signed offline transaction and per-workload snapshots.
Never stops an active workload, updates repositories, or upgrades Host/Hub.
"""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import urllib.request
import urllib.error

BASE=Path('/var/lib/apx/environments')
NAMES=()
def digest(data):return hashlib.sha256(data).hexdigest()
def run(argv,timeout=120):
    result=subprocess.run(argv,capture_output=True,text=True,timeout=timeout)
    if result.returncode:raise RuntimeError((result.stderr or result.stdout)[-2500:])
    return result.stdout

def install_packages(directory, records):
    packages = directory / 'packages';packages.mkdir(mode=0o755);packages.chmod(0o755)
    urls = {}
    selections = {}
    requested = ['qt5-wayland','otf-font-awesome','rsync','man-pages','gst-plugins-ugly']
    for name in NAMES:
        root = BASE / name / 'root'
        rows = run(['pacman','--root',str(root),'-Sp','--print-format','%n %v %l','--needed',*requested]).splitlines()
        selection = []
        for row in rows:
            package,version,url = row.split(' ',2)
            assert url.startswith('https://fastly.mirror.pkgbuild.com/')
            urls[Path(url).name] = url;selection.append(Path(url).name)
        selections[name]=selection
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
    global NAMES
    parser=argparse.ArgumentParser()
    parser.add_argument('names',nargs='+',choices=['faculdade','hytale','minecraft','steam'])
    args=parser.parse_args();NAMES=tuple(dict.fromkeys(args.names))
    assert os.geteuid()==0
    assert tuple(Path(p).read_text().strip() for p in ['/etc/hostname','/sys/class/dmi/id/product_name','/sys/class/dmi/id/board_name']) == ('apx-host','82JU','LNVNB161216')
    assert 'profile=apx-physical-headless-pilot-v1' in Path('/etc/apx-physical-pilot').read_text().splitlines()
    with open('/run/apx/machine-transition-v1.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        assert not Path('/run/apx/system-power-v1.reserved').exists()
        records={name:json.loads((BASE/name/'registration.json').read_text()) for name in NAMES}
        assert all(r['state']=='stopped' and r['role']=='graphical-base' for r in records.values())
        assert shutil.disk_usage(BASE).free > 2*1024**3
        directory=Path('/var/lib/apx/backups')/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-approved-essentials')
        directory.mkdir(mode=0o700)
        (directory/'records.json').write_text(json.dumps(records,indent=2)+'\n')
        install_packages(directory,records)
        for name in NAMES:
            output=run(['pacman','--root',str(BASE/name/'root'),'-Q','qt5-wayland','otf-font-awesome','rsync','man-pages','gst-plugins-ugly'])
            (directory/(name+'-verified.txt')).write_text(output)
        print(directory,flush=True)
if __name__=='__main__':main()
